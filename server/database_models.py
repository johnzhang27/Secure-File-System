import sqlalchemy
import sqlalchemy.orm as sqlorm
import typing

# https://www.tutorialspoint.com/sqlalchemy/
# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_updating_objects.htm
# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_deleting_related_objects.htm#:~:text=It%20is%20easy%20to%20perform,session%20and%20commit%20the%20action.
# https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
# https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91#:~:text=SQLAlchemy%20can%20be%20used%20to,metadata%20based%20on%20that%20information.

Base = sqlorm.declarative_base()

rw_association_table = sqlalchemy.Table(
    "USER_RW_FILE_DATA",
    Base.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("USER_DATA.user_id"), primary_key=True),
    sqlalchemy.Column("abs_path", sqlalchemy.ForeignKey("FILE_DATA.abs_path"), primary_key=True),
)

access_association_table = sqlalchemy.Table (
    "USER_ACCESS_FILE_DATA",
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
    rw_files = sqlorm.relationship("File", secondary=rw_association_table,
                                           back_populates="rw_users")
    access_files = sqlorm.relationship("File", secondary=access_association_table,
                                               back_populates="access_users")
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
    permission_mode = sqlalchemy.Column(sqlalchemy.String, default="USER")
    key = sqlalchemy.Column(sqlalchemy.String)
    is_dir = sqlalchemy.Column(sqlalchemy.Boolean)
    is_home_dir = sqlalchemy.Column(sqlalchemy.Boolean)
    # NULL if home dir of user
    parent_dir = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("FILE_DATA.abs_path"))
    owner_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("USER_DATA.user_id"))
    owner = sqlorm.relationship("User", back_populates="owned_files")
    rw_users = sqlorm.relationship("User",secondary=rw_association_table,
                                          back_populates="rw_files")
    access_users = sqlorm.relationship("File", secondary=access_association_table,
                                               back_populates="access_files")
  
            