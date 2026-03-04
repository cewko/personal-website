import hmac
import hashlib
from django.conf import settings


def hash_ip(ip_address):
    return hmac.new(
        key=settings.SECRET_KEY.encode(),
        msg=ip_address.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()[:32]