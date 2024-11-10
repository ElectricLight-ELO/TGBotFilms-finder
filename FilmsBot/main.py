import xml.etree.ElementTree as ET
import ast
from datetime import datetime
import pandas as pd
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes


class Users:
    def __init__(self, chatID, favourite, dateReg):
        self.chatID_T = chatID
        self.favouriteT = favourite
        self.dateRegT = dateReg


list_users = []


def appendUser(id, favour, dateRegs):
    if not existUser(id):
        list_users.append(Users(id, favour, dateRegs))
    else:
        for us in list_users:
            if str(us.chatID_T) == str(id):
                us.favouriteT = favour


def existUser(id):
    for us in list_users:
        if str(us.chatID_T) == str(id):
            return True
    return False


def saveBase():
    try:
        with open("base.xml", "w", encoding="utf-8") as file:
            for user in list_users:
                genres_str = str(user.favouriteT)
                file.write(
                    f"<user><id>{user.chatID_T}</id><genres>{genres_str}</genres><dateReg>{user.dateRegT}</dateReg></user>\n")
        print("Данные успешно сохранены.")
    except FileNotFoundError:
        print("Ошибка сохранения данных. Файл не найден.")


def loadBase():
    try:
        with open("base.xml", "r", encoding="utf-8") as file:
            lines = file.readlines()
            print(f"Количество строк в файле: {len(lines)}")
        for line in lines:
            print(line)
            try:
                user_data = ET.fromstring(line)
                chatID = user_data.find("id").text
                genres_str = user_data.find("genres").text
                dateReg = user_data.find("dateReg").text
                genres = ast.literal_eval(genres_str)
                appendUser(chatID, genres, dateReg)
            except ET.ParseError:
                continue
        print("Данные успешно загружены.")
    except FileNotFoundError:
        print("Файл базы данных не найден!")


def load_movies_dataset():
    try:
        # Используем read_excel вместо read_csv для xlsx файлов
        return pd.read_csv('dataset_ru.csv')
    except Exception as e:
        print(f"Ошибка загрузки датасета: {e}")
        return None


def find_movies_by_genres(df, selected_genres, num_movies=5):
    matching_movies = []

    for _, movie in df.iterrows():
        genres_ru = str(movie['genres_ru']).split(', ')
        if any(genre in genres_ru for genre in selected_genres):
            matching_movies.append({
                'title': movie['title'],
                'rating': movie['rating'],
                'overview': movie['overview'],
                'genres_ru': movie['genres_ru']
            })

    if matching_movies:
        return random.sample(matching_movies, min(num_movies, len(matching_movies)))
    return []


