import sqlalchemy
import sqlalchemy.orm as sqlorm
import typing

# using https://docs.sqlalchemy.org/en/20/orm/quickstart.html as base
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#setting-bi-directional-many-to-many


engine = sqlalchemy.create_engine("sqlite:///test_data.db", echo=True)

class Base(sqlorm.DeclarativeBase):
    pass

association_table = sqlalchemy.Table(
    "USER_GROUP_DATA",
    Base.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("USER_DATA.user_id"), primary_key=True),
    sqlalchemy.Column("group_id", sqlalchemy.ForeignKey("FILE_DATA.file_id"), primary_key=True),
)

class User(Base):
    __tablename__ = "USER_DATA"
    user_id: sqlorm.Mapped[str] = sqlorm.mapped_column(primary_key=True)
    password: sqlorm.Mapped[str]
    group_id: sqlorm.Mapped[typing.Optional["Group"]] = sqlorm.relationship(back_populates="users")
    owned_files: sqlorm.Mapped[typing.List["File"]] = sqlorm.relationship(back_populates="owner")
    permitted_files: sqlorm.Mapped[typing.List["File"]] = sqlorm.relationship(secondary=association_table,
                                                                              back_populates="permitted_users")

class Group(Base):
    __tablename__ = "GROUP_DATA"
    group_id: sqlorm.Mapped[str] = sqlorm.mapped_column(primary_key=True)
    users: sqlorm.Mapped[typing.List["User"]] = sqlorm.relationship(back_populates="group_id")

class File(Base):
    __tablename__ = "FILE_DATA"
    file_id: sqlorm.Mapped[str] = sqlorm.mapped_column(primary_key=True)
    parent_file: sqlorm.Mapped[str]
    file_name: sqlorm.Mapped[typing.Optional[str]] 
    owner: sqlorm.Mapped[str] = sqlorm.relationship(back_populates="owned_files")
    permiited_users: sqlorm.Mapped[typing.List["User"]] = sqlorm.relationship(secondary=association_table,
                                                                              back_populates="permitted_files")
Base.metadata.create_all(engine)