"""Timezone utilities for consistent datetime handling across the application.

All check-in/out timestamps should be stored and displayed in the configured
local timezone (default: Asia/Ho_Chi_Minh = UTC+7).

Uses zoneinfo.ZoneInfo (Python 3.9+) with pytz fallback for systems
missing tzdata (e.g. Windows without the tzdata package).
"""
from datetime import datetime, timezone, timedelta

# --- Build a timezone object for Vietnam (UTC+7) ---
_DEFAULT_TZ_NAME = 'Asia/Ho_Chi_Minh'

def _make_tz(tz_name):
    """Return a timezone object, trying zoneinfo first, then pytz."""
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(tz_name)
    except Exception:
        pass
    try:
        import pytz
        return pytz.timezone(tz_name)
    except Exception:
        pass
    # Last resort: fixed UTC+7 offset (matches Vietnam)
    return timezone(timedelta(hours=7))


_VN_TZ = _make_tz(_DEFAULT_TZ_NAME)


def _get_app_tz():
    """Return the configured application timezone.

    Reads TIMEZONE from Flask config at runtime; falls back to Vietnam time.
    """
    try:
        from flask import current_app
        tz_name = current_app.config.get('TIMEZONE', _DEFAULT_TZ_NAME)
        return _make_tz(tz_name)
    except Exception:
        return _VN_TZ


def get_local_now():
    """Return the current datetime in the application's local timezone."""
    return datetime.now(_get_app_tz())


def to_local(dt):
    """Convert a datetime (naive or timezone-aware) to the local timezone.

    - Naive datetime is assumed to already be in the local timezone (the
      common case for check-in/out times recorded by get_local_now()).
    - UTC-aware datetime is converted to local time.
    - Local-aware datetime is returned as-is.
    """
    if dt is None:
        return None

    tz = _get_app_tz()

    if dt.tzinfo is None:
        # Naive — assume it was recorded in local time; attach tz
        return dt.replace(tzinfo=tz)

    # Already timezone-aware — convert
    return dt.astimezone(tz)


def format_time_24h(dt):
    """Format a datetime as HH:MM:SS (24h) for display. Returns '--' if None."""
    if dt is None:
        return '--'
    local_dt = to_local(dt)
    return local_dt.strftime('%H:%M:%S')


def format_datetime_24h(dt):
    """Format a datetime as YYYY-MM-DD HH:MM:SS (24h). Returns '--' if None."""
    if dt is None:
        return '--'
    local_dt = to_local(dt)
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')


def format_time_input(dt):
    """Format a datetime for <input type="datetime-local">: YYYY-MM-DDTHH:MM."""
    if dt is None:
        return ''
    local_dt = to_local(dt)
    return local_dt.strftime('%Y-%m-%dT%H:%M')