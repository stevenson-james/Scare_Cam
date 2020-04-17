'''
Authors: James Stevenson, Cade Newell, Joey Torii
Section: 2
File: scareCam.py

Description:
This is our final python script designed to run on boot of
our Raspbery Pi IoT device called "Scare Cam"
This code will first take the user through the process of
authenticating their Google Drive account for usage with the app,
then will run the sensor until motion is detected
The video recorded will be saved locally and uploaded to Google Drive

'''
# Google Drive imports
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Scare cam imports
import RPi.GPIO as GPIO
from os.path import join as pjoin
import time
import picamera
from time import sleep, gmtime, strftime
from pygame import mixer

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens after authorization
    # Authorization should only have to be done once
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Sign-in for drive account
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the instance for api calls
    drive_service = build('drive', 'v3', credentials=creds)
    if drive_service:
        print ('Successful connection')

    # Create a folder for scare videos on drive account
    folderName = 'Scare Videos'
    # Get any current instance of folder in drive account
    results = drive_service.files().list(
        q="mimeType=\'application/vnd.google-apps.folder\' and name = \'" + folderName + "\' and trashed = false",
        pageSize = 1,
        fields = 'files(id, name)').execute()
    # If folder doesn't already exist, add to account
    if not results.get('files', []):
        file_metadata = {
        'name': folderName,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        root_folder = drive_service.files().create(body = file_metadata).execute()
        print('Folder \'%s\' created' % folderName)

    # Set filename to current date & time to maintain different file names for each recording
    fileName = "scare_" + strftime("%m-%d %H:%M:%S", gmtime()) + ".h264"
    path_to_file = pjoin("ScareVideos", fileName)

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    # PIR Sensor setup
    GPIO.setup(11, GPIO.IN)

    camera = picamera.PiCamera()
    camera.resolution = (640, 480)

    while True:
        # sleep for 10 seconds to allow for turning on of scare cam
        time.sleep(10)
        i=GPIO.input(11)
        if i==0:
            print("No intruders",i)
            time.sleep(1)
        elif i==1:
            print("Intruder detected",i)
            
            # play scary sound
            mixer.init()
            mixer.music.load("scream.mp3")
            mixer.music.play()

            # save to "path to file"
            camera.start_recording(path_to_file)
            camera.start_preview()
            camera.wait_recording(8)
            camera.stop_recording()
            camera.stop_preview()
            camera.close()
            mixer.music.stop()
            print("video recording stopped")
            break
    
    # Upload scare cam video (using same process as adding a folder above)
    # fileName should be changed based on current video
    results = drive_service.files().list(
        q="mimeType=\'video/h264\' and name = \'" + fileName + "\' and trashed = false",
        pageSize = 1,
        fields = 'files(id, name)').execute()
    if not results.get('files', []):
        file_metadata = {'name': fileName}
        media = MediaFileUpload('ScareVideos/' + fileName, mimetype='video/h264')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
        print ('File \'%s\' added' % file.get('name'))

if __name__ == '__main__':
    main()