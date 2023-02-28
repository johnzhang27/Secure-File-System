import sqlalchemy
import sqlalchemy.orm as sqlorm
import database_models
import bcrypt

# https://www.makeuseof.com/encrypt-password-in-python-bcrypt/ 

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
        enc_password = bcrypt.hashpw(password.encode('utf-8') ,bcrypt.gensalt())
        created_user = database_models.User(
            user_id=username,
            password=enc_password)
        self.session.add(created_user)
        self.configure_added_user_permissions(created_user)
        self.session.commit()
        return created_user
    
    def configure_added_user_permissions(self, user):
        files = sqlalchemy.select(database_models.File)
        for file in self.session.scalars(files):
            if file.permission_mode == "ALL":
                self.grant_access_permissions(file, user)
                self.grant_rw_permissions(file, user)
        self.session.commit()

    def remove_user_in_database(self, user):
        self.session.delete(user)
        self.session.commit()

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
        return bcrypt.checkpw(password.encode('utf-8'), passwordRec)
            
    def create_group_in_database(self, groupname):
        newGroup = database_models.Group(group_id=groupname)
        self.session.add(newGroup)
        self.session.commit()

    def remove_group_from_database(self, group):
        self.session.delete(group)
        self.session.commit()

    def check_group_exists(self, groupname):
        groups = sqlalchemy.select(database_models.Group)
        for group in self.session.scalars(groups):
            if group.group_id == groupname:
                return group
        return None

    def add_user_to_group(self, user, group):
        if user in group.users:
            return False
        group.users.append(user)
        self.configure_add_user_to_group_permissions(user, group)
        self.session.commit()
        return True
    
    def configure_add_user_to_group_permissions(self, user, group):
        for group_user in group.users:
            for file in group_user.owned_files:
                if file.permission_mode == "GROUP":
                    self.grant_rw_permissions(file, user)
        self.session.commit()


    def remove_user_from_group(self, user, group):
        if user not in group.users:
            return
        group.users.remove(user)
        self.configure_remove_user_from_group_permissions(user, group)
        self.session.commit()

    def configure_remove_user_from_group_permissions(self, user, group):
        for group_user in group.users:
            for file in group_user.owned_files:
                if file.permission_mode == "GROUP":
                    self.remove_rw_permissions(file, user)
        self.session.commit()


    def create_file(self, abspath, filename, file_key, user, is_dir, parent_dir, file_name_hash="", file_hash=""):
        file = database_models.File(abs_path=abspath, 
                                    file_name=filename,
                                    key=file_key,
                                    file_name_hash=file_name_hash,
                                    file_hash=file_hash,
                                    is_dir=is_dir,
                                    parent_dir=parent_dir,
                                    is_home_dir=False)
        user.owned_files.append(file)
        self.session.commit()

    def create_home_dir(self, abspath, filename, file_key, user, file_name_hash="", file_hash=""):
        file = database_models.File(abs_path=abspath, 
                                    file_name=filename,
                                    key=file_key,
                                    file_name_hash=file_name_hash,
                                    file_hash=file_hash,
                                    is_dir=True,
                                    is_home_dir=True)
        user.owned_files.append(file)
        self.session.commit()

    def rename_file(self, file, abspath, filename, file_name_hash=""):
        file.abs_path = abspath
        file.file_name = filename
        file.file_name_hash = file_name_hash
        self.session.commit()

    def edit_file(self, file, abspath, filename, file_name_hash="", file_hash=""):
        file.abs_path = abspath
        file.file_name = filename
        file.file_name_hash = file_name_hash
        file.file_hash = file_hash
        self.session.commit()

    def delete_file(self, file):
        self.session.delete(file)
        self.session.commit()

    def check_file_exists(self, abspath):
        files = sqlalchemy.select(database_models.File)
        for file in self.session.scalars(files):
            if file.abs_path == abspath:
                return file
        return None

    def check_access_permissions(self, file, requesting_user):
        owning_user = file.owner
        owning_group = owning_user.group
        if requesting_user in owning_group.users or requesting_user in file.access_users:
            return True
        else:
            return False

    def check_rw_permissions(self, file, requesting_user):
        if requesting_user in file.rw_users or file.owner == requesting_user:
            return True
        else:
            return False
    
    # modes: USER, GROUP, ALL
    def set_permission_mode(self, file, new_mode):
        if file.permission_mode == "USER":
            if new_mode == "USER":
                return False
            elif new_mode == "GROUP":
                if file.owner.group == None:
                    return False
                for user in file.owner.group.users:
                    self.grant_rw_permissions(file, user)
                return True
            elif new_mode == "ALL":
                users = sqlalchemy.select(database_models.User)
                for user in file.owner.group.users:
                    self.grant_rw_permissions(file, user)
                for user in self.session.scalars(users):
                    if user not in file.owner.group.users:
                        self.grant_access_permissions(file, user)
                        self.grant_rw_permissions(file, user)
                return True
            else:
                return False
        elif file.permission_mode == "GROUP":
            if new_mode == "USER":
                for user in file.owner.group.users:
                    self.remove_rw_permissions(file, user)
                return True
            elif new_mode == "GROUP":  
                return False
            elif new_mode == "ALL":
                users = sqlalchemy.select(database_models.User)
                for user in self.session.scalars(users):
                    if user not in file.owner.group.users:
                        self.grant_access_permissions(file, user)
                        self.grant_rw_permissions(file, user)
                return True
            else:
                return False
        elif file.permission_mode == "ALL":
            if new_mode == "USER":
                users = sqlalchemy.select(database_models.User)
                for user in self.session.scalars(users):
                    if user not in file.owner.group.users:
                        self.remove_access_permissions(file, user)
                    self.remove_rw_permissions(file, user)
                return True
            elif new_mode == "GROUP":
                users = sqlalchemy.select(database_models.User)
                for user in self.session.scalars(users):
                    if user not in file.owner.group.users:
                        self.remove_access_permissions(file, user)
                        self.remove_rw_permissions(file, user)
                return True
            elif new_mode == "ALL":
                return False
            else:
                return False
        self.session.commit()
        

    def grant_rw_permissions(self, file, requesting_user):
        if (file == None):
            return False
        if (file.owner == requesting_user or requesting_user in file.rw_users):
            return False
        file.rw_users.append(requesting_user)
        self.session.commit()
        return True

    def remove_rw_permissions(self, file, requesting_user):
        if (file == None):
            return False
        if (file.owner == requesting_user):
            return (False, "Cannot remove read/write permission from owner")
        if (requesting_user not in file.rw_users):
            return (False, "Specified user does not have read/write permission to that file!")
        file.rw_users.remove(requesting_user)
        self.session.commit()
        return (True, "Success")
    
    def grant_access_permissions(self, file, requesting_user):
        if (file == None):
            return False
        if (file.owner == requesting_user or requesting_user in file.access_users):
            return False
        file.access_users.append(requesting_user)
        self.session.commit()
        return True

    def remove_access_permissions(self, file, requesting_user):
        if (file == None):
            return False
        if (file.owner == requesting_user):
            return (False, "Cannot remove access permission from owner")
        if (requesting_user not in file.rw_users):
            return (False, "Specified user does not have access permission to that file!")
        file.access_users.remove(requesting_user)
        self.session.commit()
        return (True, "Success")

    def generate_general_lookup_table(self):
        files = sqlalchemy.select(database_models.File)
        file_list = []
        for file in self.session.scalars(files):
            file_list.append(file)
        lookup_table = self.add_to_lookup_table(file_list, {})
        return lookup_table

    def generate_file_lookup_table(self):
        files = sqlalchemy.select(database_models.File)
        file_list = {}
        for file in self.session.scalars(files):
            file_list[file.file_name] = file.key
        return file_list

    def generate_owned_lookup_table(self, user):
        lookup_table = {}
        lookup_table = self.add_to_lookup_table(user.owned_files, lookup_table)
        return lookup_table

    def generate_rw_lookup_table(self, user):
        lookup_table = self.generate_owned_lookup_table(user)
        lookup_table = self.add_to_lookup_table(user.rw_files, lookup_table)
        return lookup_table

    def generate_access_lookup_table(self, user):
        lookup_table = self.generate_rw_lookup_table(user)
        if user.group == None:
            return lookup_table
        for group_mem in user.group.users:
            lookup_table = self.add_to_lookup_table(group_mem.owned_files, lookup_table)
        return lookup_table

    def add_to_lookup_table(self, file_list, lookup_table):
        for file in file_list:
            if file.abs_path in lookup_table:
                continue
            lookup_table[file.abs_path] = (file.key, file.file_name)
        return lookup_table
    


    

