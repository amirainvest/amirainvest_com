from datetime import datetime, timedelta


def get_past_datetime(weeks=0, days=0, hours=0):
    return datetime.utcnow() - timedelta(weeks=weeks, days=days, hours=hours)


def get_class_attrs(_class):
    return [k for k, v in _class.__dict__.items()]
