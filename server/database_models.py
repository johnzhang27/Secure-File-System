import sqlalchemy
import sqlalchemy.orm as sqlorm
import typing

# https://www.tutorialspoint.com/sqlalchemy/
# https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
# https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91#:~:text=SQLAlchemy%20can%20be%20used%20to,metadata%20based%20on%20that%20information.

Base = sqlorm.declarative_base()

association_table = sqlalchemy.Table(
    "USER_FILE_DATA",
    Base.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("USER_DATA.user_id"), primary_key=True),
    sqlalchemy.Column("abs_path", sqlalchemy.ForeignKey("FILE_DATA.abs_path"), primary_key=True),
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
    abs_path = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    file_name = sqlalchemy.Column(sqlalchemy.String)
    file_hash = sqlalchemy.Column(sqlalchemy.String)
    file_name_hash = sqlalchemy.Column(sqlalchemy.String)
    key = sqlalchemy.Column(sqlalchemy.String)
    is_dir = sqlalchemy.Column(sqlalchemy.Boolean)
    owner_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("USER_DATA.user_id"))
    owner = sqlorm.relationship("User", back_populates="owned_files")
    permitted_users = sqlorm.relationship("User",
                                          secondary=association_table,
                                          back_populates="permitted_files")