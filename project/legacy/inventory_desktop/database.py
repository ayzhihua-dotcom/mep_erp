import sqlite3
from datetime import datetime
import hashlib

DB_NAME = "inventory.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            unit TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            supplier TEXT,
            note TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            customer TEXT,
            note TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocktake_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            actual_quantity INTEGER NOT NULL,
            system_quantity INTEGER NOT NULL,
            difference INTEGER NOT NULL,
            note TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS return_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            return_type TEXT NOT NULL,
            reason TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create default admin user
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.md5('admin123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('admin', password_hash, 'admin'))
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def add_user(username, password, role='user'):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND username!='admin'", (user_id,))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def search_products(keyword):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE code LIKE ? OR name LIKE ? OR category LIKE ?",
                  (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def add_product(code, name, category, unit, price, min_stock):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (code, name, category, unit, price, min_stock) VALUES (?, ?, ?, ?, ?, ?)",
                      (code, name, category, unit, price, min_stock))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_product(product_id, code, name, category, unit, price, min_stock):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET code=?, name=?, category=?, unit=?, price=?, min_stock=? WHERE id=?",
                  (code, name, category, unit, price, min_stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def add_inbound(product_id, quantity, price, supplier, note, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inbound_records (product_id, quantity, price, supplier, note, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (product_id, quantity, price, supplier, note, user_id))
    cursor.execute("UPDATE products SET stock = stock + ? WHERE id=?", (quantity, product_id))
    conn.commit()
    conn.close()

def add_outbound(product_id, quantity, price, customer, note, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
    stock = cursor.fetchone()[0]
    if stock < quantity:
        conn.close()
        return False
    cursor.execute("INSERT INTO outbound_records (product_id, quantity, price, customer, note, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (product_id, quantity, price, customer, note, user_id))
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, product_id))
    conn.commit()
    conn.close()
    return True

def get_inbound_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as product_name, u.username 
        FROM inbound_records i 
        JOIN products p ON i.product_id = p.id 
        JOIN users u ON i.user_id = u.id 
        ORDER BY i.created_at DESC
    """)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def get_outbound_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, p.name as product_name, u.username 
        FROM outbound_records o 
        JOIN products p ON o.product_id = p.id 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def add_stocktake(product_id, actual_quantity, system_quantity, note, user_id):
    conn = get_db()
    cursor = conn.cursor()
    difference = actual_quantity - system_quantity
    cursor.execute("INSERT INTO stocktake_records (product_id, actual_quantity, system_quantity, difference, note, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (product_id, actual_quantity, system_quantity, difference, note, user_id))
    cursor.execute("UPDATE products SET stock = ? WHERE id=?", (actual_quantity, product_id))
    conn.commit()
    conn.close()

def get_stocktake_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, p.name as product_name, u.username 
        FROM stocktake_records s 
        JOIN products p ON s.product_id = p.id 
        JOIN users u ON s.user_id = u.id 
        ORDER BY s.created_at DESC
    """)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def add_return(product_id, quantity, return_type, reason, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO return_records (product_id, quantity, return_type, reason, user_id) VALUES (?, ?, ?, ?, ?)",
                  (product_id, quantity, return_type, reason, user_id))
    if return_type == 'inbound':
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id=?", (quantity, product_id))
    else:
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, product_id))
    conn.commit()
    conn.close()

def get_return_records():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, p.name as product_name, u.username 
        FROM return_records r 
        JOIN products p ON r.product_id = p.id 
        JOIN users u ON r.user_id = u.id 
        ORDER BY r.created_at DESC
    """)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def get_report_data(start_date, end_date):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT i.*, p.name as product_name 
        FROM inbound_records i 
        JOIN products p ON i.product_id = p.id 
        WHERE i.created_at BETWEEN ? AND ?
        ORDER BY i.created_at DESC
    """, (start_date, end_date))
    inbound = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT o.*, p.name as product_name 
        FROM outbound_records o 
        JOIN products p ON o.product_id = p.id 
        WHERE o.created_at BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    """, (start_date, end_date))
    outbound = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return inbound, outbound

def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(price * stock) FROM products")
    total_value = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= min_stock")
    low_stock = cursor.fetchone()[0]
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM inbound_records WHERE date(created_at)=?", (today,))
    today_inbound = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM outbound_records WHERE date(created_at)=?", (today,))
    today_outbound = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_products': total_products,
        'total_value': total_value,
        'low_stock': low_stock,
        'today_inbound': today_inbound,
        'today_outbound': today_outbound
    }
