import db

def add_item(title, description, start_price, user_id):
    sql = """INSERT INTO items (title, description, start_price, user_id) 
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, start_price, user_id])

def get_items():
    # Return all items, newest first
    sql = "SELECT id, title FROM items ORDER BY id DESC"
    return db.query(sql)


def get_item(item_id):
    # Return a single item with the creator's username
    sql = """SELECT items.id,  -- Ensure you're selecting the id
                    items.title,
                    items.description,
                    items.start_price,
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

