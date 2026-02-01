from datetime import datetime, timezone


def format_time_ago(dt):
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt, timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "moment ago"
    
    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes} min{'s' if minutes != 1 else ''} ago"
    
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    
    days = int(hours / 24)
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    
    months = int(days / 30)
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    
    years = int(months / 12)
    return f"{years} year{'s' if years != 1 else ''} ago"