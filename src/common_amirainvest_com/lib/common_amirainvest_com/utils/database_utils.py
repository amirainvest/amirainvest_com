import uuid

from fastapi.encoders import jsonable_encoder  # type: ignore
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect

from common_amirainvest_com.utils.exceptions.database import CompositePrimaryKeyError


def generate_uuid():
    return str(uuid.uuid4())


def get_primary_key(sql_model):
    primary_keys: list = [key.name for key in inspect(sql_model).primary_key]
    if len(primary_keys) > 1:
        raise CompositePrimaryKeyError(sql_model, primary_keys)
    return str(primary_keys[0])
