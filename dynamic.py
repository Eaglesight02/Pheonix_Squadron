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

import os
from google.cloud import bigquery, storage
from google.oauth2 import service_account

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

#model = keras.models.load_model("sequential.h5")

class details(BaseModel):
    patient_Id : str   
    patient_Name : str
    patient_Email : str
    patient_Dob : str
    patient_Gender : str
    dr_Probability : float | None = None
    image_Path : str | None = None

key_Path = "cloudkarya-internship-7518ba5e583d.json"
bigquery_Client = bigquery.Client.from_service_account_json(key_Path)
storage_Client = storage.Client.from_service_account_json(key_Path)
bucket_Name = "demo_diabetic_retinopathy"

def upload_Data(image : UploadFile, data_Entry : dict, prediction : float):
    folder_Name = "images"
    bucket = storage_Client.get_bucket(bucket_Name)

    # Upload the image into the Cloud Storage
    blob = bucket.blob(f'{folder_Name}/{image.filename}')
    image.file.seek(0)
    blob.upload_from_file(image.file)

    # Get the image path from Cloud Storage
    data_Entry["image_Path"] = f"https://storage.cloud.google.com/{bucket_Name}/{blob.name}"
    data_Entry["dr_Probability"] = prediction

    # Upload the data along with image path into Big Query
    table = 'cloudkarya-internship.patient_data.table_01'
    errors = bigquery_Client.insert_rows_json(table, [data_Entry])

    if errors :
        raise Exception(f'Error inserting rows into BigQuery : {errors}')


@app.get("/")
async def dynamic_file(request : Request):
    return templates.TemplateResponse("index.html", {"request" : request})


@app.post("/dynamic")
async def dynamic(request : Request, image : Annotated[UploadFile, File(...)],
                                    patient_Id : Annotated[str, Form(...)],
                                    patient_Name : Annotated[str,Form(...)],
                                    patient_Dob : Annotated[str,Form(...)],
                                    patient_Email : Annotated[str,Form(...)],
                                    patient_Gender : Annotated[str,Form(...)],):

    # Read the Image and Convert it into Required Format
    data = await image.read()
    encoded_Image = base64.b64encode(data)
    img = Image.open(io.BytesIO(data))
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis = 0)

    # Get the Model Saved from Cloud Storage
    blob = storage_Client.get_bucket(bucket_Name).blob("models/sequential_Model_Demo")
    model_File = "model.h5"
    blob.download_to_filename(model_File)
    model = keras.models.load_model(model_File)

    # Get the Prediction of Our Model
    prediction = model.predict(img)[0][0] * 100
    # prediction = [[0.8881818111881]]
    os.remove(model_File)

    data_Entry = {"patient_Id": patient_Id, "patient_Name": patient_Name, "patient_Dob": patient_Dob, "patient_Email": patient_Email, "patient_Gender": patient_Gender}

    upload_Data(image, data_Entry, prediction)

    return templates.TemplateResponse("index.html", {"request" : request, "data_Entry" : data_Entry, 
                                                     "img" : image, "probability" : prediction})



# # if __name__ == '__dynamic__':
# #    uvicorn.run(app, host='0.0.0.0', port=8000)
