import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'a-default-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    TWITCH_EXTENSION_SECRET = os.environ.get("TWITCH_EXTENSION_SECRET")
    TWITCH_EXTENSION_CLIENT_ID = os.environ.get("TWITCH_EXTENSION_CLIENT_ID")
    REDIS_URL = os.environ.get("REDIS_URL")