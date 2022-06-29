from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Demo App - Graph Database"
    app_author: str = "Jay"

    env_loc = find_dotenv('.env')
    load_dotenv(env_loc)
