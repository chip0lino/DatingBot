import logging
import pymysql
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import mysql.connector

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token="6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# MySQL connection details
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "23database05"
MYSQL_DATABASE = "Local instance MySQL80"

# Establish MySQL connection
db = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

# Handler for a new user application
@dp.message_handler(commands=['apply'])
async def apply_handler(message: types.Message):
    # Prompt user for application details
    await message.answer("Please provide the following information:\n\n"
                         "Name:")
    await bot.register_next_step_handler(message, process_name_step)

async def process_name_step(message: types.Message):
    # Save user's name and prompt for gender
    user_data = {"name": message.text}
    await message.answer("Gender (M/F):")
    await bot.register_next_step_handler(message, process_gender_step, user_data)

async def process_gender_step(message: types.Message, user_data: dict):
    # Save user's gender and prompt for age
    user_data["gender"] = message.text
    await message.answer("Age:")
    await bot.register_next_step_handler(message, process_age_step, user_data)

async def process_age_step(message: types.Message, user_data: dict):
    # Save user's age and prompt for zodiac sign
    user_data["age"] = int(message.text)
    await message.answer("Zodiac sign:")
    await bot.register_next_step_handler(message, process_zodiac_step, user_data)

async def process_zodiac_step(message: types.Message, user_data: dict):
    # Save user's zodiac sign and prompt for faculty
    user_data["zodiac_sign"] = message.text
    await message.answer("Faculty:")
    await bot.register_next_step_handler(message, process_faculty_step, user_data)

async def process_faculty_step(message: types.Message, user_data: dict):
    # Save user's faculty and prompt for course
    user_data["faculty"] = message.text
    await message.answer("Course:")
    await bot.register_next_step_handler(message, process_course_step, user_data)

async def process_course_step(message: types.Message, user_data: dict):
    # Save user's course and insert application details into MySQL database
    user_data["course"] = message.text

    # Insert user's application details into MySQL database
    cursor = db.cursor()
    insert_query = "INSERT INTO questionnaires (name, gender, age, zodiac_sign, faculty, course) " \
                   "VALUES (%(name)s, %(gender)s, %(age)s, %(zodiac_sign)s, %(faculty)s, %(course)s)"
    cursor.execute(insert_query, user_data)
    db.commit()
    cursor.close()

    await message.answer("Your application has been submitted successfully!")

# Handler for searching questionnaires
@dp.message_handler(commands=['search'])
async def search_handler(message: types.Message):
    # Prompt user for search criteria
    await message.answer("Please provide the search criteria:\n\n"
                         "Gender (M/F):")
    await bot.register_next_step_handler(message, process_search_gender_step)

async def process_search_gender_step(message: types.Message):
    # Validate and save search gender and prompt for age
    search_gender = message.text.upper()
    if search_gender not in ['M', 'F']:
        await message.answer("Invalid gender. Please enter 'M' or 'F'.")
        return

    await message.answer("Minimum age:")
    await bot.register_next_step_handler(message, process_search_age_step, search_gender)

async def process_search_age_step(message: types.Message, search_gender: str):
    # Validate and save minimum age and prompt for maximum age
    try:
        min_age = int(message.text)
    except ValueError:
        await message.answer("Invalid age. Please enter a number.")
        return

    await message.answer("Maximum age:")
    await bot.register_next_step_handler(message, process_search_max_age_step, search_gender, min_age)

async def process_search_max_age_step(message: types.Message, search_gender: str, min_age: int):
    # Validate and save maximum age
    try:
        max_age = int(message.text)
    except ValueError:
        # Handle the exception here
        print("Invalid input for maximum age")
        return