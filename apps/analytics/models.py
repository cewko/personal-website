from django.db import models


class Visit(models.Model):
    ip_hash = models.CharField(max_length=32, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ["-timestamp"]
    
    def __str__(self):
        return f"{self.ip_hash[:8]}... - {self.timestamp}"
    
    @classmethod
    def get_stats(cls):
        return {
            "total_visits": cls.objects.count(),
            "unique_visitors": cls.objects.values("ip_hash").distinct().count(),
        }