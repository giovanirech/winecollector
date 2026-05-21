"""Unit tests for the ``User`` SQLAlchemy model.

The model is a thin subclass of ``fastapi_users.db.SQLAlchemyBaseUserTableUUID``
bound to the project ``Base``. These tests assert on the table metadata only
— no database connection is required.
"""

from __future__ import annotations

import pytest
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, String
from sqlalchemy.dialects import postgresql

from winecollector.database import Base
from winecollector.models import User


def test_user_table_name_is_users() -> None:
    assert User.__tablename__ == "users"


def test_user_is_registered_on_shared_metadata() -> None:
    assert "users" in Base.metadata.tables
    assert Base.metadata.tables["users"] is User.__table__


def test_user_inherits_required_columns() -> None:
    expected = {
        "id",
        "email",
        "hashed_password",
        "is_active",
        "is_superuser",
        "is_verified",
    }
    assert expected.issubset(set(User.__table__.columns.keys()))


def test_id_column_is_primary_key_and_uuid_typed() -> None:
    id_col = User.__table__.columns["id"]
    assert id_col.primary_key is True
    # ``GUID`` is the portable UUID TypeDecorator shipped by
    # fastapi-users-db-sqlalchemy; on the PostgreSQL dialect it materializes
    # as the native ``UUID`` column type.
    assert isinstance(id_col.type, GUID)
    pg_impl = id_col.type.load_dialect_impl(postgresql.dialect())
    assert isinstance(pg_impl, postgresql.UUID)


def test_email_column_has_unique_index() -> None:
    email_col = User.__table__.columns["email"]
    assert email_col.unique is True
    assert email_col.index is True
    assert email_col.nullable is False
    assert isinstance(email_col.type, String)
    assert email_col.type.length == 320


def test_hashed_password_column_is_not_null_string() -> None:
    col = User.__table__.columns["hashed_password"]
    assert col.nullable is False
    assert isinstance(col.type, String)
    assert col.type.length == 1024


@pytest.mark.parametrize(
    ("col_name", "default"),
    [("is_active", True), ("is_superuser", False), ("is_verified", False)],
)
def test_boolean_flag_columns_have_correct_defaults(
    col_name: str, default: bool
) -> None:
    col = User.__table__.columns[col_name]
    assert isinstance(col.type, Boolean)
    assert col.nullable is False
    assert col.default is not None
    assert col.default.arg is default
