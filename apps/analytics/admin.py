from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['ip_hash_short', 'timestamp']
    list_filter = ['timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['ip_hash', 'timestamp']
    
    def ip_hash_short(self, obj):
        return f"{obj.ip_hash}"
    ip_hash_short.short_description = "IP Hash"
    
    def has_add_permission(self, request):
        return False