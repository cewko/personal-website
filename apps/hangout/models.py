from django.db import models
from django.utils import timezone


class Message(models.Model):
    nickname = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_hash = models.CharField(max_length=32, null=True, blank=True)
    discord_user_id = models.CharField(max_length=32, null=True, blank=True)
    is_from_discord = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["discord_user_id"])
        ]
    
    def __str__(self):
        return f"{self.nickname}: {self.content[:50]}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "is_from_discord": self.is_from_discord,
            "discord_user_id": self.discord_user_id,
        }
