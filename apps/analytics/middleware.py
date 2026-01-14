import re
import ipaddress
from django.core.cache import cache
from .tasks import record_visit_async


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        self.bot_pattern = re.compile(
            r'bot|crawl|spider|scrape|monitor|check|scan|test|'
            r'wget|curl|python|java|http|lighthouse|pingdom|uptime|'
            r'statuspage|newrelic|datadog|nagios|zabbix|prometheus|'
            r'headless|phantom|selenium|go-http|okhttp|apache',
            re.IGNORECASE
        )
        
        self.excluded_paths = frozenset(['/admin/', '/static/', '/media/', '/ws/'])
        
        self.blocked_networks = [
            ipaddress.ip_network("2a06:98c0:3600::/48"),
        ]
    
    def __call__(self, request):
        if not any(request.path.startswith(p) for p in self.excluded_paths):
            ip = self._get_client_ip(request)
            
            if not self._is_blocked_ip(ip) and not self._is_bot(request):
                cache_key = f"visit_{ip}"
                if not cache.get(cache_key):
                    cache.set(cache_key, True, 300)
                    record_visit_async.delay(ip)
        
        return self.get_response(request)
    
    def _is_blocked_ip(self, ip):
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in network for network in self.blocked_networks)
        except ValueError:
            return False
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
        return ip
    
    def _is_bot(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if not user_agent or len(user_agent) < 10:
            return True
        
        if not user_agent.startswith('mozilla/'):
            return True
        
        if self.bot_pattern.search(user_agent):
            return True
        
        return False