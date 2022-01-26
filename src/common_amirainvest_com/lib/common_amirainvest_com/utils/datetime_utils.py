from datetime import datetime

from dateutil.parser import parse


def parse_iso_8601_from_string(timestamp: str) -> datetime:
    return parse_iso_8601_from_datetime(parse(timestamp))


def parse_iso_8601_from_datetime(timestamp: datetime) -> datetime:
    return timestamp.replace(tzinfo=None)
