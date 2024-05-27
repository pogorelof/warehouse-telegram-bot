import time
from db import *
import telebot
from telebot import types
from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn1 = types.KeyboardButton("Взять со склада")
	btn2 = types.KeyboardButton("Внести в склад")
	btn3 = types.KeyboardButton("Добавить новый товар")
	btn4 = types.KeyboardButton("Удалить товар полностью")
	btn5 = types.KeyboardButton("Добавить пользователя")
	btn6 = types.KeyboardButton("Удалить пользователя")
	btn7 = types.KeyboardButton("Поменять роль пользователя")
	btn8 = types.KeyboardButton("Склад")
	btn9 = types.KeyboardButton("История операций")

	user = message.from_user.username
	if not check_exists(user):
		bot.send_message(message.chat.id, "Вы не являетесь сотрудником!")
	elif check_admin_permission(user):
		markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8)
		bot.send_message(message.chat.id, "Ваша роль: админ", reply_markup=markup)
	else:
		markup.add(btn1,btn2,btn8)
		bot.send_message(message.chat.id, "Ваша роль: сотрудник", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu_button(message):
	if message.text == "Взять со склада":
		markup = make_categories_markup("take_category")
		bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)
	elif message.text == "Внести в склад":
		markup = make_categories_markup("put_category")
		bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)
	elif message.text == "Склад":
		text_for_reply = stock_info()
		bot.send_message(message.chat.id, text_for_reply, parse_mode="Markdown")
	elif message.text == "Добавить новый товар":
		markup = make_categories_markup("add_category")
		bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)
	elif message.text == "Удалить товар полностью":
		markup = make_categories_markup("delete_category")
		bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)
	elif message.text == "Добавить пользователя":
		sent_msg = bot.send_message(message.chat.id, "Введите id пользователя(без @):")
		bot.register_next_step_handler(sent_msg, process_add_user)
	elif message.text == "Удалить пользователя":
		markup = make_users_markup("delete_user", message.from_user.username)
		bot.send_message(message.chat.id, "Выберите пользователя:", reply_markup=markup)
	elif message.text == "Поменять роль пользователя":
		markup = make_users_markup("role_user", message.from_user.username)
		bot.send_message(message.chat.id, "Выберите пользователя:", reply_markup=markup)

# Add new item
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_category:'))
def handle_add_to_category(call):
	category_id = int(call.data.split(':')[1])
	sent_msg = bot.send_message(call.message.chat.id, "Введите название товара(укажите единицу измерения в скобках):")
	bot.register_next_step_handler(sent_msg, lambda msg: process_add_item(msg, category_id))
def process_add_item(message, category_id):
	item_name = message.text
	add_new_item(message.from_user.username, item_name, category_id)
	bot.send_message(message.chat.id, f"Вы добавили {item_name} в склад.")

# Delete item
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_category:'))
def handle_delete_to_category(call):
	category_id = int(call.data.split(':')[1])
	markup = make_items_markup("delete_item", category_id)
	bot.send_message(call.message.chat.id, "Выберите товар для удаления", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_item:'))
def process_delete_item(call):
	item_id = int(call.data.split(':')[1])
	delete_item(call.message.chat.username, item_id)
	bot.send_message(call.message.chat.id, f"Вы добавили удалили товар.")

# Add new user
def process_add_user(message):
	username = message.text
	create_user(message.from_user.username, username)
	bot.send_message(message.chat.id, f"Вы добавили {username} в систему.")

# Delete user
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_user:'))
def handle_delete_user(call):
	user_id = int(call.data.split(':')[1])
	delete_user(call.message.chat.username, user_id)
	bot.send_message(call.message.chat.id, f"Вы удалили пользователя")

# Change user role
@bot.callback_query_handler(func=lambda call: call.data.startswith('role_user:'))
def handle_change_user_role(call):
	user_id = int(call.data.split(':')[1])
	update_role_user(call.message.chat.username, user_id)
	bot.send_message(call.message.chat.id, f"Вы поменяли роль у пользователя")

# Take from stock
@bot.callback_query_handler(func=lambda call: call.data.startswith('take_category:'))
def handle_take_category(call):
	category_id = int(call.data.split(':')[1])
	markup = make_items_markup("take_item", category_id)
	bot.send_message(call.message.chat.id, "Выберите товар:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith('take_item:'))
def handle_take_item(call):
	item_id = int(call.data.split(':')[1])
	sent_msg = bot.send_message(call.message.chat.id, "Введите количество:")
	bot.register_next_step_handler(sent_msg, lambda msg: process_take_item_quantity(msg, item_id))
def process_take_item_quantity(message, item_id):
	if message.text.isdigit():
		count = int(message.text)
		if count_of_item(item_id) - count < 0:
			bot.send_message(message.chat.id, f"Не достаточно товара.")
		else:
			take_from_stock(message.from_user.username, item_id, count)
			bot.send_message(message.chat.id, f"Вы взяли {count} шт. товара.")
	else:
		bot.send_message(message.chat.id, f"Нужно ввести число, повторите операцию заново!")


# Put in stock
@bot.callback_query_handler(func=lambda call: call.data.startswith('put_category:'))
def handle_put_category(call):
	category_id = int(call.data.split(':')[1])
	markup = make_items_markup("put_item", category_id)
	bot.send_message(call.message.chat.id, "Выберите товар:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith('put_item:'))
def handle_put_item(call):
	item_id = int(call.data.split(':')[1])
	sent_msg = bot.send_message(call.message.chat.id, "Введите количество:")
	bot.register_next_step_handler(sent_msg, lambda msg: process_put_item_quantity(msg, item_id))
def process_put_item_quantity(message, item_id):
	if message.text.isdigit():
		count = int(message.text)
		put_in_stock(message.from_user.username, item_id, count)
		bot.send_message(message.chat.id, f"Вы внесли {count} шт. товара.")
	else:
		bot.send_message(message.chat.id, f"Нужно ввести число, повторите операцию заново!")


# Helpers
def make_items_markup(callback_id, category_id):
	items = take_items(category_id)
	markup = types.InlineKeyboardMarkup()
	for item_id, item_name, item_quantity, category_id in items:
		button_text = f"{item_name}: {item_quantity}"
		callback_data = f"{callback_id}:{item_id}"
		markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
	return markup

def make_users_markup(callback_id, id):
	users = take_users(id)
	markup = types.InlineKeyboardMarkup()
	for user_id, username, role in users:
		button_text = f"{username} ({role})"
		callback_data = f"{callback_id}:{user_id}"
		markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
	return markup

def make_categories_markup(callback_id):
	categories = take_categories()
	markup = types.InlineKeyboardMarkup()
	for id, name in categories:
		button_text = f"{name}"
		callback_data = f"{callback_id}:{id}"
		markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
	return markup

def stock_info():
	categories = take_categories()
	len_of_category = len(categories)
	text_for_reply = "*Данные о складе*\n"

	for i in range(1, len_of_category+1):
		items = take_items(i)
		text_for_reply += f"*\n{categories[i-1][1]}*\n"
		for item_id, item_name, item_quantity, category_id in items:
			text_for_reply += f"{item_name}: {item_quantity}\n"

	return text_for_reply


if __name__=='__main__':
	while True:
		try:
			bot.polling(non_stop=True, interval=0)
		except Exception as e:
			print(e)
			time.sleep(5)
			continue