import json
import asyncio
import hashlib
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from decouple import config
from .models import Message
from .online_tracker import OnlineUserTracker
from .redis_manager import get_async_redis_client


class HangoutConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = "hangout_main"
        self.redis_client = None
        self.redis_pubsub = None
        self.redis_listener_task = None
        self.heartbeat_task = None
        self.highlight_user_id = config("DISCORD_USER_ID", default="")
        self.online_tracker = OnlineUserTracker()
        self.user_id = None

        self.banned_words = config(
            "BANNED_NICKNAMES",
            default="",
            cast=lambda nicknames: [
                nickname.lower() for nickname in nicknames.split(",")
            ] if nicknames else []
        )

    def _get_real_client_ip(self):
        headers = dict(self.scope.get('headers', []))
        
        # Get X-Forwarded-For header
        x_forwarded_for = headers.get(b'x-forwarded-for', b'').decode('utf-8')
        
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
            return ip
        
        if self.scope.get('client'):
            return self.scope['client'][0]
        
        return 'unknown'

    async def connect(self):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        self.redis_client = get_async_redis_client()
        
        # get real client IP (not heroku's internal router ip)
        self.user_id = self._get_real_client_ip()
        
        print(f"[Hangout] User connected: {self.user_id}")
        
        await self.online_tracker.mark_user_online(self.user_id, self.redis_client)
        
        self.redis_listener_task = asyncio.create_task(self.listen_for_discord_messages())
        self.heartbeat_task = asyncio.create_task(self.online_heartbeat())

        recent_messages = await self.get_recent_messages()
        for message in recent_messages:
            await self.send(text_data=json.dumps({
                "type": "message",
                "nickname": message["nickname"],
                "content": message["content"],
                "timestamp": message["timestamp"],
                "from_discord": message.get("is_from_discord", False),
                "is_highlighted": str(message.get("discord_user_id", "")) == self.highlight_user_id
            }))

        online_count = await self.online_tracker.get_online_count(self.redis_client)
        
        await self.send(text_data=json.dumps({
            "type": "online_count",
            "count": online_count
        }))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "online_count_update",
                "count": online_count
            }
        )

        await self.send(text_data=json.dumps({
            "type": "system",
            "message": "connected to hangout"
        }))

    async def disconnect(self, close_code):
        print(f"[Hangout] User disconnected: {self.user_id}")
        
        if self.redis_listener_task:
            self.redis_listener_task.cancel()
            try:
                await self.redis_listener_task
            except asyncio.CancelledError:
                pass
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_pubsub:
            try:
                await self.redis_pubsub.unsubscribe("discord_to_web")
                await self.redis_pubsub.close()
            except Exception as e:
                print(f"Error closing pubsub: {e}")
        
        if self.user_id and self.redis_client:
            await self.online_tracker.mark_user_offline(self.user_id, self.redis_client)
            
            online_count = await self.online_tracker.get_online_count(self.redis_client)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "online_count_update",
                    "count": online_count
                }
            )
        
        self.redis_client = None

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "heartbeat":
                await self.online_tracker.heartbeat(self.user_id, self.redis_client)
                return

            if message_type == "message":
                nickname = data.get("nickname", "anonymous")[:50]
                content = data.get("content", "").strip()

                if not content:
                    return

                max_length = 280
                if len(content) > max_length:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": f"message too long (max {max_length} characters)"
                    }))
                    return

                name_lower = nickname.lower()

                if any(banned_word in name_lower for banned_word in self.banned_words):
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "this nickname is not allowed"
                    }))
                    return

                # Get real IP for message logging
                ip_address = self._get_real_client_ip()

                message = await self.save_message(
                    nickname=nickname,
                    content=content,
                    ip_address=ip_address,
                    is_from_discord=False
                )

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "message_handler",
                        "nickname": nickname,
                        "content": content,
                        "timestamp": message["timestamp"],
                        "is_highlighted": False,
                        "from_discord": False
                    }
                )

                await self.send_to_discord_via_redis(nickname, content)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "invalid message format"
            }))
        except Exception as error:
            print(f"Error in receive: {error}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "an error occurred"
            }))

    async def message_handler(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'nickname': event['nickname'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_highlighted': event.get('is_highlighted', False),
            'from_discord': event.get('from_discord', False)
        }))

    async def online_count_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'count': event['count']
        }))

    async def online_heartbeat(self):
        try:
            while True:
                await asyncio.sleep(30)
                if self.user_id and self.redis_client:
                    await self.online_tracker.heartbeat(self.user_id, self.redis_client)
        except asyncio.CancelledError:
            print(f"[Hangout] Heartbeat task cancelled for {self.user_id}")
        except Exception as error:
            print(f"Error in online heartbeat: {error}")

    async def listen_for_discord_messages(self):
        try:
            self.redis_pubsub = self.redis_client.pubsub()
            await self.redis_pubsub.subscribe("discord_to_web")
            
            async for message in self.redis_pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "message_handler",
                                "nickname": data['nickname'],
                                "content": data['content'],
                                "timestamp": data['timestamp'],
                                "is_highlighted": data.get('is_highlighted', False),
                                "from_discord": True
                            }
                        )
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from Discord: {message['data']}")
                    except Exception as error:
                        print(f"Error processing Discord message: {error}")
                        
        except asyncio.CancelledError:
            raise
        except Exception as error:
            print(f"Error in Discord listener: {error}")

    async def send_to_discord_via_redis(self, nickname, content, is_highlighted=False):
        try:
            message_data = json.dumps({
                'nickname': nickname,
                'content': content,
                'is_highlighted': is_highlighted,
                'timestamp': timezone.now().isoformat()
            })
            
            await self.redis_client.publish('web_to_discord', message_data)
            print(f"Sent to Discord via Redis: {nickname}: {content}")
        except Exception as error:
            print(f"Error sending to Discord via Redis: {error}")

    @database_sync_to_async
    def save_message(
        self, 
        nickname, 
        content, 
        ip_address, 
        discord_user_id=None, 
        is_from_discord=False
    ):
        message = Message.objects.create(
            nickname=nickname,
            content=content,
            ip_address=ip_address,
            discord_user_id=discord_user_id,
            is_from_discord=is_from_discord
        )
        return message.to_dict()

    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        messages = Message.objects.order_by("-timestamp")[:limit]
        return [message.to_dict() for message in reversed(messages)]