def find_movies_by_favorite_genres(df, user_id, num_movies=5):
    for user in list_users:
        if str(user.chatID_T) == str(user_id):
            return find_movies_by_genres(df, user.favouriteT, num_movies)
    return []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not existUser(chat_id):
        reply_keyboard = [["Выбрать любимую категорию"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        await update.message.reply_text("Привет! Это первый запуск бота вами. Выберите действие:", reply_markup=markup)
    else:
        reply_keyboard2 = [["Подобрать фильм", "Подборка по избранным"], ["Выбрать любимую категорию"]]
        markup2 = ReplyKeyboardMarkup(reply_keyboard2, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=markup2)


def InlineButtonFavorGenres():
    genres_list = [
        "Комедия", "Драма", "Боевик", "Хоррор", "Мистика", "Научная фантастика",
        "Приключения", "Анимация", "Криминал", "Документальный", "Семейный", "Фэнтези",
        "История", "Музыка", "Романтика", "Телевизионный фильм", "Триллер", "Война", "Вестерн"
    ]
    genres_buttons = [[InlineKeyboardButton(f"{genre} ❌", callback_data=genre)] for genre in genres_list]
    genres_buttons.append([InlineKeyboardButton("Сохранить", callback_data="Сохранить")])

    reply_markup = InlineKeyboardMarkup(genres_buttons)
    return reply_markup


def InlineButtonChoiceGenres():
    genres_list = [
        "Комедия", "Драма", "Боевик", "Хоррор", "Мистика", "Научная фантастика",
        "Приключения", "Анимация", "Криминал", "Документальный", "Семейный", "Фэнтези",
        "История", "Музыка", "Романтика", "Телевизионный фильм", "Триллер", "Война", "Вестерн"
    ]
    genres_buttons = [[InlineKeyboardButton(f"{genre} ❌", callback_data=genre)] for genre in genres_list]
    genres_buttons.append([InlineKeyboardButton("Подтвердить", callback_data="Подтвердить")])

    reply_markup = InlineKeyboardMarkup(genres_buttons)
    return reply_markup


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Выбрать любимую категорию":
        await update.message.reply_text("Выберите категории для избранного, затем нажмите Сохранить",
                                        reply_markup=InlineButtonFavorGenres())

    elif update.message.text == "Подобрать фильм":
        await update.message.reply_text("Выберите категории, затем нажмите Подтвердить:",
                                        reply_markup=InlineButtonChoiceGenres())

    elif update.message.text == "Подборка по избранным":
        chat_id = update.message.chat_id
        df = load_movies_dataset()
        if df is not None:
            movies = find_movies_by_favorite_genres(df, chat_id)
            if movies:
                response = "Подборка фильмов по вашим любимым категориям:\n\n"
                for i, movie in enumerate(movies, 1):
                    response += f"{i}. {movie['title']}\n"
                    response += f"Рейтинг: {movie['rating']}\n"
                    response += f"Жанры: {movie['genres_ru']}\n"
                    response += f"Описание: {movie['overview'][:200]}...\n\n"
            else:
                response = "Не удалось найти фильмы по вашим любимым категориям. Попробуйте выбрать другие категории."
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Произошла ошибка при поиске фильмов")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_genres = context.user_data.get("selected_genres", set())

    if query.data == "Сохранить":
        chat_id = query.message.chat_id
        date_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        genres_str = ", ".join(selected_genres)

        appendUser(chat_id, list(selected_genres), date_reg)
        saveBase()
        await query.edit_message_reply_markup(reply_markup=None)

        reply_keyboard2 = [["Подобрать фильм", "Подборка по избранным"], ["Выбрать любимую категорию"]]
        markup2 = ReplyKeyboardMarkup(reply_keyboard2, resize_keyboard=True)

        await query.message.reply_text(f"Категории сохранены: {genres_str}", reply_markup=markup2)

    elif query.data == "Подтвердить":
        if not selected_genres:
            await query.message.reply_text("Пожалуйста, выберите хотя бы одну категорию")
            return

        df = load_movies_dataset()
        if df is not None:
            movies = find_movies_by_genres(df, selected_genres)

            if movies:
                response = "Вот подборка фильмов по выбранным категориям:\n\n"
                for i, movie in enumerate(movies, 1):
                    response += f"{i}. {movie['title']}\n"
                    response += f"Рейтинг: {movie['rating']}\n"
                    response += f"Жанры: {movie['genres_ru']}\n"
                    response += f"Описание: {movie['overview'][:200]}...\n\n"
            else:
                response = "К сожалению, не удалось найти фильмы по выбранным категориям"

            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(response)
        else:
            await query.message.reply_text("Произошла ошибка при поиске фильмов")

    else:
        genre = query.data
        if genre in selected_genres:
            selected_genres.remove(genre)
        else:
            selected_genres.add(genre)
        context.user_data["selected_genres"] = selected_genres

        genres_buttons = [
            [InlineKeyboardButton(f"{g} {'✅' if g in selected_genres else '❌'}", callback_data=g)]
            for g in [
                "Комедия", "Драма", "Боевик", "Хоррор", "Мистика", "Научная фантастика",
                "Приключения", "Анимация", "Криминал", "Документальный", "Семейный", "Фэнтези",
                "История", "Музыка", "Романтика", "Телевизионный фильм", "Триллер", "Война", "Вестерн"
            ]
        ]

        final_button = "Сохранить" if "Сохранить" in str(query.message.reply_markup) else "Подтвердить"
        genres_buttons.append([InlineKeyboardButton(final_button, callback_data=final_button)])

        reply_markup = InlineKeyboardMarkup(genres_buttons)

        await query.edit_message_text(
            text=f"Выберите категории, затем нажмите {final_button}:",
            reply_markup=reply_markup
        )


def main():
    loadBase()

    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("7697543985:AAGCbwWWgBCOnwFajiFMqyyr7n0Psc8Sxk8").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == "__main__":
    main()