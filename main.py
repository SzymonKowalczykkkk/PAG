# Autorzy: Szymon Kowalczyk, Weronika Kałowska, Krzysztof Rutkowski
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import pymongo
import redis

# Ustworzenie api
app = FastAPI()

# Ustawienie rzeczy potrzebnych do działania api ze stroną
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/woj/")

@app.get("/pow/")

@app.get("/points/")

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)