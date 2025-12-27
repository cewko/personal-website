from decouple import config


class OnlineUserTracker:
    ONLINE_SET_KEY = "online_users"
    USER_TTL = 90
    
    def __init__(self):
        self.redis_url = config("REDIS_URL", default="redis://localhost:6379")
    
    async def mark_user_online(self, user_id, redis_client):
        try:
            await redis_client.sadd(self.ONLINE_SET_KEY, user_id)
            await redis_client.setex(f"online_user:{user_id}", self.USER_TTL, "1")
        except Exception as error:
            print(f"Error marking user online: {error}")
    
    async def mark_user_offline(self, user_id, redis_client):
        try:
            await redis_client.srem(self.ONLINE_SET_KEY, user_id)
            await redis_client.delete(f"online_user:{user_id}")
        except Exception as error:
            print(f"Error marking user offline: {error}")
    
    async def get_online_count(self, redis_client):
        try:
            count = await redis_client.scard(self.ONLINE_SET_KEY)
            return count
        except Exception as error:
            print(f"Error getting online count: {error}")
            return 0
    
    async def cleanup_expired_users(self, redis_client):
        try:
            all_users = await redis_client.smembers(self.ONLINE_SET_KEY)
            for user_id in all_users:
                exists = await redis_client.exists(f"online_user:{user_id}")
                if not exists:
                    await redis_client.srem(self.ONLINE_SET_KEY, user_id)
        except Exception as e:
            print(f"Error cleaning up expired users: {e}")
    
    async def heartbeat(self, user_id, redis_client):
        await self.mark_user_online(user_id, redis_client)