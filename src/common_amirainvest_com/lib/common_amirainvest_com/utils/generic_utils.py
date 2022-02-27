from datetime import datetime, timedelta
from decimal import Decimal


def get_past_datetime(weeks=0, days=0, hours=0):
    return datetime.utcnow() - timedelta(weeks=weeks, days=days, hours=hours)


def get_class_attrs(_class):
    return [k for k, v in _class.__dict__.items()]


def calculate_percent_change(initial_value: Decimal, end_value: Decimal) -> Decimal:
    return 100 * (end_value - initial_value) / initial_value
