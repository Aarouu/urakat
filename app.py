import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import db
import config
import items

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods=["GET", "POST"])
def index():
    search_query = request.form.get("search_query", "") if request.method == "POST" else ""
    all_items = items.get_items(search_query)
    return render_template("index.html", items=all_items, search_query=search_query)


@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    print(f"Retrieved Item: {item}")  # Debugging line
    if not item:
        return "VIRHE: Ilmoitusta ei löydy"
    return render_template("show_item.html", item=item)



@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    title = request.form["title"]
    description = request.form["description"]
    start_price = request.form["start_price"]
    user_id = session["user_id"]

    items.add_item(title, description, start_price, user_id)

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")

@app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    # Check if user is logged in
    if "user_id" not in session:
        return redirect("/login")

    # Get the current item
    item = items.get_item(item_id)
    if not item:
        return "VIRHE: Ilmoitusta ei löydy"

    # Make sure the logged-in user is the owner
    user_id = session["user_id"]
    if item["username"] != session["username"]:
        return "VIRHE: Sinulla ei ole oikeuksia muokata tätä ilmoitusta"

    # If user submitted the form
    if request.method == "POST":
        new_title = request.form["title"]
        new_description = request.form["description"]
        new_price = request.form["start_price"]

        items.update_item(item_id, new_title, new_description, new_price)
        return redirect(f"/item/{item_id}")

    # Otherwise show the edit form
    return render_template("edit_item.html", item=item)

