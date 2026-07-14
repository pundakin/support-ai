from sqlalchemy.orm import DeclarativeBase


# Conventions for naming database objects (optional, but recommended)
# For example, indexes will be named: ix_table_column
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All models should inherit from this class.
    """
    pass


Base.metadata.naming_convention = convention