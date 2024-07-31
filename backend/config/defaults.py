### Custom default settings
# SECRET_KEY is created automatically if missing

class ConfigDefault:
    PASSWORD_LENGTH = 13
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ADMIN_USER = "admin"
    ADMIN_EMAIL = "admin@localhost"
    ADMIN_DEFAULT_PASSWORD = "N8Lwcs4G7Vbmkp5t5g"
    USE_MIDDLEWARE = True
