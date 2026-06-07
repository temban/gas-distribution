# Gas Distribution System (Web Version)

This project is a web-based adaptation of the Gas Distribution System originally designed for JavaFX.

## Project Structure

- `backend/`: FastAPI backend containing SQLite database and API logic.
- `frontend/`: Simple HTML, CSS, and JS frontend designed to be easily deployed on static site hosting platforms.

## Running Locally

### Backend Setup

1. Open a terminal in the `backend/` directory.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will start at `http://localhost:8000` and automatically seed the database on the first run.

### Frontend Setup

The frontend is entirely static. 
1. You can open `frontend/index.html` directly in your browser.
2. Alternatively, serve it via a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then navigate to `http://localhost:8080`.

## Deployment

### Backend
Deploy the `backend` folder to a platform like **Render**, **Railway**, or **Heroku**.
1. Set the run command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
2. Update the `API_BASE_URL` in `frontend/app.js` to match the deployed backend URL.

### Frontend
Deploy the `frontend` folder to any free static site hosting platform such as **Vercel**, **GitHub Pages**, **Netlify**, or **Cloudflare Pages**. Since it's purely static, it requires no build process. Just link the repository and specify `frontend` as the root directory.

## Features implemented
- Fully functional Splash Screen
- Station browsing by city (Yaounde & Douala)
- Station Details & Cylinder Inventory
- Order Form with real-time total calculation and validation
- Backend API with SQLite DB and CORS enabled for separate static hosting.
