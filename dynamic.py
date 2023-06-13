# dynamic.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
import base64

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("dynamic.html", {"request": request})

@app.post("/dynamic")
def dynamic(request: Request, file: UploadFile = File()):
    data = file.file.read()
    file.file.close()

    # encoding the image
    encoded_image = base64.b64encode(data).decode("utf-8")

    return templates.TemplateResponse(
        "dynamic.html", {"request": request,  "img": encoded_image})
