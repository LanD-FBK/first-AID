import logging
import os
import secrets
import subprocess

from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, Session

from config.defaults import ConfigDefault
from sql.crud import create_user
from sql.database import engine
from sql.dboptions import getOption, saveOption
from sql.models import User, UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_middleware():
    useMiddleware = getOption("USE_MIDDLEWARE", ret_type=int)

    if not useMiddleware:
        logger.info("Not using middleware")
        return None

    logger.info("Loading middleware")
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=['access-control-allow-origin'],
        )
    ]
    return middleware


def app_init():
    for key in dir(ConfigDefault):
        if not key.startswith("__"):
            saveOption(key, getattr(ConfigDefault, key))

    ### Create files folder
    files_folder = getOption("SAVE_PATH")
    if not os.path.exists(files_folder):
        logger.info(f"Folder {files_folder} does not exist, creating it")
        try:
            os.makedirs(files_folder)
        except Exception as e:
            logger.error(f"Critical error, fix and restart ({e})")
            exit()
    else:
        if not os.path.isdir(files_folder):
            logger.error(f"Critical error, {files_folder} is not a folder")
            exit()

    ### Check SECRET_KEY
    secret_key = getOption("SECRET_KEY")
    if not secret_key:
        logger.info("Secret key not found, creating it")
        try:
            run_sk = subprocess.run(["openssl", "rand", "-hex", "32"], capture_output=True)
            secret_key = run_sk.stdout.decode().strip()
        except Exception as e:
            logger.error(f"Critical error, fix and restart ({e})")
            exit()

        saveOption("SECRET_KEY", secret_key)

    ### Load/create admin user
    admin_username = getOption("ADMIN_USER")
    admin_email = getOption("ADMIN_EMAIL")
    with Session(engine) as db:
        stmt = select(User).where(User.username == admin_username)
        f = db.exec(stmt).first()
        if not f:
            pw = getOption("ADMIN_DEFAULT_PASSWORD")
            if not pw:
                pw = secrets.token_urlsafe(getOption("PASSWORD_LENGTH", ret_type=int))
            admin_user = UserCreate(
                username=admin_username,
                email=admin_email,
                password=pw
            )
            user_info = create_user(db, admin_user, is_admin=True)
            logger.info(f"User ** {admin_username} ** not found, created with password ** {pw} **")
