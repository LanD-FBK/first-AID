### Custom default settings
# SECRET_KEY is created automatically if missing

#@arMQDSZFcvgh72

class ConfigDefault:
    PASSWORD_LENGTH: int = 13
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USER: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_DEFAULT_PASSWORD: str = "N8Lwcs4G7Vbmkp5t5g"
    USE_MIDDLEWARE: bool = True
    SAVE_PATH: str = "../files"
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = ""
