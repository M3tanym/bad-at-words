from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


app = FastAPI()

app.mount("/", StaticFiles(directory="../client"), name="index.html")


VERSION = 0.1

@app.get("/")
def root():
    return {"Welcome" : "The Game by Timothy Ford and Ben Gillett"}

@app.get("/version")
def version():
    return {"Version" : VERSION}
