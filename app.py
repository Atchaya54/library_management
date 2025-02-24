from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector

app = Flask(__name__, static_folder='static')
 

# Database Connection Function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="library"
        )
        return connection
    except mysql.connector.Error as err:
        print("Database Connection Error:", err)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books', methods=['GET', 'POST'])
def books():
    db = get_db_connection()
    if not db:
        return "Database connection failed", 500

    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        stock = request.form['stock']

        try:
            cursor.execute("INSERT INTO books (title, author, stock) VALUES (%s, %s, %s)", 
                           (title, author, stock))
            db.commit()
            flash("Book added successfully!", "success")
        except mysql.connector.Error as e:
            flash(f"Database Error: {e}", "danger")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('books'))
    
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('add_book.html', books=books)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    db = get_db_connection()
    if not db:
        return "Database connection failed", 500

    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        db.commit()
        flash("Book deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Database Error: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('books'))

@app.route('/members', methods=['GET', 'POST'])
def members():
    db = get_db_connection()
    if not db:
        return "Database connection failed", 500

    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        try:
            cursor.execute("INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))
            db.commit()
            flash("Member added successfully!", "success")
        except mysql.connector.Error as e:
            flash(f"Database Error: {e}", "danger")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('members'))

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('members.html', members=members)

@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    db = get_db_connection()
    if not db:
        return "Database connection failed", 500

    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
        db.commit()
        flash("Member deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Database Error: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('members'))

@app.route('/issue_book', methods=['POST'])
def issue_book():
    db = get_db_connection()
    cursor = db.cursor()
    member_id = request.form['member_id']
    book_id = request.form['book_id']
    issue_date = datetime.today().strftime('%Y-%m-%d')

    try:
       
        cursor.execute("SELECT stock FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        if book and book[0] > 0:
            
            cursor.execute("SELECT SUM(rent_fee) FROM transactions WHERE member_id = %s AND return_date IS NOT NULL", (member_id,))
            total_debt = cursor.fetchone()[0] or 0

            if total_debt > 500:
                flash("Member has outstanding debt over Rs.500. Cannot issue book!", "danger")
                return redirect(url_for('transactions'))

            
            cursor.execute("INSERT INTO transactions (member_id, book_id, issue_date) VALUES (%s, %s, %s)", 
                           (member_id, book_id, issue_date))
            cursor.execute("UPDATE books SET stock = stock - 1 WHERE id = %s", (book_id,))
            db.commit()
            flash("Book issued successfully!", "success")
        else:
            flash("Book is out of stock!", "danger")

    except mysql.connector.Error as e:
        flash(f"Database Error: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('transactions.html',transactions=transactions))

    


@app.route('/search_books', methods=['GET'])
def search_books():
    query = request.args.get('query', '').strip()

    if not query:
        flash("Please enter a search query!", "warning")
        return redirect(url_for('books'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM books 
        WHERE title LIKE %s OR author LIKE %s
    """, (f"%{query}%", f"%{query}%"))
    
    books = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('books.html', books=books, search_query=query)


if __name__ == '__main__':
    app.run(debug=True)
