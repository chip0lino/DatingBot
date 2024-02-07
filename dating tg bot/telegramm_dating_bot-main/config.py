from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = "6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M"
BOT_NAME = "GEUDATE"
BOT_ID = "6774580974"

LOG_PATH = "LOG_PATH"
LOG_NAME = "LOG_NAME"

DB_USER = "DB_USER"
DB_PASS = "DB_PASS"
DB_NAME = "DB_NAME"
DB_HOST = "DB_HOST"
# адрес для подключения к БД
POSTGRES_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# первый админ будет создатель бота, затем он добавит модераторов и админов.
# модераторам и админам не нужно проходить регистрацию - заполнять анкету
SUPER_ADMIN_USERNAME = "SUPER_ADMIN_USERNAME"
SUPER_ADMIN_ID = "SUPER_ADMIN_ID"
SUPER_ADMIN_STATUS = "SUPER_ADMIN_STATUS"

# количество карточек пользователей на одной странице
COUNT_USERS_CARDS_AT_PAGE = 5
# время в часах для временной блокировки пользователям
TIME_BANNED = 10
# время которое будут видны сообщения и после удалятся
time_sleep = 3
