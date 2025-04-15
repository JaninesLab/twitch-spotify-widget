from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import dateutil.parser
db = SQLAlchemy()
class Streamer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    broadcaster_id = db.Column(db.String, unique=True, nullable=False)
    spotify_refresh_token = db.Column(db.String, nullable=True) 
    spotify_access_token = db.Column(db.String, nullable=True)
    spotify_token_expires_at = db.Column(db.DateTime, nullable=True)
    twitch_panel_data = db.Column(JSONB, nullable=True)
    def __repr__(self):
        return f"<Streamer {self.broadcaster_id}>"
    def set_spotify_token(self, token_data: dict):
        self.spotify_access_token = token_data['access_token']
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'] - 60) 
        self.spotify_token_expires_at = expires_at
        if 'refresh_token' in token_data:  
            self.spotify_refresh_token = token_data['refresh_token']
    def is_spotify_token_expired(self) -> bool:
        if self.spotify_token_expires_at is None:
            return True  
        return datetime.now(timezone.utc) > self.spotify_token_expires_at