from fastapi import FastAPI
from .routers import search, tiles, maps, regions, health
from .middleware.cors import setup_cors

app = FastAPI(
    title="Geospatial Visual Search Engine",
    description="API for searching visually similar objects in satellite imagery",
    version="0.1.0"
)

# Setup Middleware
setup_cors(app)

# Include Routers
app.include_router(search.router)
app.include_router(tiles.router)
app.include_router(maps.router)
app.include_router(regions.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Geospatial Visual Search Engine API"}
