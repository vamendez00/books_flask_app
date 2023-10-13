from flask_app.config.mysqlconnection import connectToMySQL
# for validation messages, import flash
from flask import flash
from flask_app.models import user

class Book:
    db="users_and_books"

    def __init__(self, data):
        self.id=data["id"]
        self.user_id=data["user_id"]
        self.title=data["title"]
        self.author=data["author"]
        self.page_count=data["page_count"]
        self.created_at=data["created_at"]
        self.updated_at=data["updated_at"]
        self.reader=None

# ******** ADD/CREATE NEW book*********
    @classmethod
    def create_new_book(cls, data):
        query = """
            INSERT INTO books
            (user_id, title, author, page_count, created_at, updated_at)
            VALUES(%(user_id)s, %(title)s, %(author)s, %(page_count)s, NOW(), NOW());
        """
        results= connectToMySQL(cls.db).query_db(query, data)
        return results
    
# ******** GET ALL bookS *********
    @classmethod
    def get_all_books(cls):
        query = """
            SELECT * FROM books
            JOIN users ON books.user_id=users.id;
            """

        results = connectToMySQL(cls.db).query_db(query)

        all_books = []

        for record in results:
            one_book=cls(record)
            
            user_data={
                "id":record["users.id"],
                "f_name":record["f_name"],
                "l_name":record["l_name"],
                "email":record["email"],
                "password":record["password"],
                "created_at":record["users.created_at"],
                "updated_at":record["users.updated_at"],
            }
            
            one_book.reader=user.User(user_data)
            all_books.append(one_book)
        return all_books
    
# ******** GET ONE book *********
    @classmethod
    def get_one_book(cls, data):
        query = """
            SELECT * FROM books
            JOIN users ON books.user_id=users.id
            WHERE books.id = %(id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        one_book= cls(results[0])

        user_data={
            "id":results[0]["users.id"],
            "f_name":results[0]["f_name"],
            "l_name":results[0]["l_name"],
            "email":results[0]["email"],
            "password":results[0]["password"],
            "created_at":results[0]["users.created_at"],
            "updated_at":results[0]["users.updated_at"],
        }
        one_book.reader=user.User(user_data)
        return one_book

# # ************** GET book WITH USER **********
#     @classmethod
#     def get_book_with_user(cls, data ):
#         query = "SELECT * FROM books JOIN users ON books.user_id=users.id WHERE books.id = %(id)s;"
#         results = connectToMySQL(cls.db).query_db(query, data )
#         one_book=cls(results[0])
#         for row in results:
#             user_data = {
#                 "id": row["users.id"],
#                 "name": row["name"],
#                 "created_at": row["users.created_at"],
#                 "updated_at": row["users.updated_at"]
#             }
            
#             one_user=user.User(user_data)
#             one_book.school.append(one_user)
#             return one_book
        
# ******** DELETE book *********
    @classmethod
    def delete_book(cls, id):
        query="""
            DELETE FROM books
            WHERE id=%(id)s;
        """
        data={"id": id}
        return connectToMySQL(cls.db).query_db(query, data)
    
    # ******** DELETE book *********
    @classmethod
    def delete_fav_book(cls, id):
        query="""
            DELETE FROM favorites
            WHERE book_id=%(id)s;
        """
        data={"id": id}
        return connectToMySQL(cls.db).query_db(query, data)

# ************ VALIDATE book ***************
    @staticmethod
    def validate_book(data):
        is_valid = True

        if len(data["title"]) < 2:
            flash(' "Book title must be at least 2 characters." ', "books")
            is_valid = False

        if len(data["author"]) < 2:
            flash(' "Author must be at least 2 characters long." ', "books")
            is_valid = False

        if len(data["page_count"]) == 0:
            flash(' "Number of pages cannot be left empty." ', "books")
            is_valid = False

        return is_valid
    
    @classmethod
    def add_fav_book(cls, data):
        query="""
            INSERT INTO favorites (book_id, user_id) 
            VALUES (%(book_id)s, %(user_id)s)
        """
        return connectToMySQL(cls.db).query_db(query, data)