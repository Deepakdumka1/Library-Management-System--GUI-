import flet as ft
from flet import Page, View, AppBar, ElevatedButton, Text, TextField, Column, Row, Container, Image, DataTable, DataColumn, DataRow, DataCell, IconButton, icons, dropdown, border, padding, margin, alignment
import mysql.connector
import qrcode
import io
import base64
from datetime import datetime, timedelta
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

def main(page: Page):
    page.title = "Library Management System"
    page.theme_mode = "light"
    page.bgcolor = "#EBEFFF"
    
    def show_dialog(page, title, content):
        def close_dialog(e):
            dialog.open = False
            page.update()
            
        dialog = ft.AlertDialog(
            title=Text(title),
            content=Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=content if isinstance(content, ft.Control) else Text(content),
                            expand=True,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=20,
                width=400,
                height=500,
            ),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def home_view(page: Page):
        return View(
            "/",
            [
                AppBar(title=Text("Library Management System"), bgcolor="#AFB3FF"),
                Column([
                    ElevatedButton("Admin Login", on_click=lambda _: page.go("/admin-login"),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),bgcolor="#fde686",color="black"),
                    ElevatedButton("User Login", on_click=lambda _: page.go("/user-login"), width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),bgcolor="#86e2fd",color="black"),
                    ElevatedButton("User Signup", on_click=lambda _: page.go("/user-signup"), width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),bgcolor="#86fda1",color="black"),
                    ElevatedButton("Exit", on_click=lambda _: page.window_close(), width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),bgcolor="#fc6e6e",color="black",)
                ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            ],
            bgcolor="#EBEFFF",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def admin_login_view(page: Page):
        def login(e):
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = TRUE", (username.value, password.value))
            user = cursor.fetchone()
            if user:
                page.go("/admin")
            else:
                error_text.value = "Invalid username or password"
                page.update()

        username = TextField(label="Username", width=300)
        password = TextField(label="Password", password=True, width=300)
        login_button = ElevatedButton("Login", on_click=login)
        error_text = Text("", color="red")

        return View(
            "/admin-login",
            [
                AppBar(title=Text("Admin Login"), bgcolor="#AFB3FF", leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                Row([
                    Container(
                        content=Column([
                            Text("Welcome Back!", size=32, weight=ft.FontWeight.BOLD),
                            username,
                            password,
                            login_button,
                            error_text
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        bgcolor="light",
                        border_radius=10,
                    ),
                    Image(
                        src="log_in.png",
                        width=400,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            bgcolor="#EBEFFF",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

    def user_login_view(page: Page):
        def login(e):
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = FALSE", (username.value, password.value))
            user = cursor.fetchone()
            if user:
                page.go("/user")
            else:
                error_text.value = "Invalid username or password"
                page.update()

        username = TextField(label="Username", width=300)
        password = TextField(label="Password", password=True, width=300)
        login_button = ElevatedButton("Login", on_click=login)
        error_text = Text("", color="red")

        return View(
            "/user-login",
            [
                AppBar(title=Text("User Login"), bgcolor="#AFB3FF", leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                Row([
                    Container(
                        content=Column([
                            Text("Welcome Back!", size=32, weight=ft.FontWeight.BOLD),
                            username,
                            password,
                            login_button,
                            error_text
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        bgcolor="light",
                        border_radius=10,
                    ),
                    Image(
                        src="log_in.png",
                        width=400,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            bgcolor="#EBEFFF",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )
    def user_signup_view(page: Page):
        def signup(e):
            error_message = ""
            # Phone number validation
            if not re.match(r'^[6-9]\d{9}$', phone_no.value):
                error_message = "Please Enter a Valid 10 digits Phone Number!!"
            # Email validation
            elif not check_email(email.value):
                error_message = "Invalid email format. Please use a valid 'gehu.ac.in' email."
            # Password validation
            elif password.value != confirm_password.value:
                error_message = "Passwords do not match"
            elif len(password.value) < 8:
                error_message = "Password must be at least 8 characters long"
            elif not re.search(r'[A-Z]', password.value):
                error_message = "Password must contain at least one uppercase letter"
            elif not re.search(r'[a-z]', password.value):
                error_message = "Password must contain at least one lowercase letter"
            elif not re.search(r'\d', password.value):
                error_message = "Password must contain at least one digit"
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password.value):
                error_message = "Password must contain at least one special character"
        
            if error_message:
                error_text.value = error_message
                page.update()
                return
        
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, FALSE)", (username.value, password.value))
            db.commit()
            show_dialog(page, "Success", "User account created successfully!")
            page.go("/user-login")

        username = TextField(label="Username", width=300, color="black")
        phone_no = TextField(label="Phone Number", width=300)
        email = TextField(label="Email", width=300) 
        password = TextField(label="Password", password=True, width=300)
        confirm_password = TextField(label="Confirm Password", password=True, width=300)
        signup_button = ElevatedButton("Sign Up", on_click=signup, width=140, height=40)
        error_text = Text("", color="red")

        return View(
            "/user-signup",
            [
                AppBar(title=Text("User Signup"), bgcolor="#AFB3FF", leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                Row([
                    Container(
                        content=Column([
                            Text("Create a new account!", size=32, weight=ft.FontWeight.BOLD),
                            username,
                            phone_no,
                            email,
                            password,
                            confirm_password,
                            signup_button,
                            error_text
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=100,
                        
                        bgcolor="light",
                        border_radius=10,
                    ),
                    Image(
                        src="sign_up.png",
                        width=550,
                        height=550,
                        fit=ft.ImageFit.CONTAIN,
                    ),                   
                ],alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            bgcolor="#EBEFFF",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

    def check_email(email):
        email = email.lower()
        end = "gehu.ac.in"
        email = email.strip()
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

    def admin_view(page: Page):
        return View(
            "/admin",
            [
                AppBar(title=Text("Admin View"), bgcolor="#AFB3FF", leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                Column([
                    ElevatedButton("Display All Members", on_click=lambda _: page.go("/members"),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Display All Books", on_click=lambda _: page.go("/books"),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Add A New Book", on_click=lambda _: add_book(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Remove A Book", on_click=lambda _: remove_book(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Add A New Member", on_click=lambda _: add_member(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Remove A Member", on_click=lambda _: remove_member(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Issue a Book", on_click=lambda _: issue_book(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Return a Book", on_click=lambda _: return_book(page),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black"),
                    ElevatedButton("Back to Main Menu", on_click=lambda _: page.go("/"),width=240, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)),color="black")
                ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def user_view(page: Page):
        return View(
            "/user",
            [
                AppBar(title=Text("User View"), bgcolor="#AFB3FF", leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                Column([
                    ElevatedButton("Check Member Status", on_click=lambda _: check_member_status(page),width=265, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))),
                    ElevatedButton("Search a Book", on_click=lambda _: search_book(page),width=265, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))),
                    ElevatedButton("Display Book Categories", on_click=lambda _: display_categories(page),width=265, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))),
                    ElevatedButton("Display Books by Category", on_click=lambda _: display_books_by_category(page),width=265, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=18))),
                    ElevatedButton("Back to Main Menu", on_click=lambda _: page.go("/"),width=265, height=50,style=ft.ButtonStyle(text_style=ft.TextStyle(size=20)))
                ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def remove_member_from_list(page, member_id):
        cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
        db.commit()
        if cursor.rowcount > 0:
            show_dialog(page, "Success", f"Member with ID {member_id} has been removed successfully.")
        else:
            show_dialog(page, "Error", "Member not found.")
        page.go("/members")

    def members_view(page: Page):
        cursor.execute("SELECT * FROM members ORDER BY id")
        members = cursor.fetchall()

        members_table = DataTable(
            columns=[
                DataColumn(Text("ID")),
                DataColumn(Text("Name")),
                DataColumn(Text("Department")),
                DataColumn(Text("Phone")),
                DataColumn(Text("Available Cards")),
                DataColumn(Text("Issued Books")),
                DataColumn(Text("Actions")),
            ],
            rows=[],
        )
        
        for member in members:
            members_table.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(str(member["id"]))),
                        DataCell(Text(member["name"])),
                        DataCell(Text(member["department"])),
                        DataCell(Text(member["phone"])),
                        DataCell(Text(str(member["available_cards"]))),
                        DataCell(Text(str(member["issued_books"]))),
                        DataCell(
                            Row(
                                [
                                    ElevatedButton(
                                        "View Details",
                                        on_click=lambda _, m=member: show_member_details(page, m),
                                    ),
                                    ElevatedButton(
                                        "Remove",
                                        on_click=lambda _, m=member: remove_member_from_list(page, m["id"]),
                                        style=ft.ButtonStyle(
                                            color={"": ft.colors.ERROR},
                                        ),
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )
        return View(
            "/members",
            [
                AppBar(
                    title=Text("All Members"),
                    bgcolor="#AFB3FF",
                    leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/admin")),
                ),
                ft.ListView(
                    [
                        Container(
                            content=members_table,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=10,
                            padding=10,
                        )
                    ],
                    expand=True,
                    auto_scroll=False,
                ),
            ],
        )

    def books_view(page: Page):
        cursor.execute("SELECT * FROM books ORDER BY id")
        books = cursor.fetchall()

        books_table = DataTable(
            columns=[
                DataColumn(Text("ID")),
                DataColumn(Text("Name")),
                DataColumn(Text("Author")),
                DataColumn(Text("Status")),
                DataColumn(Text("Category")),
                DataColumn(Text("Actions")),
            ],
            rows=[],
        )

        for book in books:
            books_table.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(str(book["id"]))),
                        DataCell(Text(book["name"])),
                        DataCell(Text(book["author"])),
                        DataCell(Text(book["status"])),
                        DataCell(Text(book["category"])),
                        DataCell(
                            Row(
                                [
                                    ElevatedButton(
                                        "View Details",
                                        on_click=lambda _, b=book: show_book_details(page, b),
                                    ),
                                    ElevatedButton(
                                        "Remove",
                                        on_click=lambda _, b=book: remove_book_from_list(page, b["id"]),
                                        style=ft.ButtonStyle(color={"": ft.colors.ERROR}),
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )

        return View(
            "/books",
            [
                AppBar(
                    title=Text("All Books"),
                    bgcolor="#AFB3FF",
                    leading=IconButton(icon=icons.ARROW_BACK, on_click=lambda _: page.go("/admin")),
                ),
                ft.ListView(
                    [
                        Container(
                            content=books_table,
                            padding=10,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=10,
                        ) 
                ],
                expand=True,
                auto_scroll=False,
                ),  
            ],
        )

    def remove_book_from_list(page, book_id):
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        db.commit()
        if cursor.rowcount > 0:
            show_dialog(page, "Success", f"Book with ID {book_id} has been removed successfully.")
        else:
            show_dialog(page, "Error", "Book not found.")
        page.go("/books")

    def show_member_details(page: Page, member):
        cursor.execute("SELECT * FROM books WHERE issued_to = %s", (member["id"],))
        issued_books = cursor.fetchall()
        
        details = Column(
            controls=[
                Text(f"Member: {member['name']}", size=16, weight=ft.FontWeight.BOLD),
                Text(f"Department: {member['department']}"),
                Text(f"Phone: {member['phone']}"),
                Text("Issued Books:", size=16, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        )

        for book in issued_books:
            issue_date = book['issue_date']
            fine = calculate_fine(issue_date)
            
            book_details = Column(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Text(f"Book: {book['name']} (ID: {book['id']})"),
                                Text(f"Issue Date: {issue_date.strftime('%Y-%m-%d')}"),
                                Text(f"Fine: ₹{fine}", color="red" if fine > 0 else "black"),
                            ],
                            spacing=5,
                        ),
                        border=border.all(1, ft.colors.GREY_400),
                        border_radius=8,
                        padding=10,
                    ),
                ],
                spacing=10,
            )
            
            if fine > 0:
                upi_id = "ddumka102@okhdfcbank"
                qr_code = generate_qr_code(upi_id, fine)
                book_details.controls.extend([
                    Image(
                        src_base64=qr_code,
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    Text(
                        f"Scan this QR code to pay ₹{fine} fine",
                        size=14,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    Text(
                        f"UPI ID: {upi_id}",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ])
            details.controls.append(book_details)

        show_dialog(page, "Member Details", details)

    def show_book_details(page: Page, book):
        details = ft.Column([
            ft.Text(f"Book ID: {book['id']}", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"Name: {book['name']}", size=14),
            ft.Text(f"Author: {book['author']}", size=14),
            ft.Text(f"Status: {book['status']}", size=14),
            ft.Text(f"Category: {book['category']}", size=14),
        ])

        if book['status'] == "Checked Out":
            cursor.execute("SELECT * FROM members WHERE id = %s", (book['issued_to'],))
            member = cursor.fetchone()
            if member:
                details.controls.extend([
                    Text("Issued To:", size=14, weight=ft.FontWeight.BOLD),
                    Text(f"Member Name: {member['name']}", size=14),
                    Text(f"Department: {member['department']}", size=14),
                    Text(f"Issue Date: {book['issue_date'].strftime('%Y-%m-%d')}", size=14),
                ])

        show_dialog(page, "Book Details", details)

    def add_book(page):
        def save_book(e):
            cursor.execute("INSERT INTO books (name, author, status, category) VALUES (%s, %s, %s, %s)",
                           (book_name_field.value, author_field.value, "Available", category_field.value))
            db.commit()
            show_dialog(page, "Success", "A New Book has been Added Successfully...")
            page.update()

        book_name_field = TextField(label="Book Name")
        author_field = TextField(label="Author")
        category_field = TextField(label="Category")

        show_dialog(page, "Add a New Book", Column([
            book_name_field,
            author_field,
            category_field,
            ElevatedButton("Save", on_click=save_book)
        ]))

    def remove_book(page):
        def perform_remove(e):
            cursor.execute("DELETE FROM books WHERE id = %s", (int(book_id_field.value),))
            db.commit()
            if cursor.rowcount > 0:
                show_dialog(page, "Success", f"Book with ID {book_id_field.value} has been removed successfully.")
            else:
                show_dialog(page, "Error", "Book not found.")
            page.update()

        book_id_field = TextField(label="Book ID")
        show_dialog(page, "Remove a Book", Column([
            book_id_field,
            ElevatedButton("Remove", on_click=perform_remove)
        ]))

    def add_member(page):
        def save_member(e):
            cursor.execute("INSERT INTO members (name, department, phone, available_cards, issued_books) VALUES (%s, %s, %s, %s, %s)",
                           (name_field.value, dept_field.value, phone_field.value, int(available_cards_field.value), 0))
            db.commit()
            show_dialog(page, "Success", "A New Member has been Added Successfully...")
            page.update()

        name_field = TextField(label="Name")
        dept_field = TextField(label="Department")
        phone_field = TextField(label="Phone Number")
        available_cards_field = TextField(label="Available Cards")

        show_dialog(page, "Add a New Member", Column([
            name_field,
            dept_field,
            phone_field,
            available_cards_field,
            ElevatedButton("Save", on_click=save_member)
        ]))

    def remove_member(page):
        def perform_remove(e):
            cursor.execute("DELETE FROM members WHERE id = %s", (int(member_id_field.value),))
            db.commit()
            if cursor.rowcount > 0:
                show_dialog(page, "Success", f"Member with ID {member_id_field.value} has been removed successfully.")
            else:
                show_dialog(page, "Error", "Member not found.")
            page.update()

        member_id_field = TextField(label="Member ID")
        show_dialog(page, "Remove a Member", Column([
            member_id_field,
            ElevatedButton("Remove", on_click=perform_remove)
        ]))

    def issue_book(page):
        def perform_issue(e):
            cursor.execute("SELECT * FROM books WHERE id = %s", (int(book_id_field.value),))
            book = cursor.fetchone()
            cursor.execute("SELECT * FROM members WHERE id = %s", (int(member_id_field.value),))
            member = cursor.fetchone()

            if not book:
                show_dialog(page, "Error", "Book not found.")
                return
            if not member:
                show_dialog(page, "Error", "Member not found.")
                return
            if book['status'] == "Checked Out":
                show_dialog(page, "Error", "Book is already issued.")
                return
            if member['available_cards'] <= 0:
                show_dialog(page, "Error", "Member has no available cards.")
                return

            cursor.execute("UPDATE books SET status = 'Checked Out', issued_to = %s, issue_date = %s WHERE id = %s",
                           (member['id'], datetime.now(), book['id']))
            cursor.execute("UPDATE members SET available_cards = available_cards - 1, issued_books = issued_books + 1 WHERE id = %s",
                           (member['id'],))
            db.commit()
            show_dialog(page, "Success", f"Book '{book['name']}' issued to {member['name']}.")
            page.update()

        book_id_field = TextField(label="Book ID")
        member_id_field = TextField(label="Member ID")

        show_dialog(page, "Issue a Book", Column([
            book_id_field,
            member_id_field,
            ElevatedButton("Issue", on_click=perform_issue)
        ]))

    def return_book(page):
        def perform_return(e):
            cursor.execute("SELECT * FROM books WHERE id = %s", (int(book_id_field.value),))
            book = cursor.fetchone()
            cursor.execute("SELECT * FROM members WHERE id = %s", (int(member_id_field.value),))
            member = cursor.fetchone()

            if not book:
                show_dialog(page, "Error", "Book not found.")
                return
            if not member:
                show_dialog(page, "Error", "Member not found.")
                return
            if book['status'] == "Available":
                show_dialog(page, "Error", "Book is not issued.")
                return

            fine = calculate_fine(book['issue_date'])
            if fine > 0:
                upi_id = "ddumka102@okhdfcbank"
                qr_code = generate_qr_code(upi_id, fine)
                fine_details = Column([
                    Text(f"Fine: ₹{fine}", color="red"),
                    Image(src_base64=qr_code, width=200, height=200),
                    Text(f"Scan this QR code to pay ₹{fine} fine", size=14, italic=True),
                    Text(f"UPI ID: {upi_id}", size=14)
                ])
                show_dialog(page, "Fine Payment", fine_details)

            cursor.execute("UPDATE books SET status = 'Available', issued_to = NULL, issue_date = NULL WHERE id = %s",
                           (book['id'],))
            cursor.execute("UPDATE members SET available_cards = available_cards + 1, issued_books = issued_books - 1 WHERE id = %s",
                           (member['id'],))
            db.commit()
            show_dialog(page, "Success", f"Book '{book['name']}' returned by {member['name']}.")
            page.update()

        book_id_field = TextField(label="Book ID")
        member_id_field = TextField(label="Member ID")

        show_dialog(page, "Return a Book", Column([
            book_id_field,
            member_id_field,
            ElevatedButton("Return", on_click=perform_return)
        ]))

    def check_member_status(page):
        def perform_check(e):
            cursor.execute("SELECT * FROM members WHERE id = %s", (int(member_id_field.value),))
            member = cursor.fetchone()

            if member:
                show_member_details(page, member)
            else:
                show_dialog(page, "Error", "Member not found.")

        member_id_field = TextField(label="Member ID")

        show_dialog(page, "Check Member Status", Column([
            member_id_field,
            ElevatedButton("Check", on_click=perform_check)
        ]))

    def search_book(page):
        def perform_search(e):
            book_name = search_field.value.lower()
            cursor.execute("SELECT * FROM books WHERE LOWER(name) LIKE %s", (f"%{book_name}%",))
            found_books = cursor.fetchall()
            
            if found_books:
                result = Column([Text("Search Results:")])
                for book in found_books:
                    book_info = Column([
                        Text(f"Book ID: {book['id']}"),
                        Text(f"Name: {book['name']}"),
                        Text(f"Author: {book['author']}"),
                        Text(f"Status: {book['status']}"),
                        Text(f"Category: {book['category']}"),
                        Text("")
                    ])
                    result.controls.append(book_info)
                show_dialog(page, "Search Results", Container(content=result, height=300))
            else:
                show_dialog(page, "Search Results", "Book Not Found!")

        search_field = TextField(label="Book Name")
        show_dialog(page, "Search a Book", Column([
            search_field,
            ElevatedButton("Search", on_click=perform_search)
        ]))

    def display_categories(page):
        cursor.execute("SELECT DISTINCT category FROM books")
        categories = [row['category'] for row in cursor.fetchall()]
        content = Column([Text("Book Categories:")])
        for category in categories:
            content.controls.append(Text(f"- {category}"))

        show_dialog(page, "Book Categories", content)

    def display_books_by_category(page):
        def show_books(e):
            category = category_dropdown.value
            cursor.execute("SELECT * FROM books WHERE category = %s", (category,))
            books_in_category = cursor.fetchall()
            
            books_table = DataTable(
                columns=[
                    DataColumn(Text("Book ID")),
                    DataColumn(Text("Name")),
                    DataColumn(Text("Author")),
                    DataColumn(Text("Status")),
                ],
                rows=[]
            )

            for book in books_in_category:
                books_table.rows.append(
                    DataRow(cells=[
                        DataCell(Text(str(book['id']))),
                        DataCell(Text(book['name'])),
                        DataCell(Text(book['author'])),
                        DataCell(Text(book['status'])),
                    ])
                )

            show_dialog(page, f"Books in {category}", Container(
                content=books_table,
                height=300,
                width=500,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
            ))

        cursor.execute("SELECT DISTINCT category FROM books")
        categories = [row['category'] for row in cursor.fetchall()]
        category_dropdown = dropdown.Dropdown(
            label="Select Category",
            options=[dropdown.Option(category) for category in categories],
            width=200
        )

        show_dialog(page, "Display Books by Category", Column([
            category_dropdown,
            ElevatedButton("Show Books", on_click=show_books)
        ]))

    def calculate_fine(issue_date):
        today = datetime.now()
        diff = today - issue_date
        if diff.days > 30:
            return (diff.days - 30) * 1  # $1 per day after 30 days
        return 0

    def generate_qr_code(upi_id, amount):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        upi_payment_string = f"upi://pay?pa={upi_id}&pn=Library%20Fine&am={amount}&cu=INR"
        qr.add_data(upi_payment_string)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route == "/admin-login":
            page.views.append(admin_login_view(page))
        elif page.route == "/user-login":
            page.views.append(user_login_view(page))
        elif page.route == "/user-signup":
            page.views.append(user_signup_view(page))
        elif page.route == "/admin":
            page.views.append(admin_view(page))
        elif page.route == "/user":
            page.views.append(user_view(page))
        elif page.route == "/members":
            page.views.append(members_view(page))
        elif page.route == "/books":
            page.views.append(books_view(page))
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

ft.app(target=main)