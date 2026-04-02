from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api import router as api_router

app = FastAPI()

# Mount the static directory for CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)

@app.get("/")
async def serve_frontend():
    return FileResponse('index.html')
