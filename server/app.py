from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="../client/index.html"), name="static")


VERSION = 0.1

@app.get("/")
def root():
    return {"Welcome" : "The Game by Timothy Ford and Ben Gillet"}

@app.get("/version")
def version():
    return {"Version" : VERSION}
