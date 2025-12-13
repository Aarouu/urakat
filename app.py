import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import db
import config
import items
import re
import users

app = Flask(__name__)
app.secret_key = config.secret_key

USERNAME_RE = re.compile(r"^[A-Za-z0-9_-]{3,30}$")

@app.route("/", methods=["GET", "POST"])
def index():
    search_query = request.form.get("search_query", "") if request.method == "POST" else ""
    all_items = items.get_items(search_query)
    return render_template("index.html", items=all_items, search_query=search_query)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        return "VIRHE: Käyttäjää ei löydy"
    user_items = users.get_items(user_id)
    # Debug
    print("DEBUG user:", dict(user))
    print("DEBUG user_items sample:", [dict(r) for r in user_items[:3]])
    return render_template("show_user.html", user=user, items=user_items)


@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        return "VIRHE: Ilmoitusta ei löydy"
    classes = items.get_classes(item_id)
    # Optional debug
    print("DEBUG classes:", [dict(r) for r in classes])
    return render_template("show_item.html", item=item, classes=classes)


@app.route("/new_item")
def new_item():
    # Require login to create item
    if "user_id" not in session:
        flash("Kirjaudu sisään luodaksesi ilmoituksen.")
        return redirect("/login")
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    start_price_raw = request.form.get("start_price", "").strip()

    # Otsikon validointi
    if not title:
        flash("Otsikko ei voi olla tyhjä.")
        return redirect("/new_item")
    if len(title) > 50:
        flash("Otsikon maksimipituus on 50 merkkiä.")
        return redirect("/new_item")

    # Kuvauksen validointi
    if len(description) > 2000:
        flash("Kuvauksen maksimipituus on 2000 merkkiä.")
        return redirect("/new_item")

    # Lähtöhinnan validointi
    if len(start_price_raw) > 10:  # estää liian pitkät luvut
        flash("Luvun tulee olla pienempi kuin 1000000000.")
        return redirect("/new_item")
    if not start_price_raw.isdigit():
        flash("Lähtöhinnan tulee olla kokonaisluku ≥ 0.")
        return redirect("/new_item")

    start_price = int(start_price_raw)
    if start_price > 1_000_000_000:
        flash("Luvun tulee olla pienempi kuin 1000000000.")
        return redirect("/new_item")
    
    classes = []
    category = request.form["category"]
    if category:
        classes.append(("Kategoria", category))
    
    # Tallennus
    items.add_item(title, description, start_price, session["user_id"], classes)
    return redirect("/")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")

    # Server-side validation
    if not username:
        flash("Käyttäjänimi ei voi olla tyhjä.")
        return redirect("/register")
    if not USERNAME_RE.match(username):
        flash("Käyttäjänimi: 3–30 merkkiä; kirjaimet ja numerot sallittu.")
        return redirect("/register")
    if not password1 or not password2:
        flash("Salasana ei voi olla tyhjä.")
        return redirect("/register")
    if len(password1) < 8:
        flash("Salasanan pituus vähintään 8 merkkiä.")
        return redirect("/register")
    if password1 != password2:
        flash("Salasanat eivät täsmää.")
        return redirect("/register")

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu. Kirjaudu sisään.")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Server-side validation
    if not username or not password:
        flash("Anna käyttäjätunnus ja salasana.")
        return redirect("/login")

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    rows = db.query(sql, [username])

    if not rows:
        flash("VIRHE: väärä tunnus tai salasana")
        return redirect("/login")

    result = rows[0]
    user_id = result["id"]
    password_hash = result["password_hash"]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    else:
        flash("VIRHE: väärä tunnus tai salasana")
        return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        session.pop("user_id", None)
        session.pop("username", None)
    return redirect("/")

@app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    item = items.get_item(item_id)
    if not item:
        return "VIRHE: Ilmoitusta ei löydy"

    if item["user_id"] != session["user_id"]:
        return "VIRHE: Sinulla ei ole oikeuksia muokata tätä ilmoitusta"

    if request.method == "POST":
        new_title = request.form.get("title", "").strip()
        new_description = request.form.get("description", "").strip()
        new_price_raw = request.form.get("start_price", "").strip()

        # Otsikon validointi
        if not new_title:
            flash("Otsikko ei voi olla tyhjä.")
            return redirect(f"/item/{item_id}/edit")
        if len(new_title) > 100:
            flash("Otsikon maksimipituus on 100 merkkiä.")
            return redirect(f"/item/{item_id}/edit")

        # Kuvauksen validointi
        if len(new_description) > 2000:
            flash("Kuvauksen maksimipituus on 2000 merkkiä.")
            return redirect(f"/item/{item_id}/edit")

        # Lähtöhinnan validointi
        if len(new_price_raw) > 10:  # estää liian pitkät luvut
            flash("Luvun tulee olla pienempi kuin 1000000000.")
            return redirect(f"/item/{item_id}/edit")
        if not new_price_raw.isdigit():
            flash("Lähtöhinnan tulee olla kokonaisluku ≥ 0.")
            return redirect(f"/item/{item_id}/edit")

        new_price = int(new_price_raw)
        if new_price > 1_000_000_000:
            flash("Luvun tulee olla pienempi kuin 1000000000.")
            return redirect(f"/item/{item_id}/edit")

        # Päivitä tietokantaan
        items.update_item(item_id, new_title, new_description, new_price)
        flash("Ilmoitus päivitetty onnistuneesti.")
        return redirect(f"/item/{item_id}")

    # GET-pyyntö: näytä editointilomake
    return render_template("edit_item.html", item=item)


@app.route("/item/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    item = items.get_item(item_id)
    if not item:
        flash("VIRHE: Ilmoitusta ei löydy")
        return redirect("/")

    if item["user_id"] != session["user_id"]:
        flash("VIRHE: Sinulla ei ole oikeuksia poistaa tätä ilmoitusta")
        return redirect(f"/item/{item_id}")

    items.delete_item(item_id)
    return redirect("/")
