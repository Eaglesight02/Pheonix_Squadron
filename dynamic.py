# dynamic.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
import base64
import tensorflow
from tensorflow import keras
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

#model = keras.models.load_model("sequential.h5")

class Item(BaseModel):
    image_Path : str | None = None

@app.get("/")
async def dynamic_file(request: Request):
    path = "No Image Uploaded Yet"
    prediction = [[0]]
    return templates.TemplateResponse("index.html", {"request": request, "img_Path": path ,"probability": prediction})

# @app.post("/sendURL")
# async def sendURL(request: Request, item: Item):
#     path = item.image_Path
#     return templates.TemplateResponse("/dynamic", {"request": request, "path": path})

@app.post("/dynamic")
async def dynamic(request: Request, image: Annotated[UploadFile, File(...)]):
    # data = file.file.read()
    # file.file.close()
    # encoding the image
    data = await image.read()
    # encoded_image = base64.b64encode(data).decode("utf-8")

    # file = open(path, 'rb')
    # encoded_Data = await file.read()
    # file.close()

# decoded_Image = base64.b64decode(path)

    image = Image.open(io.BytesIO(data))
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis = 0)

    shape = image.shape
    # prediction = model.predict(image)
    prediction = [[0.8881818111881]]

    return templates.TemplateResponse("index.html", {"request": request, "img_Path": shape, "probability": prediction})

# # if __name__ == '__dynamic__':
# #    uvicorn.run(app, host='0.0.0.0', port=8000)

# demo = Image.open("/workspace/Pheonix_Squadron/PDR-OS-LRG.jpg")
# plt.imshow(demo)
#