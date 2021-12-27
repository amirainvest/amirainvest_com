import json
import os
import subprocess
import uuid
from typing import Container, Optional, Type

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty


def generate_pydantic_model_from_dict(data: dict, model_name: str):
    data_file = "data.json"
    with open(data_file, "w+") as file:
        file.write(json.dumps(data))
    with open("api_models.py", "a") as file:
        file.write(
            subprocess.Popen(
                f"datamodel-codegen --class-name '{model_name}' "
                f"--target-python-version 3.9 --input-file-type json "
                f"--input {data_file}",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.read()  # type: ignore
            .decode("utf-8")
            .split("from pydantic import BaseModel")[1]
        )
    os.remove(data_file)


class OrmConfig(BaseConfig):
    orm_mode = True


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = []
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None
                if str(column.type) == "UUID":
                    python_type = uuid.UUID
                elif hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)
    pydantic_model = create_model(db_model.__name__, __config__=config, **fields)  # type: ignore
    return pydantic_model


def remove_from_pydantic_model(pydantic_model, attr_to_remove):
    delattr(pydantic_model, attr_to_remove)
    return pydantic_model
