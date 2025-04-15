import requests
import base64
import time
import logging
from typing import Optional, Dict, Any, List
import jwt
logger = logging.getLogger(__name__)
def refresh_spotify_token(client_id: str, client_secret: str, refresh_token: str) -> Optional[Dict[str, Any]]:
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Fehler beim Aktualisieren des Spotify-Tokens: {e}")
        return None
    except ValueError: 
        logger.error(f"Fehler beim Parsen der Spotify-Token-Antwort: Ungültiges JSON. Antworttext: {response.text}")
        return None
def get_currently_playing_song(access_token: str) -> Optional[Dict[str, Any]]:
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:  
            return response.json()
        elif response.status_code == 204:  
            return None
        else:
            logger.warning(f"Unerwarteter Statuscode von Spotify: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Fehler beim Abrufen des aktuell abgespielten Songs: {e}")
        return False
    except ValueError: 
        logger.error(f"Fehler beim Parsen der Spotify-Song-Antwort: Ungültiges JSON. Antworttext: {response.text}")
        return False
def create_jwt(payload: Dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)
def verify_jwt(token: str, secret: str, audience: Optional[List[str]] = None, required_claims: Optional[List[str]] = None) -> Dict[str, Any]:
    try:
        options = {}
        if audience:
            options['audience'] = audience
        if required_claims:
            options['require'] = required_claims
        return jwt.decode(token, secret, algorithms=["HS256"], options=options)
    except jwt.ExpiredSignatureError:
        raise ValueError("JWT ist abgelaufen.")
    except jwt.InvalidAudienceError:
        raise ValueError("JWT hat ungültige Audience.")
    except jwt.MissingRequiredClaimError as e:
        raise ValueError(f"JWT fehlt erforderlicher Claim: {e}")
    except jwt.InvalidSignatureError:
        raise ValueError("JWT hat ungültige Signatur.")
    except jwt.DecodeError:
        raise ValueError("JWT konnte nicht dekodiert werden.")
    except Exception as e:
        raise ValueError(f"Ungültiger JWT: {e}")