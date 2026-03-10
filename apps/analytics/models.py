from django.db import models
from django.db.models import Count
from django.core.cache import cache


class Visit(models.Model):
    ip_hash = models.CharField(max_length=32, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ["-timestamp"]
    
    def __str__(self):
        return f"{self.ip_hash[:8]}... - {self.timestamp}"
    
    @classmethod
    def get_stats(cls):
        stats = cache.get("analytics:visitor_stats")

        if stats:
            return stats

        res = cls.objects.aggregate(
            total_visits=Count("id"),
            unique_visitors=Count("ip_hash", distinct=True)
        )

        cache.set("nalytics:visitor_stats", res, 60)
        return res