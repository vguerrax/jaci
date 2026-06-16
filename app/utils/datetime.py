from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
import locale

# Timezone configuration
UTC_TZ = timezone.utc
LOCAL_TZ = ZoneInfo("America/Sao_Paulo")

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR")
    except locale.Error:
        # Fallback to system default
        pass


def format_local_datetime(dt: datetime, fmt: str = "%d/%m/%Y %H:%M") -> str:
    """Convert UTC datetime to local timezone for display"""
    if dt is None:
        return ""

    # If datetime has no timezone info, assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)

    # Convert to local timezone
    dt_local = dt.astimezone(LOCAL_TZ)
    return dt_local.strftime(fmt)


def format_local_date(dt: datetime | date, fmt: str = "%d/%m/%Y") -> str:
    """Convert UTC datetime to local date only"""
    if dt is None:
        return ""

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC_TZ)

        dt_local = dt.astimezone(LOCAL_TZ)
        return dt_local.strftime(fmt)

    return dt.strftime(fmt)


def now_local() -> datetime:
    """Get current datetime in local timezone"""
    return datetime.now(LOCAL_TZ)


def to_utc(dt_local: datetime) -> datetime:
    """Convert local datetime to UTC for storage"""
    if dt_local.tzinfo is None:
        dt_local = dt_local.replace(tzinfo=LOCAL_TZ)
    return dt_local.astimezone(UTC_TZ)


def to_local(dt_utc: datetime) -> datetime:
    """Convert UTC datetime to local"""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=UTC_TZ)
    return dt_utc.astimezone(LOCAL_TZ)


def parse_local_date(
    date_str: str,
    time_str: str = "00:00",
    date_format: str = "%Y-%m-%d",
    time_format: str = "%H:%M",
) -> datetime:
    """
    Parse a date string from form and convert to UTC for storage.
    """
    from datetime import datetime as dt

    # Combine date and time
    datetime_str = f"{date_str} {time_str}"
    dt_local = dt.strptime(datetime_str, f"{date_format} {time_format}")

    # Attach local timezone and convert to UTC
    dt_local = dt_local.replace(tzinfo=LOCAL_TZ)
    return dt_local.astimezone(UTC_TZ)
