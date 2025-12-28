import asyncio
import re
import json
import discord
from decouple import config
from discord.ext import commands
from apps.hangout.models import Message
from apps.hangout.redis_manager import get_async_redis_client


class HangoutDiscord:
    def __init__(self):
        self.token = config("DISCORD_BOT_TOKEN", default="")
        self.channel_id = config("DISCORD_CHANNEL_ID", default="", cast=int)
        self.highlight_user_id = config("DISCORD_USER_ID", default="")
        self.bot = None
        self.redis_client = None
        self.redis_pubsub = None
        self.redis_listener_task = None
        self.room_group_name = "hangout_main"
        
    async def setup(self):
        if not self.token or not self.channel_id:
            print("missing Discord bot token or channel ID")
            return False
        
        self.redis_client = get_async_redis_client()
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f"Discord bot logged in as {self.bot.user}")
            self.redis_listener_task = asyncio.create_task(self.listen_for_web_messages())
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            if message.channel.id != self.channel_id:
                return
                
            await self.handle_discord_message(message)
        
        return True
    
    async def handle_discord_message(self, message):
        try:
            nickname = message.author.display_name
            content = message.clean_content

            content = re.sub(r'<a?:\w+:\d+>', '', content)
            content = re.sub(r'https?://\S+', '', content)
            
            if not content.strip():
                return

            max_length = 280
            if len(content) > max_length:
                await message.channel.send(
                    f"{message.author.mention} message too long (max {max_length} characters)",
                    delete_after=5 
                )
                return
            
            is_highlighted = str(message.author.id) == self.highlight_user_id
            
            db_message = await self.save_message_async(
                nickname=nickname,
                content=content,
                discord_user_id=str(message.author.id),
                is_from_discord=True
            )
            
            message_data = json.dumps({
                "nickname": nickname,
                "content": content,
                "timestamp": db_message["timestamp"],
                "is_highlighted": is_highlighted,
                "discord_user_id": str(message.author.id)
            })

            await self.redis_client.publish("discord_to_web", message_data)
            print(f"Sent to web via Redis: {nickname}: {content}")
            
        except Exception as error:
            print(f"Error handling Discord message: {error}")
    
    async def listen_for_web_messages(self):
        try:
            self.redis_client = get_async_redis_client()
            self.redis_pubsub = self.redis_client.pubsub()
            await self.redis_pubsub.subscribe("web_to_discord")
            
            print("Listening for web messages...")
            
            async for message in self.redis_pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await self.send_to_discord(
                            data["nickname"],
                            data["content"],
                            data.get("is_highlighted", False)
                        )
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from web: {message['data']}")
                    except Exception as error:
                        print(f"Error processing web message: {error}")
                        
        except asyncio.CancelledError:
            print("Web message listener cancelled")
            raise
        except Exception as error:
            print(f"Error in web listener: {error}")
        finally:
            if self.redis_pubsub:
                try:
                    await self.redis_pubsub.unsubscribe("web_to_discord")
                    await self.redis_pubsub.close()
                except:
                    pass
            if self.redis_client:
                try:
                    await self.redis_client.aclose()
                except:
                    pass
    
    async def send_to_discord(self, nickname, content, is_highlighted=False):
        try:
            if not self.bot or not self.bot.is_ready():
                print("Bot not ready")
                return False
            
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print(f"Channel {self.channel_id} not found")
                return False
            
            if is_highlighted:
                formatted_message = f"**[{nickname}]:** {content}"
            else:
                formatted_message = f"**{nickname}:** {content}"
            
            await channel.send(formatted_message)
            print(f"Sent to Discord: {formatted_message}")
            return True
            
        except Exception as error:
            print(f"Error sending to Discord: {error}")
            return False
    
    async def save_message_async(self, nickname, content, discord_user_id, is_from_discord):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.save_message_sync,
            nickname,
            content,
            discord_user_id,
            is_from_discord
        )
    
    def save_message_sync(self, nickname, content, discord_user_id, is_from_discord):
        message = Message.objects.create(
            nickname=nickname,
            content=content,
            ip_address=None,
            discord_user_id=discord_user_id,
            is_from_discord=is_from_discord
        )
        return message.to_dict()
    
    async def start(self):
        if await self.setup():
            try:
                await self.bot.start(self.token)
            except Exception as error:
                print(f"Error starting bot: {error}")
        else:
            print("Bot setup failed")
    
    async def stop(self):
        if self.redis_listener_task:
            self.redis_listener_task.cancel()
            try:
                await self.redis_listener_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_pubsub:
            try:
                await self.redis_pubsub.unsubscribe("web_to_discord")
                await self.redis_pubsub.close()
            except Exception as e:
                print(f"Error closing pubsub: {e}")
        
        self.redis_client = None
        
        if self.bot:
            await self.bot.close()