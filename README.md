# Spotify Now Playing Twitch Extension 🎶

## ✨ Features

* Displays the currently playing song title, artist, and album cover from the broadcaster's Spotify.
* Links to the song on Spotify.
* Includes a song history (displays the last 5 played tracks).
* Secure configuration panel for the broadcaster to authorize Spotify access using OAuth2.
* "Disconnect" functionality for the broadcaster.
* Backend hosted on Railway for handling Spotify API interaction and token management.

## 💻 Tech Stack

* **Frontend (Twitch Extension):** HTML, CSS, JavaScript (jQuery)
* **Backend:** Python, Flask, Gunicorn
* **APIs:** Twitch API (Configuration Service, JWT Auth), Spotify API (OAuth2, Web Playback State)
* **Libraries:**
    * Python: `spotipy`, `requests`, `Flask-CORS`, `PyJWT`, `psycopg2-binary` (for PostgreSQL)
* **Hosting:** Railway (Backend + PostgreSQL Database)

## 🔧 Setup and Installation

Follow these steps to set up the extension for development or deployment.

**1. Prerequisites:**

* Git
* Python 3.9+ and Pip
* Twitch Developer Account
* Spotify Developer Account
* Railway Account (or other hosting provider)
* PostgreSQL Database (e.g., via Railway Addons)

**2. Spotify Application:**

* Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
* Create a new application.
* Note down your **Client ID** and **Client Secret**.
* Go to "Edit Settings".
* Add the following **Redirect URI** (replace `<your-railway-app-url>` with your actual Railway app URL, e.g., `https://seriousdots-now-playing.up.railway.app`):
    * `https://<your-railway-app-url>/spotify/auth_callback`
* Save the settings.

**3. Twitch Extension:**

* Go to the [Twitch Developer Console](https://dev.twitch.tv/console/extensions).
* Create a new extension.
    * **Name:** Choose a name (e.g., "My Spotify Widget").
    * **Type:** Select "Panel".
* Note down your extension's **Client ID** and **Extension ID**.
* **Asset Hosting:** Upload your frontend files (`config.html`, `config.js`, `panel.html`, `viewer.js`, CSS, images like `na.png`, `spotify.png`) as a ZIP file for each version you create. Set the "Panel Viewer Path" and "Configuration Path".
* **Capabilities / Content Security Policy (CSP):**
    * Add your Railway app's base URL to the **`Allowlist config Urls`**, **`Allowlist panel Urls`** and **`Allowlist for URL Fetching Domains`** directive in the CSP. Example:
        ```
        https://<your-railway-app-url> 
        ````
        It also could be possible that you need the following endpoints specified: 
        ```
        https://<your-railway-app-url>/spotify/disconnect
        https://<your-railway-app-url>/spotify/status
        https://<your-railway-app-url>/spotify/auth_callback
        ```
    * You also need the following Spotify URL in **`Allowlist config Urls`**:
        ```
        https://accounts.spotify.com
        ```
    * Add Spotify's image CDN to the **`Allowlist for Image Domains`** directive:
        ```
        https://i.scdn.co/image, https://i.scdn.co/
        ```
* **Testing:** Set a version to "Hosted Test" for development.

**4. Backend Setup (Railway):**

* **Clone Repository:**
    ```bash
    git clone https://github.com/SeriousDots/twitch-spotify-widget.git
    cd twitch-spotify-widget
    ```
* **Railway Project:**
    * Create a new project on Railway and link it to your GitHub repository.
    * Add a **PostgreSQL** database service. Railway should automatically provide a `DATABASE_URL` environment variable to your application service.
* **Environment Variables:** Set the following environment variables in your Railway service settings:
    * `SPOTIPY_CLIENT_ID`: Your Spotify App Client ID.
    * `SPOTIPY_CLIENT_SECRET`: Your Spotify App Client Secret.
    * `SPOTIPY_REDIRECT_URI`: The *exact* redirect URI you added to Spotify (`https://<your-railway-app-url>/spotify/auth_callback`).
    * `TWITCH_EXTENSION_CLIENT_ID`: Your Twitch Extension Client ID.
    * `TWITCH_EXTENSION_ID`: Your Twitch Extension ID.
    * `DATABASE_URL`: (Should be provided automatically by Railway when linking the PostgreSQL service).
* **Procfile:** Ensure you have a `Procfile` in your repository root:
    ```Procfile
    web: gunicorn app:app --bind 0.0.0.0:$PORT -t 120
    ```
    *(The `-t 120` increases the worker timeout, which can be helpful).*
* **Deployment:** Railway should automatically deploy when you push changes to your linked GitHub branch. The `requirements.txt` will be used to install dependencies, and the `init_db()` function in `app.py` will create the database table on the first start.

**5. Local Development (Optional):**

* Create a virtual environment: `python -m venv venv`
* Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
* Install dependencies: `pip install -r requirements.txt`
* Create a `.env` file in the `backend` directory with the same environment variables as listed for Railway.
* Run the Flask development server: `python app.py` (This will use the `if __name__ == '__main__':` block).

## 🚀 Usage

1.  **Broadcaster Setup:**
    * Install the extension on their Twitch channel.
    * Activate it in a Panel slot.
    * Go to Creator Dashboard -> Extensions -> My Extensions -> Click the gear icon on your extension to open the Configuration Panel (`config.html`).
    * Click "Connect with Spotify".
    * Log in to Spotify and authorize the requested permissions.
    * The panel should update to show "Connected to Spotify" and a "Disconnect" button.
2.  **Viewer Experience:**
    * Viewers visiting the broadcaster's channel will see the panel.
    * The panel (`panel.html`/`viewer.js`) will fetch data from your backend (`/spotify/data`).
    * The backend uses the broadcaster's stored Refresh Token to get the currently playing song from Spotify.
    * The panel displays the song title, artist, and album cover, linked to Spotify.
    * If no song is playing, a default message and image are shown.

## 📝 Notes

* The Refresh Token is stored securely in the backend database, associated with the Broadcaster's Twitch ID. It is never exposed to the frontend viewer panel.
* The `config.js` uses `window.opener.postMessage` to communicate success back from the Spotify auth popup to the main config window.
* The config panel UI relies on querying a backend `/spotify/status` endpoint to determine the connection state dynamically.

## 🙏 Acknowledgements

* [Spotipy](https://spotipy.readthedocs.io/) library for simplifying Spotify API interaction.
* [Flask](https://flask.palletsprojects.com/) web framework.
* [Twitch Developers](https://dev.twitch.tv/) for the extension platform.
