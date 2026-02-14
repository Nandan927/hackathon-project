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
            response = "You can plan a local 1-2 day trip nearby your city. Try hill stations or nearby beaches."
        elif budget < 10000:
            response = "We suggest a weekend trip to nearby cities like Jaipur, Rishikesh, or Udaipur."
        elif budget < 20000:
            response = "You can explore North India destinations like Manali, Shimla, or Darjeeling for 3-4 days."
        elif budget < 35000:
            response = "Consider Goa, Andaman Islands, or Kerala for a 4-5 day trip with comfortable stays."
        elif budget < 50000:
            response = "You can plan a longer domestic trip to places like Ladakh, Sikkim, or Rajasthan for 6-7 days."
        elif budget < 80000:
            response = "International options like Thailand, Bali, or Dubai for 5-6 days are possible."
        elif budget < 120000:
            response = "You can plan an international trip to Europe (like Switzerland, France) for 7-8 days."
        elif budget < 200000:
            response = "Consider a luxury international trip to countries like Japan, USA, or Australia for 8-10 days."
        else:
            response = "You can go on a premium world tour including multiple international destinations with luxury stays!"

    return render_template("chatbot.html", response=response)

@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    return redirect("/home")

@app.route("/clear_users")
def clear_users():
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")  # Delete all users
    conn.commit()
    conn.close()
    return "All users cleared! <a href='/home'>Back Home</a>"


if __name__ == "__main__":
    app.run(debug=True)
