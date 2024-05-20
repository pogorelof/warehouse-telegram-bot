import sqlite3
from dotenv import load_dotenv
import os


load_dotenv()

db_name = os.getenv("DB_NAME")

"""
Check admin persmission

Args:
tg_id: Verifiable user

Returns:
	Bool
"""
def check_admin_permission(tg_id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT role FROM user WHERE tg_id = ?", (tg_id,))
		return True if cursor.fetchone()[0] == "ADMIN" else False

"""
Check user existence

Args:
tg_id: Verifiable user

Returns:
	Bool
"""
def check_exists(tg_id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT id FROM user WHERE tg_id = ?", (tg_id,))
		return True if cursor.fetchone() != None else False


"""
Create user via admin

Args:
whois: Who is execute function(tg_id)
tg_id: Register tg_id

Returns:
	None
"""
def create_user(whois, tg_id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT id FROM user WHERE tg_id = ?", (tg_id,))
		if cursor.fetchone() != None:
			return

		if check_admin_permission(whois) and check_exists(tg_id) == False:
			cursor.execute("INSERT INTO user (tg_id, role) VALUES (?, 'EMPLOYEE')", (tg_id,))
			conn.commit()

"""
Delete user via admin

Args:
whois: Who is execute function(tg_id)
id: Id of user

Returns:
	None
"""
def delete_user(whois, id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		if check_admin_permission(whois):
			cursor.execute("DELETE FROM user WHERE id = ?", (id, ))
			conn.commit()

"""
Update role of user

Args:
whois: Who is execute function(tg_id)
tg_id: Update tg_id
role: Switch role to

Returns:
	None
"""
def update_role_user(whois, id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT role FROM user WHERE id = ?", (id, ))
		role = cursor.fetchone()[0]
		if role == "ADMIN":
			role = "EMPLOYEE"
		else:
			role = "ADMIN"

		if check_admin_permission(whois):
			cursor.execute("UPDATE user SET role = ? WHERE id = ?", (role, id))
			conn.commit()


"""
Add new item. Admin action

Args:
whois: Who is execute function(tg_id)
name: Name of item

Returns:
	None
"""
def add_new_item(whois, name):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		if check_admin_permission(whois):
			cursor.execute("INSERT INTO item(name, count) VALUES (?, 0)", (name,))
			conn.commit()

"""
Delete item. Admin action

Args:
whois: Who is execute function(tg_id)
name: Name of item
count: Initial value of count

Returns:
	None
"""
def delete_item(whois, id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		if check_admin_permission(whois):
			cursor.execute("DELETE FROM item WHERE id = ?", (id,))
			conn.commit()


"""
Take from stock.

Args:
whois: For log
id: Id of item
count: Count that was taken

Returns:
	None
"""
def take_from_stock(whois, id, count):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("UPDATE item SET count = count - ? WHERE id = ?", (count, id))
		conn.commit()

"""
Return count of item.

Args:
id: Id of item

Returns:
	Int
"""
def count_of_item(id):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT count FROM item WHERE id = ?", (id,))
		return cursor.fetchone()[0]
"""
Put in stock.

Args:
whois: For log
id: Id of item
count: Count that was put

Returns:
	None
"""
def put_in_stock(whois, id, count):
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("UPDATE item SET count = count + ? WHERE id = ?", (count, id))
		conn.commit()

"""
Take all items.

Args:
	None

Returns:
	Array
"""
def take_items(category_id):
	items = None
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM item WHERE category_id = ?", (category_id,))
		items = cursor.fetchall()
	return items

"""
Take all users.

Args:
	whois_id: Auth user

Returns:
	Array
"""
def take_users(whois):
	users = None
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM user WHERE tg_id != ?", (whois, ))
		users = cursor.fetchall()
	return users

"""
Take all categories.

Args:
	whois_id: Auth user

Returns:
	Array
"""
def take_categories():
	categories = None
	with sqlite3.connect(db_name) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM category")
		categories = cursor.fetchall()
	return categories


