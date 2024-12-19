import mysql.connector
from datetime import datetime
import re

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="library_management"
)
cursor = db.cursor(dictionary=True)

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    issued_to INT,
    issue_date DATETIME
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    available_cards INT NOT NULL,
    issued_books INT NOT NULL
)
""")

db.commit()

def check_email(email):
    email = email.lower().strip()
    end = "gehu.ac.in"
    if not email.endswith(end):
        return False
    if '@' not in email or email.count('@') > 1:
        return False
    username, domain = email.split('@')
    if '.' not in username or not username.split('.')[-1].isdigit():
        return False
    digits = re.findall(r'\d+', username)
    if len(digits) == 0 or len(digits[0]) < 8:
        return False
    return True

def calculate_fine(issue_date):
    today = datetime.now()
    diff = today - issue_date
    if diff.days > 30:
        return (diff.days - 30) * 1  # $1 per day after 30 days
    return 0

def admin_login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = TRUE", (username, password))
    return cursor.fetchone() is not None

def user_login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = FALSE", (username, password))
    return cursor.fetchone() is not None

def user_signup():
    username = input("Enter username: ")
    phone_no = input("Enter phone number: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")

    if not re.match(r'^[6-9]\d{9}$', phone_no):
        print("Please enter a valid 10-digit phone number.")
        return
    if not check_email(email):
        print("Invalid email format. Please use a valid 'gehu.ac.in' email.")
        return
    if password != confirm_password:
        print("Passwords do not match.")
        return
    if len(password) < 8:
        print("Password must be at least 8 characters long.")
        return
    if not re.search(r'[A-Z]', password):
        print("Password must contain at least one uppercase letter.")
        return
    if not re.search(r'[a-z]', password):
        print("Password must contain at least one lowercase letter.")
        return
    if not re.search(r'\d', password):
        print("Password must contain at least one digit.")
        return
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        print("Password must contain at least one special character.")
        return

    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, FALSE)", (username, password))
    db.commit()
    print("User account created successfully!")

def display_all_members():
    cursor.execute("SELECT * FROM members ORDER BY id")
    members = cursor.fetchall()
    for member in members:
        print(f"ID: {member['id']}, Name: {member['name']}, Department: {member['department']}, Phone: {member['phone']}, Available Cards: {member['available_cards']}, Issued Books: {member['issued_books']}")

def display_all_books():
    cursor.execute("SELECT * FROM books ORDER BY id")
    books = cursor.fetchall()
    for book in books:
        print(f"ID: {book['id']}, Name: {book['name']}, Author: {book['author']}, Status: {book['status']}, Category: {book['category']}")

def add_book():
    name = input("Enter book name: ")
    author = input("Enter author name: ")
    category = input("Enter category: ")
    cursor.execute("INSERT INTO books (name, author, status, category) VALUES (%s, %s, %s, %s)",
                   (name, author, "Available", category))
    db.commit()
    print("Book added successfully.")

def remove_book():
    book_id = int(input("Enter book ID to remove: "))
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    db.commit()
    if cursor.rowcount > 0:
        print(f"Book with ID {book_id} has been removed successfully.")
    else:
        print("Book not found.")

def add_member():
    name = input("Enter member name: ")
    department = input("Enter Your course: ")
    duration=input("course duration")
    phone = input("Enter phone number: ")
    available_cards = int(input("Enter number of available cards: "))
    cursor.execute("INSERT INTO members (name, department, phone, available_cards, issued_books) VALUES (%s, %s, %s, %s, %s)",
                   (name, department, phone, available_cards, 0))
    db.commit()
    print("Member added successfully.")

def remove_member():
    member_id = int(input("Enter member ID to remove: "))
    cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
    db.commit()
    if cursor.rowcount > 0:
        print(f"Member with ID {member_id} has been removed successfully.")
    else:
        print("Member not found.")

def issue_book():
    book_id = int(input("Enter book ID: "))
    member_id = int(input("Enter member ID: "))

    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()

    if not book:
        print("Book not found.")
        return
    if not member:
        print("Member not found.")
        return
    if book['status'] == "Checked Out":
        print("Book is already issued.")
        return
    if member['available_cards'] <= 0:
        print("Member has no available cards.")
        return

    cursor.execute("UPDATE books SET status = 'Checked Out', issued_to = %s, issue_date = %s WHERE id = %s",
                   (member['id'], datetime.now(), book['id']))
    cursor.execute("UPDATE members SET available_cards = available_cards - 1, issued_books = issued_books + 1 WHERE id = %s",
                   (member['id'],))
    db.commit()
    print(f"Book '{book['name']}' issued to {member['name']}.")

def return_book():
    book_id = int(input("Enter book ID: "))
    member_id = int(input("Enter member ID: "))

    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()

    if not book:
        print("Book not found.")
        return
    if not member:
        print("Member not found.")
        return
    if book['status'] == "Available":
        print("Book is not issued.")
        return

    fine = calculate_fine(book['issue_date'])
    if fine > 0:
        print(f"Fine: ${fine}")
        print("Please pay the fine.")

    cursor.execute("UPDATE books SET status = 'Available', issued_to = NULL, issue_date = NULL WHERE id = %s",
                   (book['id'],))
    cursor.execute("UPDATE members SET available_cards = available_cards + 1, issued_books = issued_books - 1 WHERE id = %s",
                   (member['id'],))
    db.commit()
    print(f"Book '{book['name']}' returned by {member['name']}.")

def check_member_status():
    member_id = int(input("Enter member ID: "))
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()

    if member:
        print(f"Member: {member['name']}")
        print(f"Department: {member['department']}")
        print(f"Phone: {member['phone']}")
        print(f"Available Cards: {member['available_cards']}")
        print(f"Issued Books: {member['issued_books']}")

        cursor.execute("SELECT * FROM books WHERE issued_to = %s", (member['id'],))
        issued_books = cursor.fetchall()
        if issued_books:
            print("Issued Books:")
            for book in issued_books:
                issue_date = book['issue_date']
                fine = calculate_fine(issue_date)
                print(f"Book: {book['name']} (ID: {book['id']})")
                print(f"Issue Date: {issue_date.strftime('%Y-%m-%d')}")
                print(f"Fine: ${fine}")
                print()
        else:
            print("No books currently issued.")
    else:
        print("Member not found.")

def search_book():
    book_name = input("Enter book name to search: ").lower()
    cursor.execute("SELECT * FROM books WHERE LOWER(name) LIKE %s", (f"%{book_name}%",))
    found_books = cursor.fetchall()
    
    if found_books:
        print("Search Results:")
        for book in found_books:
            print(f"Book ID: {book['id']}")
            print(f"Name: {book['name']}")
            print(f"Author: {book['author']}")
            print(f"Status: {book['status']}")
            print(f"Category: {book['category']}")
            print()
    else:
        print("No books found.")

def display_categories():
    cursor.execute("SELECT DISTINCT category FROM books")
    categories = [row['category'] for row in cursor.fetchall()]
    print("Book Categories:")
    for category in categories:
        print(f"- {category}")

def display_books_by_category():
    display_categories()
    category = input("Enter category to display books: ")
    cursor.execute("SELECT * FROM books WHERE category = %s", (category,))
    books_in_category = cursor.fetchall()
    
    if books_in_category:
        print(f"Books in {category}:")
        for book in books_in_category:
            print(f"Book ID: {book['id']}")
            print(f"Name: {book['name']}")
            print(f"Author: {book['author']}")
            print(f"Status: {book['status']}")
            print()
    else:
        print(f"No books found in the category: {category}")

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Display All Members")
        print("2. Display All Books")
        print("3. Add A New Book")
        print("4. Remove A Book")
        print("5. Add A New Member")
        print("6. Remove A Member")
        print("7. Issue a Book")
        print("8. Return a Book")
        print("9. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            display_all_members()
        elif choice == '2':
            display_all_books()
        elif choice == '3':
            add_book()
        elif choice == '4':
            remove_book()
        elif choice == '5':
            add_member()
        elif choice == '6':
            remove_member()
        elif choice == '7':
            issue_book()
        elif choice == '8':
            return_book()
        elif choice == '9':
            break
        else:
            print("Invalid choice. Please try again.")

def user_menu():
    while True:
        print("\nUser Menu:")
        print("1. Check Member Status")
        print("2. Search a Book")
        print("3. Display Book Categories")
        print("4. Display Books by Category")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            check_member_status()
        elif choice == '2':
            search_book()
        elif choice == '3':
            display_categories()
        elif choice == '4':
            display_books_by_category()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def main_menu():
    while True:
        print("\nLibrary Management System")
        print("1. Admin Login")
        print("2. User Login")
        print("3. User Signup")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            if admin_login():
                print("Admin login successful.")
                admin_menu()
            else:
                print("Invalid admin credentials.")
        elif choice == '2':
            if user_login():
                print("User login successful.")
                user_menu()
            else:
                print("Invalid user credentials.")
        elif choice == '3':
            user_signup()
        elif choice == '4':
            print("Thank you for using the Library Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()