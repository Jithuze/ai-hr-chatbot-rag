import sqlite3
from datetime import date, timedelta

# Create a connection and cursor
conn = sqlite3.connect('amazon_mobiles.db')
cursor = conn.cursor()

# Create the table with sample details
cursor.execute('''CREATE TABLE IF NOT EXISTS mobile_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mobile_name TEXT,
                    price REAL,
                    date DATE
                )''')

# List of sample mobile phones and their prices (these prices will vary on different days)
mobiles = [
    ("Samsung Galaxy S23", 899.99),
    ("iPhone 14 Pro", 1099.00),
    ("OnePlus 11", 749.99),
    ("Google Pixel 7 Pro", 899.00),
    ("Xiaomi 13 Pro", 699.99),
    ("Sony Xperia 1 V", 999.99),
    ("Oppo Find X6", 799.00),
    ("Vivo X90 Pro", 849.99),
    ("Motorola Edge 40", 699.00),
    ("Asus ROG Phone 7", 1099.99)
]

# Start date and end date for May 1 to May 15, 2024
start_date = date(2024, 5, 1)
end_date = date(2024, 5, 15)

# Insert price details for each mobile from May 1 to May 15, with varying prices
current_date = start_date
while current_date <= end_date:
    for mobile_name, base_price in mobiles:
        # Randomly fluctuate the price for the day by +/- 5%
        price_variation = base_price * (0.95 + (0.1 * (current_date.day % 5)) / 100)
        cursor.execute("INSERT INTO mobile_prices (mobile_name, price, date) VALUES (?, ?, ?)",
                       (mobile_name, round(price_variation, 2), current_date))
    current_date += timedelta(days=1)

# Commit and close the connection
conn.commit()
conn.close()

print("Data inserted successfully!")
