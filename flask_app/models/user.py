from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import book
# for validation messages, import flash
from flask import flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db="users_and_books"

    def __init__(self, data):
        self.id=data["id"]
        self.f_name=data["f_name"]
        self.l_name=data["l_name"]
        self.email=data["email"]
        self.password=data["password"]
        self.created_at=data["created_at"]
        self.updated_at=data["updated_at"]
        self.added_books=[]
        self.favorite_books=[]

# ******** ADD/CREATE NEW user *********
    @classmethod
    def create_new_user(cls, data):
        query = """
            INSERT INTO users
            (f_name, l_name, email, password)
            VALUES(%(f_name)s, %(l_name)s, %(email)s, %(password)s);
        """
        results= connectToMySQL(cls.db).query_db(query, data)
        return results
    

# ******** GET INDIVIDUAL USER INFO *********
    @classmethod
    def get_user_info(cls, data):
        query = """
            SELECT * FROM users
            WHERE id = %(id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        return cls(results[0])
    
    @classmethod
    def get_user_by_email(cls, data):
        query = """
            SELECT * FROM users
            WHERE email = %(email)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        if len(results)<1:
            return False
        
        # if not results:
        #     return False
        
        return cls(results[0])

# ******** SHOW ALL userS *********
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"

        results = connectToMySQL(cls.db).query_db(query)

        all_users = []

        for user in results:
            all_users.append(cls(user))
        return all_users

# ******** GET BOOK BY USER *********
    @classmethod
    def get_user_with_books(cls, data):
        query = "SELECT * FROM users LEFT JOIN books ON books.user_id =users.id WHERE users.id = %(id)s;"
        # query=" SELECT * FROM users JOIN favorites on users.id=favorites.user_id JOIN books ON favorites.book_id=books.id WHERE users.id=%(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data )

        one_user = cls(results[0])

        for row in results:
            book_data = {
                "id": row["books.id"],
                "user_id": row["user_id"],
                "title": row["title"],
                "author":row["author"],
                "page_count": row["page_count"],
                "created_at": row["books.created_at"],
                "updated_at": row["books.updated_at"]
                }
            one_book=book.Book(book_data)
            one_user.added_books.append(one_book)
        return one_user
    
    @classmethod
    def get_users_who_favored_book(cls,data):
        query="SELECT * FROM favorites JOIN users ON favorites.user_id=users.id WHERE favorites.book_id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data )
        users1=[]
        if results:
            for row in results:
                user=cls(row)
                users1.append(user)
            return users1
        return users1
    
    @classmethod
    def get_user_with_favorite_books(cls,data):
        query="""
            SELECT * FROM users 
            JOIN favorites on users.id=favorites.user_id 
            JOIN books ON favorites.book_id=books.id 
            WHERE users.id=%(id)s;
            """
        results = connectToMySQL(cls.db).query_db(query, data )
        print (results)
        return results



# ******** UPDATE *********
    @classmethod
    def update_user(cls, data):
        query = """
            UPDATE users
            SET f_name=%(f_name)s, l_name=%(l_name)s, email=%(email)s, updated_at=NOW() 
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query,data)

# ************ VALIDATIONS ***************
    @staticmethod
    def validate_user_registration(data):
        is_valid = True # we assume this is true

        one_user=User.get_user_by_email(data)
        if one_user:
            is_valid=False
            flash(" ! Account already exists. Try logging in instead.", "user_registration")

        if len(data["f_name"]) < 3:
            flash(" ! First Name must be at least 3 characters.", "user_registration")
            is_valid = False
        if len(data["l_name"]) < 3:
            flash(" ! Last Name must be at least 3 characters.", "user_registration")
            is_valid = False

        if len(data["email"]) == 0:
            flash(" ! Email cannot be left empty.", "user_registration")
            is_valid = False
        if not EMAIL_REGEX.match(data["email"]): 
            flash(" ! Invalid email. Try again.", "user_registration")
            is_valid = False

        if len(data["password"]) < 8:
            flash(" ! Password must be at least 8 characters.", "user_registration")
            is_valid = False
        if data["password"] != data["confirm_pw"]:
            is_valid=False
            flash(" ! Passwords do not match. Try again!", "user_registration")
        return is_valid
    
    @staticmethod
    def validate_login(data):
        is_valid = True # we assume this is true
        one_user=User.get_user_by_email(data)

        if not one_user:
            flash(" ! Invalid email and/or password.", "user_login")
            return False

        if len(data["email"]) == 0:
            flash(" ! Email cannot be left empty.", "user_login")
            return False
        
        if len(data["password"]) == 0:
            flash( "! Email cannot be left empty.", "user_login")
            return False

        if not bcrypt.check_password_hash(one_user.password, data["password"]):
            flash(" ! Invalid email and/or password.", "user_login")
            return False

        return one_user

    @staticmethod
    def validate_user_update(data):
        is_valid = True # we assume this is true

        # one_user=User.get_user_by_email(data)
        # if one_user:
        #     is_valid=False
        #     flash("Account already exists. Try logging in instead.", "user_update")

        if len(data["f_name"]) < 3:
            flash(" ! First Name must be at least 3 characters. Original data retained.", "user_update")
            is_valid = False
        if len(data["l_name"]) < 3:
            flash(" ! Last Name must be at least 3 characters. Original data retained.", "user_update")
            is_valid = False

        if len(data["email"]) <1:
            flash(" ! Email cannot be left empty. Original data retained.", "user_update")
            is_valid = False
        if not EMAIL_REGEX.match(data["email"]): 
            flash(" ! Invalid email format. Try again.", "user_update")
            is_valid = False

        # if len(data["password"]) < 8:
        #     flash("Password must be at least 8 characters.", "user_registration")
        #     is_valid = False
        # if data["password"] != data["confirm_pw"]:
        #     is_valid=False
        #     flash("Passwords do not match. Try again!", "user_registration")
        return is_valid

# ******** SHOW ALL userS *********
    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM users;"

        results = connectToMySQL(cls.db).query_db(query)
        all_users = []

        for user in results:
            all_users.append(cls(user))
        return all_users

# ******** SHOW INDIVIDUAL user INFO - NOT USED *********
    @classmethod
    def get_user_info(cls, data):
        query = """
            SELECT * FROM users
            WHERE id = %(id)s;
        """
        result = connectToMySQL(cls.db).query_db(query, data) 
        return cls(result[0])


# ******** GRAB SINGLE user WITH LIST OF bookS *********
    # @classmethod
    # def get_user_with_books(cls, data ):
    #     query = "SELECT * FROM users LEFT JOIN books ON books.user_id = users.id WHERE users.id = %(id)s;"
    #     results = connectToMySQL(cls.db).query_db(query, data )

    #     one_user = cls(results[0])

    #     for row in results:
    #         book_data = {
    #             "id": row["books.id"],
    #             "user_id": row["user_id"],
    #             "title": row["title"],
    #             "page_count": row["num_of_pages"],
    #             "created_at": row["books.created_at"],
    #             "updated_at": row["books.updated_at"]
    #         }

    #         one_book=book.Book(book_data)
    #         one_user.user_favorites.append(one_book)
    #     return one_user

# ******** DELETE user - !!! FK OPTION SET TO NULL !!! *********
    # @classmethod
    # def delete_user(cls, user_id):
    #     query="""
    #         DELETE FROM users
    #         WHERE id=%(id)s;
    #     """
    #     data={"id": user_id}
    #     results = connectToMySQL(cls.db).query_db(query, data)
    #     return results

