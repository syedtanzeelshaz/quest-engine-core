"""
Custom GraphQL scalar definitions for Ariadne.
Binds DateTime, Date, Time, UUID, and JSON scalars matching the schema registry.
"""
from __future__ import annotations

import json
from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from ariadne import ScalarType

datetime_scalar = ScalarType("DateTime")
date_scalar = ScalarType("Date")
time_scalar = ScalarType("Time")
uuid_scalar = ScalarType("UUID")
json_scalar = ScalarType("JSON")


@datetime_scalar.serializer
def serialize_datetime(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


@datetime_scalar.value_parser
def parse_datetime_value(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


@date_scalar.serializer
def serialize_date(value: Any) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


@date_scalar.value_parser
def parse_date_value(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


@time_scalar.serializer
def serialize_time(value: Any) -> str:
    if isinstance(value, time):
        return value.isoformat()
    return str(value)


@time_scalar.value_parser
def parse_time_value(value: Any) -> time:
    if isinstance(value, time):
        return value
    return time.fromisoformat(str(value))


@uuid_scalar.serializer
def serialize_uuid(value: Any) -> str:
    return str(value)


@uuid_scalar.value_parser
def parse_uuid_value(value: Any) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


@json_scalar.serializer
def serialize_json(value: Any) -> Any:
    return value


@json_scalar.value_parser
def parse_json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


ALL_SCALARS = [
    datetime_scalar,
    date_scalar,
    time_scalar,
    uuid_scalar,
    json_scalar,
]
