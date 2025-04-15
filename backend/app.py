from flask import Flask, jsonify, request, abort
import requests
import os
import time
import json
import logging
import utils  
import db  
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple

load_dotenv()  
app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
TWITCH_EXTENSION_SECRET = os.environ.get("TWITCH_EXTENSION_SECRET")
TWITCH_EXTENSION_CLIENT_ID = os.environ.get("TWITCH_EXTENSION_CLIENT_ID")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db.init_db()

def get_access_token(broadcaster_id: str) -> Optional[str]:
    tokens = db.get_tokens(broadcaster_id)
    if tokens and tokens["access_token"] and tokens["expires_at"] > int(time.time()):
        logger.info(f"Using access token from database for {broadcaster_id}.")
        return tokens["access_token"]
    if tokens and tokens["refresh_token"]:
        logger.info(f"Refreshing access token for {broadcaster_id} using refresh token.")
        new_token_data = utils.refresh_spotify_token(
            SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, tokens["refresh_token"]
        )
        if new_token_data:
            expires_at = int(time.time()) + new_token_data["expires_in"] - 60  
            db.store_tokens(broadcaster_id, tokens["refresh_token"], new_token_data["access_token"], expires_at)
            logger.info(f"Access token for {broadcaster_id} refreshed and stored.")
            return new_token_data["access_token"]
        else:
            logger.warning(f"Token refresh failed for {broadcaster_id}.")
            return None
    else:
        logger.warning(f"No refresh token found for {broadcaster_id}.")
        return None

def create_ebs_jwt(broadcaster_id: str) -> str:
    payload = {
        "exp": int(time.time()) + 60,  
        "user_id": broadcaster_id,
        "role": "external",
        "channel_id": broadcaster_id,
    }
    return utils.create_jwt(payload, TWITCH_EXTENSION_SECRET)

def create_panel_jwt(broadcaster_id: str) -> str:
    payload = {
        "exp": int(time.time()) + 60,
        "user_id": broadcaster_id,
        "role": "broadcaster", 
        "channel_id": broadcaster_id,
    }
    return utils.create_jwt(payload, TWITCH_EXTENSION_SECRET)

def verify_ebs_request(request) -> Tuple[Optional[str], int]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, 401  
    token = auth_header.split(" ")[1]
    try:
        decoded = utils.verify_jwt(token, TWITCH_EXTENSION_SECRET, audience=[TWITCH_EXTENSION_CLIENT_ID], required_claims=['user_id', 'role', 'channel_id'])
        if decoded.get("role") != "external": 
            return None, 403 
        return decoded.get("channel_id"), 0
    except ValueError as e:
        logger.warning(f"Invalid EBS JWT: {e}")
        return None, 401 

@app.route("/currently-playing", methods=['GET'])
def currently_playing_get():
    broadcaster_id = request.args.get('broadcaster_id') 
    if not broadcaster_id:
        return jsonify({"error": "Missing broadcaster_id"}), 400
    access_token = get_access_token(broadcaster_id)
    if not access_token:
        return jsonify({"error": "Could not retrieve/refresh access token."}), 500
    song_data = utils.get_currently_playing_song(access_token)
    if song_data:
        formatted_data = {
            "title": song_data["item"]["name"],
            "artist": ", ".join([artist["name"] for artist in song_data["item"]["artists"]]),
            "cover_url": song_data["item"]["album"]["images"][0]["url"],
            "is_playing": song_data["is_playing"],
        }
        return jsonify(formatted_data)
    elif song_data is None:
        return jsonify({"is_playing": False}) 
    else:
         return jsonify({"error": "Could not fetch currently playing song."}), 500

@app.route("/currently-playing", methods=['POST'])
def currently_playing_post():
    broadcaster_id, error_code = verify_ebs_request(request)
    if error_code:
        return jsonify({"error": "EBS authentication failed"}), error_code
    try:
        data = request.get_json()
        if not data or "refresh_token" not in data:
            return jsonify({"error": "Invalid request: refresh_token missing"}), 400
        refresh_token = data["refresh_token"]
        db.store_tokens(broadcaster_id, refresh_token)
        return jsonify({"message": "Refresh token received and stored"}), 200
    except Exception as e:
        logger.error(f"Error processing EBS POST request: {e}")
        return jsonify({"error": "Internal server error"}), 500

def send_to_twitch_panel(broadcaster_id: str, data: Dict[str, Any]):
    try:
        twitch_api_url = f"https://api.twitch.tv/extensions/{TWITCH_EXTENSION_CLIENT_ID}/{broadcaster_id}/state"
