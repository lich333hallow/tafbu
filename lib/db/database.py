from sqlite3 import connect
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os.path import isfile

db_path = "./data/db/database.db"
db_build = "./data/db/build.sql"

connection = connect(db_path, check_same_thread=False)
cursor = connection.cursor()

def write_commit(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        commit()
    return wrapper

@write_commit
def build():
    if isfile(db_build):
        script_execute(db_build)

def commit():
    connection.commit()

def autosave(sched: AsyncIOScheduler):
    sched.add_job(commit, CronTrigger(second=30))

def close():
    connection.close()

def field(command, *values):
    cursor.execute(command, tuple(values))

    if (fetch := cursor.fetchone()) is not None:
        return fetch[0]

def record(command, *values):
    cursor.execute(command, tuple(values))
    return cursor.fetchone()

def records(command, *values):
    cursor.execute(command, tuple(values))
    return cursor.fetchall()

def column(command, *values):
    cursor.execute(command, tuple(values))
    return[item[0] for item in cursor.fetchall()]

def execute(command, *values):
    cursor.execute(command, tuple(values))

def multi_execute(command, valueset):
    cursor.executemany(command, valueset)

def script_execute(path):
    with open(path, "r", encoding="UTF-8") as script:
        cursor.executescript(script.read())
