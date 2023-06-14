# dynamic.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base64
# import tensorflow
# from tensorflow import keras
# from PIL import Image
# import matplotlib.pyplot as plt

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def dynamic_file(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dynamic")
async def dynamic(request: Request, file: UploadFile = File()):
    data = file.file.read()
    file.file.close()

    # encoding the image
    encoded_image = base64.b64encode(data).decode("utf-8")

    #Demo Model Linking
    # probability = model.predict(img2Array(image))

    return templates.TemplateResponse("dynamic.html", {"request": request,  "img": encoded_image})

# # if __name__ == '__dynamic__':
# #    uvicorn.run(app, host='0.0.0.0', port=8000)

# demo = Image.open("/workspace/Pheonix_Squadron/PDR-OS-LRG.jpg")
# plt.imshow(demo)