from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        image TEXT,
        caption TEXT,
        budget TEXT,
        likes INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect("/home")

    return render_template("login.html")

@app.route("/home")
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY likes DESC")
    posts = cursor.fetchall()
    conn.close()

    return render_template("home.html", posts=posts)

@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        username = request.form["username"]
        caption = request.form["caption"]
        budget = request.form["budget"]
        image = request.files["image"]

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (username, image, caption, budget) VALUES (?, ?, ?, ?)",
                       (username, image.filename, caption, budget))
        conn.commit()
        conn.close()

        return redirect("/home")

    return render_template("add_post.html")

@app.route("/like/<int:post_id>")
def like(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

    return redirect("/home")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    response = ""
    if request.method == "POST":
        budget = int(request.form["budget"])

        if budget < 5000:
            response = "You can plan a local 2-day trip nearby."
        elif budget < 15000:
            response = "We suggest Goa or Manali for 3-4 days."
        else:
            response = "You can plan an international trip!"

    return render_template("chatbot.html", response=response)

@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    return redirect("/home")

if __name__ == "__main__":
    app.run(debug=True)
