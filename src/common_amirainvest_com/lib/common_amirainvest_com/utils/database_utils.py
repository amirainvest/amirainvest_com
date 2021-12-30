import uuid

from fastapi.encoders import jsonable_encoder  # type: ignore
from sqlalchemy import select
from sqlalchemy.inspection import inspect

from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.exceptions.database import CompositePrimaryKeyError


def generate_uuid():
    return str(uuid.uuid4())


def get_primary_key(sql_model):
    primary_keys: list = [key.name for key in inspect(sql_model).primary_key]
    if len(primary_keys) > 1:
        raise CompositePrimaryKeyError(sql_model, primary_keys)
    return str(primary_keys[0])


@Session
async def update(session, sql_model, update_data: dict):
    _object = (await session.execute(
        select(sql_model).filter_by(**{get_primary_key(sql_model): update_data[get_primary_key(sql_model)]})
    )).scalars().first()
    for field in jsonable_encoder(_object):
        if field in update_data:
            setattr(_object, field, update_data[field])
    session.add(_object)
    return _object
