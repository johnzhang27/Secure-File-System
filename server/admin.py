import database_manager

db = database_manager.DatabaseManager()

def main():
    while True:
        command = input("Enter command: ")


def reset_database():
    db.drop_tables()
    db.create_tables()



if __name__ == "__main__":
    main()