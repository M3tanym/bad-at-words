from fastapi import FastAPI

app = FastAPI()

VERSION = 0.1

@app.get("/")
def root():
    return {"Welcome" : "The Game by Timothy Ford and Ben Gillett"}

@app.get("/version")
def version():
    return {"Version" : VERSION}
