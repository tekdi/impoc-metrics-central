import os
import shutil
import schedule
import time
from pydantic import BaseModel
import csv
import requests

class Metrics(BaseModel):
    _os: str="Android"
    _os_version: str="4.1"
    _device: str="Samsung Galaxy"
    _resolution: str="1200x800"
    _carrier: str="Vodafone"
    _app_version: str="1.2"
    _density: str="MDPI"
    _store: str="com.android.vending"
    _browser: str="Chrome"
    _browser_version: str="40.0.0"

class Custom(BaseModel):
    user_id: str
    data:str
    result_level: str
    topic: str



class user_details(BaseModel):
    name: str
    username: str
    custom: Custom

class CSVRow(BaseModel):
    device_id: str
    session_id: str
    start_time: str
    duration: int
    unit_key: str
    user_id:str
    topic: str
    result_level: str
    data: str

def read_all_csv_data(directory):
    all_data = []

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and "diagnosis" in filename.lower():
            file_path = os.path.join(directory, filename)
            
            # Read data from each CSV file
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = [row for row in reader]
            
            # Append the data to the list
            all_data.extend(data)

    return all_data

def call_external_api(app_key: str, device_id: str ,user_info :user_details,metrics : Metrics,duration :int):
    external_api_url = f'https://imagine-53aad90cf8be4.flex.countly.com/i?app_key={app_key}&device_id={device_id}&user_details={user_info}&metrics={metrics}&begin_session=1&end_session=1&session_duration={duration}'

    try:
        response = requests.get(external_api_url, headers={"accept": "application/json"})
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(response.json())
    except requests.exceptions.HTTPError as exc:
         print(f"Error: {response.status_code} - {response.text}")
    except Exception as exc:
         print(f"Error: {response.status_code} - {response.text}")
    

def process_csv_files(source_directory, destination_directory):
    # Ensure the destination directory exists
    os.makedirs(destination_directory, exist_ok=True)

    # List all files in the source directory
    files_to_process = [f for f in os.listdir(source_directory) if f.endswith(".csv")]

    for file_name in files_to_process:
        # Construct the paths for the source and destination files
        source_file_path = os.path.join(source_directory, file_name)
        destination_file_path = os.path.join(destination_directory, file_name)

        # Copy the file to the destination directory
        shutil.copyfile(source_file_path, destination_file_path)

        # Delete the original file
        os.remove(source_file_path)

def job():
    # Replace these paths with your actual source and destination directories
    source_directory = 'UploadedFilesOnCentralServer'
    destination_directory = 'UplodedToCountlyServer'

    file =read_all_csv_data(source_directory)
    for row in file:
        try:
            csv_row = CSVRow(**row)
            custom =Custom(user_id=csv_row.user_id,data=csv_row.data,result_level=csv_row.result_level,topic=csv_row.topic)
            user_info = user_details(name="test",username="student",custom= custom)
            mertics =Metrics
            response  = call_external_api("57db304136b17d7ceb29def4c74bed576c1eb645",csv_row.device_id,user_info,mertics,csv_row.duration)
        except Exception as e:
            print(f"Error: {response.status_code} - {response.text}")

    print(f"Successfully uploded to countly")
    process_csv_files(source_directory, destination_directory)
    print("Job executed at", time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    # Schedule the job to run every 10 minutes
    schedule.every(1).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass


