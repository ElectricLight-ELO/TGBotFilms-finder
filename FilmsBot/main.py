# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication
import sys
import json

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

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Выбрать любимую категорию"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=markup
    )

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Выбрать любимую категорию":
        # Создаем inline-кнопки с жанрами
        genres = [
            [InlineKeyboardButton("Комедия", callback_data="Комедия")],
            [InlineKeyboardButton("Драма", callback_data="Драма")],
            [InlineKeyboardButton("Боевик", callback_data="Боевик")],
            [InlineKeyboardButton("Хоррор", callback_data="Хоррор")],
        ]
        reply_markup = InlineKeyboardMarkup(genres)

        await update.message.reply_text(
            "Выберите категорию:",
            reply_markup=reply_markup
        )

# Обработчик нажатий на инлайн-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение запроса

    # Отправляем ответ о выборе жанра
    await query.edit_message_text(text=f"Вы выбрали жанр: {query.data}")

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
