from datetime import datetime, timezone, timedelta

def moscow_now():
    """Текущее московское время"""
    moscow_tz = timezone(timedelta(hours=3))
    return datetime.now(moscow_tz).replace(tzinfo=None)
