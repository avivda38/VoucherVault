import sqlite3
import uuid
from datetime import datetime , timedelta, date
import csv
import os
from coupon import Coupon


DB_PATH = "voucher_vault.db"

# Define the explicit column order for coupon selection to match Coupon constructor
COUPON_COLUMNS_ORDERED = (
    "id", "user_id", "code", "business_name", "purchase_source", "discount", 
    "coupon_type", "code_type", "category", "description", "terms", "is_favorite", 
    "cvv", "expiry", "balance", "image_path", "is_redeemed", "is_deleted"
)
COUPON_COLUMNS_SELECT_STRING = ", ".join(COUPON_COLUMNS_ORDERED)

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS coupons (
            {COUPON_COLUMNS_ORDERED[0]} TEXT PRIMARY KEY,
            {COUPON_COLUMNS_ORDERED[1]} TEXT,
            {COUPON_COLUMNS_ORDERED[2]} TEXT,
            {COUPON_COLUMNS_ORDERED[3]} TEXT,
            {COUPON_COLUMNS_ORDERED[4]} TEXT,
            {COUPON_COLUMNS_ORDERED[5]} REAL,
            {COUPON_COLUMNS_ORDERED[6]} TEXT,
            {COUPON_COLUMNS_ORDERED[7]} TEXT,
            {COUPON_COLUMNS_ORDERED[8]} TEXT,
            {COUPON_COLUMNS_ORDERED[9]} TEXT,
            {COUPON_COLUMNS_ORDERED[10]} TEXT,
            {COUPON_COLUMNS_ORDERED[11]} INTEGER,
            {COUPON_COLUMNS_ORDERED[12]} TEXT,
            {COUPON_COLUMNS_ORDERED[13]} TEXT,
            {COUPON_COLUMNS_ORDERED[14]} REAL,
            {COUPON_COLUMNS_ORDERED[15]} TEXT,
            {COUPON_COLUMNS_ORDERED[16]} INTEGER DEFAULT 0,
            {COUPON_COLUMNS_ORDERED[17]} INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT,
            timestamp TEXT,
            details TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id TEXT PRIMARY KEY,
            alert_days INTEGER DEFAULT 14,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    try:
        cursor.execute("ALTER TABLE coupons ADD COLUMN is_deleted INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower(): # pragma: no cover

            pass
            if "duplicate column name" not in str(e).lower(): raise

    try:
        cursor.execute("ALTER TABLE coupons ADD COLUMN category TEXT")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            pass
            if "duplicate column name" not in str(e).lower(): raise

    conn.commit()
    conn.close()
create_tables()

# ---------- משתמשים ----------
def add_user(id, username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (id, username, password))
    cursor.execute("INSERT INTO settings (user_id, alert_days) VALUES (?, ?)", (id, 14))
    conn.commit()
    conn.close()
    return True

def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# ---------- שוברים ----------
def add_coupon(user_id, code, business_name, purchase_source, discount, coupon_type, code_type, category,
               description, terms, is_favorite, cvv, expiry, balance, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    coupon_id = str(uuid.uuid4())
    expiry_str = expiry.isoformat() if hasattr(expiry, "isoformat") else (str(expiry) if expiry else None)
    

    cursor.execute(f"""
        INSERT INTO coupons ({COUPON_COLUMNS_SELECT_STRING})
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        coupon_id, user_id, code, business_name, purchase_source, discount, coupon_type, code_type, category,
        description, terms, int(is_favorite), cvv, expiry_str, balance, image_path, 
        0, 0  # is_redeemed, is_deleted default to 0 on insert
    ))
    conn.commit()
    conn.close()
    return coupon_id

def get_user_coupons(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons WHERE user_id=? AND is_deleted=0", (user_id,))
    rows = cursor.fetchall()
    coupons = [Coupon(*row) for row in rows]
    conn.close()
    return coupons

def get_deleted_coupons(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons WHERE user_id=? AND is_deleted=1", (user_id,))
    rows = cursor.fetchall()
    coupons = [Coupon(*row) for row in rows]
    conn.close()
    return coupons

def soft_delete_coupon(coupon_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE coupons SET is_deleted=1 WHERE id=?", (coupon_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def restore_coupon(coupon_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE coupons SET is_deleted=0 WHERE id=?", (coupon_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def permanent_delete_coupon(coupon_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coupons WHERE id=?", (coupon_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_coupon(coupon_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coupons WHERE id=?", (coupon_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def update_coupon(coupon_id, updates):
    if not updates:
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fields = ", ".join([f"{k}=?" for k in updates.keys()])
    values = list(updates.values())
    values.append(coupon_id)
    cursor.execute(f"UPDATE coupons SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def search_coupons(user_id, query):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # For dict conversion
    cursor = conn.cursor()
    query_param = f"%{query}%"

    cursor.execute(f"""
        SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons 
        WHERE user_id=? AND is_deleted=0
        AND (business_name LIKE ? OR code LIKE ? OR description LIKE ? OR category LIKE ? OR coupon_type LIKE ?)
    """, (user_id, query_param, query_param, query_param, query_param, query_param))
    rows = cursor.fetchall()

    coupons = [dict(row) for row in rows]
    conn.close()
    return coupons

def toggle_favorite(user_id, coupon_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # קבל ערך נוכחי
    cursor.execute("SELECT is_favorite FROM coupons WHERE id=? AND user_id=?", (coupon_id, user_id))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return False
    new_fav = 0 if result[0] else 1
    cursor.execute("UPDATE coupons SET is_favorite=? WHERE id=? AND user_id=?", (new_fav, coupon_id, user_id))
    conn.commit()
    conn.close()
    return True

def get_favorite_coupons(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons WHERE user_id=? AND is_favorite=1 AND is_deleted=0", (user_id,))
    rows = cursor.fetchall()
    favs = [Coupon(*row) for row in rows]
    conn.close()
    return favs

def filter_and_sort_coupons(user_id, filters, sort_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() # No row_factory needed if direct tuple unpacking for Coupon(*row)
    base_query = f"SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons WHERE user_id=? AND is_deleted=0"
    params = [user_id]
    
    if filters:
        for key, val in filters.items():
            if val and val != "הכל":
                if key in COUPON_COLUMNS_ORDERED:
                    base_query += f" AND {key}=?"
                    params.append(val)
                else:
                    print(f"Warning: Invalid filter key ignored: {key}") # Or log
    
    if not sort_by or not all(part.strip().split()[0] in COUPON_COLUMNS_ORDERED for part in sort_by.split(',')):
        sort_by = "business_name ASC"
    
    base_query += f" ORDER BY {sort_by}"
    
    try:
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        filtered_coupons = [Coupon(*row) for row in rows]
    except sqlite3.OperationalError as e:
        print(f"Error during filtering/sorting coupons: {e}")
        filtered_coupons = []
    finally:
        conn.close()
        
    return filtered_coupons

def get_expiring_coupons(user_id, days=7):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    end_date = (now.replace(hour=23, minute=59, second=59) + timedelta(days=days)).isoformat()[:10]
    cursor.execute(f"""
        SELECT {COUPON_COLUMNS_SELECT_STRING} FROM coupons
        WHERE user_id=?
        AND expiry IS NOT NULL
        AND expiry <= ?
        AND is_redeemed=0 AND is_deleted=0
    """, (user_id, end_date))
    rows = cursor.fetchall()
    alerts = [Coupon(*row) for row in rows]
    conn.close()
    return alerts

# ---------- לוגים ----------
def add_log(user_id, action, details):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    log_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    cursor.execute("INSERT INTO logs (id, user_id, action, timestamp, details) VALUES (?, ?, ?, ?, ?)",
                   (log_id, user_id, action, timestamp, details))


    conn.commit()
    conn.close()
    return log_id

def get_user_logs(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")
    all_logs = cursor.fetchall()

    cursor.execute("SELECT * FROM logs WHERE user_id = ?", (user_id,))
    filtered = cursor.fetchall()

    conn.close()
    return {"status": "ok", "logs": filtered}




# ---------- ייצוא ----------
def export_coupons_to_csv(user_id):
    coupon_objects = get_user_coupons(user_id)
    if not coupon_objects:
        return None
    
    # Convert Coupon objects to list of dicts
    coupons_as_dicts = []
    for c_obj in coupon_objects:
        c_dict = c_obj.__dict__ # Get attributes as dict
        if isinstance(c_dict.get('expiry'), date): # Format date for CSV
            c_dict['expiry'] = c_dict['expiry'].isoformat()
        coupons_as_dicts.append(c_dict)

    if not coupons_as_dicts:
        return None

    filename = f"coupons_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COUPON_COLUMNS_ORDERED)
        writer.writeheader()
        writer.writerows(coupons_as_dicts)
    return os.path.abspath(filename)

try:
    import pandas as pd
    def export_coupons_to_excel(user_id):
        coupon_objects = get_user_coupons(user_id)
        if not coupon_objects:
            return None
        
        coupons_as_dicts = []
        for c_obj in coupon_objects:
            c_dict = c_obj.__dict__
            if isinstance(c_dict.get('expiry'), date):
                c_dict['expiry'] = c_dict['expiry'].isoformat()
            coupons_as_dicts.append(c_dict)

        if not coupons_as_dicts:
             return None

        filename = f"coupons_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        df = pd.DataFrame(coupons_as_dicts, columns=COUPON_COLUMNS_ORDERED) # Use ordered columns for DataFrame
        df.to_excel(filename, index=False)
        return os.path.abspath(filename)
except ImportError:
    def export_coupons_to_excel(user_id):
        return None




