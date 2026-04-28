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
