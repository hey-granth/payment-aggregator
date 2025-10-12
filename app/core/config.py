from pydantic_settings import BaseSettings


# settings class to load env variables, like i used to make config.py file in django
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file: str = ".env"


settings = Settings()
# leaving parameter unfilled as it will automatically look for .env file in the root directory, and fetch the variables from there
