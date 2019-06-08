from __future__ import print_function
import datetime
from datetime import datetime
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

########################################

# Imports for replace()
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

import time
import os

dbFile = "db.txt"

taskName = ""
start = 0
day = 0
hour = 0
minutes = 0
seconds = 0
elapsedSeconds = 0

startTime = ""

prevTime = 0
newTime = 0
formatTime = 0

saveQ = ""

def beginTask():
    global start, startTime
    start = time.perf_counter()
    startTime = time.strftime('%Y-%m-%dT%H:%M:00-07:00',time.localtime(time.time()))
    print("Enjoy your work session!")
    # current date and time
    now = datetime.now()
    t = now.strftime("%H:%M:%S")
    print("Session began at " + t)

def endTask():
    global taskName
    input_var = input("End task?: ")
    elapsedSeconds = time.perf_counter() - start
    convertSeconds(elapsedSeconds)
    promptSave()
    if saveQ == 'y':
        print("Summary of your work period:")
        updateDB(taskName, elapsedSeconds)
        print("The total time spent on this task is: ")
        convertSeconds(getTime(taskName))
    elif saveQ == 'n':
        exit()
    else:
        endTask()

def convertSeconds(elapsedSeconds):
    day = elapsedSeconds/(24*3600)
    if day < 1:
        day = 0
    elapsedSeconds = elapsedSeconds % (3600)
    hour = elapsedSeconds/3600
    if hour < 1:
        hour = 0
    elapsedSeconds %= 3600
    minutes = elapsedSeconds/60
    if minutes < 1:
        minutes = 0
    elapsedSeconds %= 60
    seconds = elapsedSeconds
    print('{:.0f}'.format(hour),"h", '{:.0f}'.format(minutes),"m", '{:.0f}'.format(seconds),"s")

def checkDB(taskName):
    global prevTime
    dbString = open(dbFile, 'r')
    dbString.read()
    if taskName in open(dbFile).read():
        # Task already exists
        lines = [line.rstrip('\n') for line in open(dbFile)]
        for task in lines:
            split = task.split(":")
            name = split[0]
            time = split[1]
            if name == taskName:
                prevTime = int(time)
    else:
        # Task does not yet exist
        if os.stat(dbFile).st_size > 0:
            with open(dbFile, 'a') as db:
                print(taskName + " was added to the database")
                db.write('\n' + taskName  + ":0")
        else:
            with open(dbFile, 'a') as db:
                print(taskName + " was added to the database")
                db.write(taskName  + ":0")

def updateDB(taskName, elapsedSeconds): 
    global prevTime
    global newTime
    global formatTime, dbFile
    lines = [line.rstrip('\n') for line in open(dbFile)]
    for task in lines:
        split = task.split(":")
        name = split[0]
        prevTime = split[1]
        if name == taskName:
            newTime = int(prevTime) + elapsedSeconds
            formatTime = '{:.0f}'.format(newTime)
            newTask = taskName + ":" + str(formatTime)
            with open(dbFile, 'a'):
                replace(task, newTask)

def replace(pattern, subst):
    global dbFile
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(dbFile) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Move new file
    move(abs_path, dbFile)

def getTime(taskName):
    lines = [line.rstrip('\n') for line in open('db.txt')]
    for task in lines:
        split = task.split(":")
        name = split[0]
        time = split[1]
        if name == taskName:
            return int(time)

def updateGoogleCalendar():
    global endTime
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    event = {
        'summary': taskName,
        'location': 'Home',
        'description': '',
        'colorId' : 8,
        'start': {
            'dateTime': startTime,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': endTime,
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            
        ],
        'attendees': [
            
        ],
        'reminders': {
            
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def promptSave():
    global saveQ
    saveQ = input("Would you like to record this work session? (y/n)")        
   
print("----------------------------\n         WORK LOGGER \n----------------------------")
taskName = input("What is the name of the task? ")
taskName = taskName.title() # Converts input string to title
checkDB(taskName) 
beginTask()
endTask()
endTime = time.strftime('%Y-%m-%dT%H:%M:00-07:00',time.localtime(time.time()))
updateGoogleCalendar()
