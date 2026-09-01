import sqlite3

from streamlit import connection

DATABASE_NAME = "shopassist.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    create table if not exists customers (
    customer_id text primary_key,
    name text not null,
    email text not null
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        product TEXT NOT NULL,
        price TEXT NOT NULL,
        status TEXT NOT NULL,
        order_date TEXT NOT NULL,
        estimated_delivery TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    connection.commit()
    connection.close()


def insert_sample_data():
    connection = get_connection()
    cursor = connection.cursor()

    customers = [
        ("C001", "Ravi", "ravi@example.com"),
        ("C002", "Divya", "divya@example.com"),
        ("C003", "Amit", "amit@example.com"),
    ]

    orders = [
        ("ORD001", "C001", "Laptop",8999, "Shipped", "2023-08-01", "2023-08-05"),
        ("ORD002", "C002", "Mechanical Keyboard",4999, "Delivered", "2026-08-20", "2026-08-25"),
        ("ORD1003", "C002", "Smart Watch", 2999,"Processing","2026-08-31", "2026-09-04"),
        ("ORD1004", "C003", "USB-C Charger",1999, "Cancelled", "2026-08-28", None),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (customer_id, name, email)
        VALUES (?, ?, ?)
    """, customers)

    cursor.executemany("""
        INSERT OR IGNORE INTO orders
        (
            order_id,
            customer_id,
            product,
            price,
            status,
            order_date,
            estimated_delivery
        )
        VALUES (?, ?, ?, ?, ?, ?,?)
    """, orders)

    connection.commit()
    connection.close()


if __name__ == "__main__":

    create_tables()
    insert_sample_data()

    print("Database created successfully.")