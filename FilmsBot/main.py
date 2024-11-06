# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication
import sys
import json
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

class Users:
    def __init__(self, chatID, favourite, dateReg):
        self.chatID_T = chatID
        self.favouriteT = favourite
        self.dateRegT = dateReg

list_users = []

def appendUser(id, favour, dateRegs):
    list_users.append(Users(id, favour, dateRegs))

def existUser(id):
    for us in list_users:
        if us.chatID_T == id:
            return True
    return False

def saveBase(id, genres, dateReg):
    with open("base.xml", "a", encoding="utf-8") as file:
        file.write(f"<user><id>{id}</id><genres>{genres}</genres><dateReg>{dateReg}</dateReg></user>\n")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not existUser(chat_id):
        reply_keyboard = [["Выбрать любимую категорию"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        await update.message.reply_text("Привет! Это первый запуск бота вами. Выберите действие:", reply_markup=markup)

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not existUser(update.message.chat_id) and update.message.text == "Выбрать любимую категорию":
        # Создаем inline-кнопки с жанрами
        genres = [
            [InlineKeyboardButton("Комедия ❌", callback_data="Комедия")],
            [InlineKeyboardButton("Драма ❌", callback_data="Драма")],
            [InlineKeyboardButton("Боевик ❌", callback_data="Боевик")],
            [InlineKeyboardButton("Хоррор ❌", callback_data="Хоррор")],
            [InlineKeyboardButton("Подтвердить", callback_data="Подтвердить")]
        ]
        reply_markup = InlineKeyboardMarkup(genres)

        await update.message.reply_text(
            "Выберите категории, затем нажмите Подтвердить:",
            reply_markup=reply_markup
        )

# Обработчик нажатий на инлайн-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение запроса

    selected_genres = context.user_data.get("selected_genres", set())

    if query.data == "Подтвердить":
        chat_id = query.message.chat_id
        date_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        genres_str = ", ".join(selected_genres)
        appendUser(chat_id, list(selected_genres), date_reg)
        saveBase(chat_id, genres_str, date_reg)
        await query.edit_message_text(text=f"Вы выбрали категории: {genres_str}")
    else:
        genre = query.data
        if genre in selected_genres:
            selected_genres.remove(genre)
        else:
            selected_genres.add(genre)
        context.user_data["selected_genres"] = selected_genres

        # Обновляем кнопки с отметками
        genres = [
            [InlineKeyboardButton(f"Комедия {'✅' if 'Комедия' in selected_genres else '❌'}", callback_data="Комедия")],
            [InlineKeyboardButton(f"Драма {'✅' if 'Драма' in selected_genres else '❌'}", callback_data="Драма")],
            [InlineKeyboardButton(f"Боевик {'✅' if 'Боевик' in selected_genres else '❌'}", callback_data="Боевик")],
            [InlineKeyboardButton(f"Хоррор {'✅' if 'Хоррор' in selected_genres else '❌'}", callback_data="Хоррор")],
            [InlineKeyboardButton("Подтвердить", callback_data="Подтвердить")]
        ]
        reply_markup = InlineKeyboardMarkup(genres)

        await query.edit_message_text(
            text="Выберите категории, затем нажмите Подтвердить:",
            reply_markup=reply_markup
        )

def main():
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("7697543985:AAGCbwWWgBCOnwFajiFMqyyr7n0Psc8Sxk8").build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
