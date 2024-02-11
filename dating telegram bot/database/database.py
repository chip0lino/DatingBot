import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                    "user_id INTEGER PRIMARY KEY, " #0
                    "username TEXT, "
                    "nickname TEXT, " # 2ссылка на пользователя в телеге
                    "name TEXT, "
                    "gender TEXT, " #4
                    "age INTEGER, "
                    "photo TEXT, " #6
                    "anketa_description TEXT, "
                    "zodiac_sign TEXT, " #8
                    "kurs INTEGER, " # курс
                    "faculty TEXT, " # 10 факультет
                    "grade INTEGER, " # бакалавр или магистратура
                    "blocked TEXT)")  # new 
  

cursor.execute("CREATE TABLE IF NOT EXISTS like ("
                   "user_id INTEGER PRIMARY KEY, "
                   "last_ank_id INTEGER, " # айди человека чью анкету юзер смотрит, используется для отправки этому человеку лайка
                   "people_who_like TEXT, " # люди которые лайкнули юзера
                   "hidden TEXT)") # люди анкеты которых не показывать
conn.commit()

#выбирает случайную анкету, удовлетворяющую интересам пользователя
async def get_anket(user_id):
    gender = cursor.execute("SELECT gender FROM users WHERE user_id = {key}".format(key=user_id)).fetchone()[0]
    if gender=="male":
        desired = "female"
    elif gender=="female":
        desired = "male"
    hidden = cursor.execute("SELECT hidden FROM like WHERE user_id = {id}".format(id=user_id)).fetchall()[0][0]+',1' # колонка hidden в бд включает в себя id разделенные запятой, изначально там должен находиться id пользователя и любой второй id например: {user_id1},{user_id2} и так далее
    hidden = tuple(map(int, hidden.split(",")))
    ank = cursor.execute("SELECT * FROM users WHERE gender = (?) AND user_id NOT IN {hidden} ORDER BY RANDOM() LIMIT 1".format(hidden=hidden), (desired,)).fetchall() # выбор рандомной анкеты id которой не в hidden и которая противоположна по полу
    if len(ank)!=0:
        cursor.execute("UPDATE like SET last_ank_id = {people_id} WHERE user_id = {user_id}".format(user_id=user_id, people_id=ank[0][0])) # айди человека чью анкету юзер смотрит
        return ank[0]
    else:
        return 'no'

# если юзер пропустил анкету
async def do_not_show(id):
    hidden = cursor.execute("SELECT hidden, last_ank_id FROM like WHERE user_id={user_id}".format(user_id=id)).fetchall()[0]
    hidden = str(hidden[0])+','+str(hidden[1])
    cursor.execute("UPDATE like SET hidden = (?) WHERE user_id = {id}".format(id=id), (hidden, ))
    conn.commit()

# если юзер оценил анкету
async def like_ank(id):
    last_id = cursor.execute("SELECT last_ank_id FROM like WHERE user_id={key}".format(key=id)).fetchone()[0]
    who_like = cursor.execute("SELECT people_who_like FROM like WHERE user_id = {last_id}".format(last_id=last_id)).fetchone()[0]
    if len(str(who_like))==0 or who_like==None:
        peoples_like_me = str(id)
    else:
        peoples_like_me = str(who_like)+','+str(id)
    cursor.execute("UPDATE like SET people_who_like = (?) WHERE user_id = {last_ank_id}".format(last_ank_id=last_id), (peoples_like_me, )) #добавление в спиоск людей которые лайкнули человека юзера
    conn.commit()
    return last_id

#все люди которые лайкнули юзера
async def who_like(id):
    who_like = cursor.execute("SELECT people_who_like FROM like WHERE user_id = {id}".format(id=id)).fetchone()[0]
    if who_like==None or str(who_like)=="":
        return "no likes"
    else:
        return tuple(map(int, who_like.split(",")))

#анкета лайкнувшего человека
async def like_person(user_id):
    ank = cursor.execute("SELECT * FROM users WHERE user_id = {user_id}".format(user_id=user_id)).fetchall()[0]
    return ank

# удаляет оценку человека которого показал
async def delete_one_like(user_id):
    all_who_like = cursor.execute("SELECT people_who_like FROM like WHERE user_id = {user_id}".format(user_id=user_id)).fetchone()[0]
    delete_one_like = tuple(map(int, all_who_like.split(",")))
    if len(delete_one_like)>=2:
        deleted_one_like = str(delete_one_like[1])
        for i in range(1, len(delete_one_like)-1):
            deleted_one_like+=f",{delete_one_like[i]}"
        stop_or_continue = "cont"
    else:
        deleted_one_like = "NULL"
        stop_or_continue = "stop"
    cursor.execute("UPDATE like SET people_who_like = {delete_one_like} WHERE user_id = {user_id}".format(delete_one_like=deleted_one_like, user_id=user_id))
    conn.commit()
    return stop_or_continue