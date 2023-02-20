import sqlalchemy
import sqlalchemy.orm as sqlorm
import database_models

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_updating_objects.htm

class DatabaseManager:
    
    def __init__(self):
        self.engine = sqlalchemy.create_engine("sqlite:///test_data.db")
        self.session = sqlalchemy.orm.Session(self.engine)

    def create_tables(self):
        database_models.Base.metadata.create_all(self.engine)
        print("Created database tables")

    def drop_tables(self):
        database_models.Base.metadata.drop_all(self.engine)
        print("Removed database tables")
    
    def close_session(self):
        self.session.close()

    def register_user_in_database(self, username, password): 
        created_user = database_models.User(
            user_id=username,
            password=password)
        self.session.add(created_user)
        self.session.commit()
        return created_user

    def remove_user_in_database(self, username, password):
        return

    def check_user_exists(self, username):
        users = sqlalchemy.select(database_models.User)
        for user in self.session.scalars(users):
            if user.user_id == username:
                return user
        return None

    def login_in_user(self, username, password):
        passwordSt = sqlalchemy.select(database_models.User.password).where(database_models.User.user_id 
                                                                            == username)
        passwordRec = self.session.execute(passwordSt).first()[0]
        if (passwordRec != password):
            return False
        return True
            
    def create_group_in_database(self, groupname):
        newGroup = database_models.Group(group_id=groupname)
        self.session.add(newGroup)
        self.session.commit()

    def remove_group_from_database(self, group):
        return

    def check_group_exists(self, groupname):
        groups = sqlalchemy.select(database_models.Group)
        for group in self.session.scalars(groups):
            if group.group_id == groupname:
                return group
        return None

    def add_user_to_group(self, user, group):
        if user in group.users:
            return
        group.users.append(user)
        self.session.commit()

    def remove_user_from_group(self, user, group):
        if user not in group.users:
            return
        group.users.remove(user)
        self.session.commit()

   
    def create_file(self, abspath, filename, file_key, user, is_dir, file_hash=""):
        file = database_models.File(abs_path=abspath, 
                                    file_name=filename,
                                    key=file_key,
                                    hash=file_hash,
                                    is_dir=is_dir)
        user.owned_files.append(file)
        self.session.commit()

    def rename_file(self, file, abspath, filename):
        file.abs_path = abspath
        file.file_name = filename
        self.session.commit()


    def edit_file(self, file, abspath, filename, file_hash=""):
        file.abs_path = abspath
        file.file_name = filename
        file.hash = file_hash
        self.session.commit()

    def check_file_exists(self, abspath):
        files = sqlalchemy.select(database_models.File)
        for file in files:
            if file.abs_path == abspath:
                return file
        return None

    def check_group_permissions(self, file, requesting_user):
        owning_user = file.owner
        owning_group = owning_user.group
        if requesting_user in owning_group.users:
            return True
        else:
            return False

    def check_file_permissions(self, file, requesting_user):
        if requesting_user in file.permitted_users or file.owner == requesting_user:
            return True
        else:
            return False

    def grant_permissions(self, file, requesting_user):
        if (file.owner == requesting_user or requesting_user in file.permitted_users):
            return False
        file.permitted_users.append(requesting_user)
        self.session.commit()
        return True

    def remove_permissions(self, file, requesting_user):
        if (file.owner == requesting_user):
            return (False, "Cannot remove permission from owner")
        if (requesting_user not in file.permitted_users):
            return (False, "Specified user does not have permission to that file!")
        file.permitted_users.remove(requesting_user)
        self.session.commit()
        return (True, "Success")

    def generate_owned_lookup_table(self, user):
        lookup_table = {}
        lookup_table = self.add_to_lookup_table(user.owned_files, lookup_table)
        return lookup_table

    def generate_permitted_lookup_table(self, user):
        lookup_table = self.generate_owned_lookup_table(user)
        lookup_table = self.add_to_lookup_table(user.permitted_files, lookup_table)
        return lookup_table

    def generate_group_permitted_lookup_table(self, user):
        lookup_table = self.generate_permitted_lookup_table(self, user)
        for group_mem in user.group.users:
            lookup_table = self.add_to_lookup_table(group_mem.owned_files, lookup_table)
        return lookup_table

    def add_to_lookup_table(self, file_list, lookup_table):
        for file in file_list:
            if file.abs_path in lookup_table:
                continue
            lookup_table[file.abs_path] = (file.file_name, file.key)
        return lookup_table
    


    

