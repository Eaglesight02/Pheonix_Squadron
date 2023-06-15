# dynamic.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import base
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

model = keras.models.load_model("sequential.h5")

@app.get("/")
async def dynamic_file(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dynamic")
async def dynamic(filerequest: FileRequest()):
    # data = file.file.read()
    # file.file.close()
    # encoding the image
    data = await file.read()
    # encoded_image = base64.b64encode(data).decode("utf-8")

    image = Image.open(io.BytesIO(data))
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis = 0)

    prediction = model.predict(image)
    

    return templates.TemplateResponse("index.html", {"request": request, "probability": prediction})

# # if __name__ == '__dynamic__':
# #    uvicorn.run(app, host='0.0.0.0', port=8000)

# demo = Image.open("/workspace/Pheonix_Squadron/PDR-OS-LRG.jpg")
# plt.imshow(demo)
#