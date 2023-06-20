# dynamic.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
from datetime import date, datetime

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

key_Path = "cloudkarya-internship key gcs.json"
project_id = "cloudkarya-internship"
bigquery_Client = bigquery.Client.from_service_account_json(key_Path)
storage_Client = storage.Client.from_service_account_json(key_Path)
bucket_Name = "diabetic-retinopathy_01"

def upload_Data(image : UploadFile, data_Entry : dict, prediction : float):
    folder_Name = "images"
    bucket = storage_Client.get_bucket(bucket_Name)

    # Upload the image into the Cloud Storage
    blob = bucket.blob(f'{folder_Name}/{image.filename}')
    image.file.seek(0)
    blob.upload_from_file(image.file)

    # Get the image path from Cloud Storage
    data_Entry["image_Path"] = f"https://storage.googleapis.com/{bucket_Name}/{blob.name}"
    data_Entry["dr_Probability"] = prediction

    # Upload the data along with image path into Big Query
    table = 'cloudkarya-internship.patient_data.demo_table_01'

    # query = f"""
    #         INSERT INTO `{project_id}.ImageData.ImageDataTable`
    #         VALUES ('{image_path}', '{image_type}', '{patient_id}', '{patient_name}', 
    #                 DATE('{dob}'), '{Gender}', '{patient_email}', 
    #                 {pred1}, {pred2}, {pred3}, {pred4})
    #         """
    #         job = bigquery_client.query(query)
    #         job.result()
            

    errors = bigquery_Client.insert_rows_json(table, [data_Entry])

    if errors :
        raise Exception(f'Error inserting rows into BigQuery : {errors}')

    return data_Entry["image_Path"]


@app.get("/")
async def dynamic_file(request : Request):
    return templates.TemplateResponse("index.html", {"request" : request})


@app.post("/dynamic")
async def dynamic(request : Request, image : Annotated[UploadFile, File(...)],
                                    patient_Id : Annotated[str, Form(...)],
                                    patient_Name : Annotated[str, Form(...)],
                                    patient_Dob : Annotated[str, Form(...)],
                                    patient_Email : Annotated[str, Form(...)],
                                    patient_Gender : Annotated[str, Form(...)],
                                    patient_Mobile : Annotated[str, Form(...)]):

    # Read the Image and Convert it into Required Format
    data = await image.read()
    #encoded_Image = base64.b64encode(data)
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
    
    test_Date = str(datetime.now().date())

    data_Entry = {"patient_Id": patient_Id, "patient_Name": patient_Name, "patient_Dob": patient_Dob, "patient_Mobile": patient_Mobile, "patient_Email": patient_Email, "patient_Gender": patient_Gender, "test_Date": test_Date}

    image_Path = upload_Data(image, data_Entry, prediction)

    return templates.TemplateResponse("index.html", {"request" : request, "probability": prediction, "img": image_Path , "patient_Id": patient_Id, "patient_Name": patient_Name,"patient_Dob": patient_Dob,"patient_Email": patient_Email,"patient_Gender": patient_Gender, "test_Date": test_Date})


    
@app.post("/getdata")
async def get_data(request: Request,patient_id:Annotated[str,Form(...)]):

   query = f"""
         SELECT  * FROM {project_id}.patient_data.demo_table_01
         WHERE patient_id = '{patient_id}';
   """

   df = bigquery_Client.query(query).to_dataframe()
   print(df.head())
   image_Path = df.iloc[0]["image_Path"]
   #img = Image.open(image_Path)
   #encoded_img =base64.b64encode(img).decode('utf-8')
   prediction = df.iloc[0]['dr_Probability']
   patient_Id = df.iloc[0]['patient_Id']
   patient_Name = df.iloc[0]['patient_Name']
   patient_Email = df.iloc[0]['patient_Email']
   patient_Dob = df.iloc[0]['patient_Dob']
   patient_Gender = df.iloc[0]['patient_Gender']
   test_Date = df.iloc[0]['test_Date']

   return templates.TemplateResponse("index.html", {"request": request, "probability": prediction, "img": image_Path , "patient_Id": patient_Id, "patient_Name": patient_Name,"patient_Dob": patient_Dob,"patient_Email": patient_Email,"patient_Gender": patient_Gender, "test_Date": test_Date})
   

# # if __name__ == '__dynamic__':
# #    uvicorn.run(app, host='0.0.0.0', port=8000)
