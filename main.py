from fastapi import FastAPI


app = FastAPI(debug=__debug__)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/PodShift')
async def addFeed():
    return {"message": "content"}
