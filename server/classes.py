import sqlalchemy
import sqlalchemy.orm as sqlorm
import typing

# https://www.tutorialspoint.com/sqlalchemy/

engine = sqlalchemy.create_engine("sqlite:///test_data.db", echo=True)
Base = sqlorm.declarative_base()

association_table = sqlalchemy.Table(
    "USER_GROUP_DATA",
    Base.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("USER_DATA.user_id"), primary_key=True),
    sqlalchemy.Column("group_id", sqlalchemy.ForeignKey("FILE_DATA.file_id"), primary_key=True),
)

class User(Base):
    __tablename__ = "USER_DATA"
    user_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    group_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("GROUP_DATA.group_id"))
    group = sqlorm.relationship("Group", back_populates="users")
    owned_files = sqlorm.relationship("File", back_populates="owner")
    permitted_files = sqlorm.relationship("File",
                                          secondary=association_table,
                                          back_populates="permitted_users")
class Group(Base):
    __tablename__ = "GROUP_DATA"
    group_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    users = sqlorm.relationship("User", back_populates="group")

class File(Base):
    __tablename__ = "FILE_DATA"
    file_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    parent_file = sqlalchemy.Column(sqlalchemy.String)
    file_name = sqlalchemy.Column(sqlalchemy.String)
    owner_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("USER_DATA.user_id"))
    owner = sqlorm.relationship("User", back_populates="owned_files")
    permitted_users = sqlorm.relationship("User",
                                          secondary=association_table,
                                          back_populates="permitted_files")
Base.metadata.create_all(engine)