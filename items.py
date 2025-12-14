import db

def add_item(title, description, start_price, user_id, classes):
    sql = """INSERT INTO items (title, description, start_price, user_id) 
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, start_price, user_id])

    item_id = db.last_insert_id()
    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def add_offer(item_id, user_id, price):
    sql = """INSERT INTO offers (item_id, user_id, price) 
             VALUES (?, ?, ?)"""
    db.execute(sql, [item_id, user_id, price])

def get_offers(item_id):
    sql = """
        SELECT o.id AS offer_id, o.price, u.id AS user_id, u.username
        FROM offers o
        JOIN users u ON o.user_id = u.id
        WHERE o.item_id = ?
        ORDER BY o.id DESC
    """
    return db.query(sql, [item_id])

def delete_offer(offer_id, user_id):
    # Poista vain jos tarjous kuuluu tälle käyttäjälle
    sql = "DELETE FROM offers WHERE id = ? AND user_id = ?"
    db.execute(sql, [offer_id, user_id])


def get_classes(item_id):
    sql = "SELECT title, value FROM item_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_best_price(item_id):
    # Palauta alin voimassa oleva tarjous, jos on, muuten None
    sql = "SELECT MIN(price) AS min_price FROM offers WHERE item_id = ?"
    rows = db.query(sql, [item_id])
    return rows[0]["min_price"] if rows and rows[0]["min_price"] is not None else None

def get_items(search_query=None):
    # Return all items, newest first, filtered by search query
    if search_query:
        sql = "SELECT id, title FROM items WHERE title LIKE ? ORDER BY id DESC"
        return db.query(sql, ['%' + search_query + '%'])
    else:
        sql = "SELECT id, title FROM items ORDER BY id DESC"
        return db.query(sql)



# items.py
def get_item(item_id):
    # Return a single item with the creator's username and user_id
    sql = """SELECT items.id,
                    items.title,
                    items.description,
                    items.start_price,
                    items.user_id,      -- add user_id for ownership checks
                    users.username
             FROM items
             JOIN users ON items.user_id = users.id
             WHERE items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None


def update_item(item_id, title, description, start_price):
    sql = """UPDATE items
             SET title = ?, description = ?, start_price = ?
             WHERE id = ?"""
    db.execute(sql, [title, description, start_price, item_id])

def delete_item(item_id):
    # Delete dependent rows first to satisfy FK constraints
    db.execute("DELETE FROM offers WHERE item_id = ?", [item_id])
    db.execute("DELETE FROM item_classes WHERE item_id = ?", [item_id])
    db.execute("DELETE FROM items WHERE id = ?", [item_id])

