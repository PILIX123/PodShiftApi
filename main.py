from fastapi import FastAPI
from models.forminputmodel import FormInputModel

app = FastAPI(debug=__debug__)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/PodShift')
async def addFeed(form: FormInputModel):
    tt = form
    print(type(form.recurrence[0]))
    return {"message": "content"}
