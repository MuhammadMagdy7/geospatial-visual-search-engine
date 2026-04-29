# Geospatial Visual Search Engine

An application that allows users to search for visually similar objects in satellite imagery.

## Tech Stack
- **Frontend:** React, TypeScript, Vite, MapLibre GL JS, Zustand, React Query, Tailwind CSS.
- **Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL, PostGIS, pgvector.
- **Infrastructure:** Docker, Docker Compose.

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/MuhammadMagdy7/geospatial-visual-search-engine
   cd geospatial-visual-search
   ```

2. **Configuration**
   Copy the example environment file and add your Google Maps API Key.
   ```bash
   cp .env.example .env
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Features
- **Interactive Map:** Browse satellite imagery and select regions for search.
- **Visual Search:** Upload an image of an object to find similar ones.
- **Mock Results:** Currently uses a mock service to simulate AI-driven search results.
- **Google Maps Proxy:** Seamlessly view high-resolution satellite tiles via the backend proxy.

## Project Structure
- `backend/`: FastAPI application and search logic.
- `frontend/`: React application and interactive map.
- `database/`: SQL scripts for initializing PostGIS and pgvector.

## First-time Model Setup

The backend uses **RemoteCLIP** (a CLIP model fine-tuned for satellite imagery) 
which is ~600 MB. The model must be downloaded once on first run, then runs 
fully offline thereafter.

### First run (one-time download)

1. Edit your `.env` file and temporarily set:
   ```env
   TRANSFORMERS_OFFLINE=0
   ```

2. Start the stack:
   ```bash
   docker-compose up -d
   ```

3. Watch logs until you see "Startup complete. Model loaded successfully.":
   ```bash
   docker-compose logs -f backend
   ```
   This first run takes 5-20 minutes depending on your internet speed.

4. After the model is cached, edit `.env` and switch back to:
   ```env
   TRANSFORMERS_OFFLINE=1
   ```

5. Restart the backend to apply offline mode:
   ```bash
   docker-compose restart backend
   ```

### Subsequent runs
The model is now cached in the `hf_cache` Docker volume. Backend starts in ~2 seconds.

### What if the volume is deleted?
If you run `docker-compose down -v`, the cache is wiped. Repeat the first-run procedure above.

### Verifying the model is loaded
```bash
curl http://localhost:8000/api/v1/ml/health
```
Should return `"model_loaded": true`.
