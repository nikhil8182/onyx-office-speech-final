import datetime
import time
import pyrebase
import pyttsx3
import requests
# changes by koushik
ebOfflineAnounced = False
ebOnlineAnounced = False
ebOffline15MinAnnounced = False
ebOffline30MinAnnounced = False
ebOffline35MinAnnounced = False
ebOfflineTime = ""
tabAnnounce = True

config = {
    "apiKey": "AIzaSyCMp8OJqHy8CkWr6AfYZ0DMMi40wKI98VM",
    "authDomain": "marketing-data-d141d.firebaseapp.com",
    "databaseURL": "https://marketing-data-d141d-default-rtdb.firebaseio.com",
    "projectId": "marketing-data-d141d",
    "storageBucket": "marketing-data-d141d.appspot.com",
    "messagingSenderId": "566962550940",
    "appId": "1:566962550940:web:eee189eca2bb49309e5559"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def say(text):
    voiceId = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()
    voices = engine.getProperty('voices')
    # for voice in voices:
    #     print(voice, voice.id)
    #     engine.setProperty('voice', voice.id)
    #     print("voice id= " , voice.id)
    #     engine.say("hello world from onyx")
    #     engine.runAndWait()
    #     engine.stop()


def powerSavingMode():
    # turn off 3D printer, main pc, design pc
    pass


def ebState():
    global ebOfflineTime, ebOfflineAnounced, ebOnlineAnounced, ebOffline30MinAnnounced, ebOffline35MinAnnounced, ebOffline15MinAnnounced

    _ebstate = requests.get("http://192.168.1.18/sensor/1/").json()
    # _ebstate = requests.get("http://192.168.1.18/24/").json()
    ebState = _ebstate['EB_Status']
    # ebState = _ebstate['Device_Status']
    # print(ebState)
    if not ebState and not ebOfflineAnounced:
        ebOfflineTime = datetime.datetime.now().strftime("%H%M")
        say("onwords office is on UPS, external power supply to the office is down")
        ebOfflineAnounced = True
        ebOnlineAnounced = False

    if ebState and not ebOnlineAnounced:
        say("External power supply in office is restored")
        ebOfflineAnounced = False
        ebOffline30MinAnnounced = False
        ebOffline35MinAnnounced = False
        ebOffline15MinAnnounced = False
        ebOnlineAnounced = True
        ebOfflineTime = None

    if ebOfflineTime is not None:
        currentTime = datetime.datetime.now().strftime("%H%M")
        ebOfflineDuration = int(currentTime) - int(ebOfflineTime)
        print("ebOfflineTime = {}, so eb power is down for {} minutes ".format(ebOfflineTime, ebOfflineDuration))

        if ebOfflineDuration == 15 and not ebOffline15MinAnnounced:
            say("external power supply is down for more than 15 minutes")
            ebOffline15MinAnnounced = True

        if ebOfflineDuration == 30 and not ebOffline30MinAnnounced:
            say("external power supply is down for more than 30 minutes. Prepare for power saving mode which will be "
                "initiated in 5 minutes")
            ebOffline30MinAnnounced = True

        if ebOfflineDuration == 35 and not ebOffline35MinAnnounced:
            say("As External power supply is down for long time onyx is initiating power saving mode")
            powerSavingMode()
            ebOffline35MinAnnounced = True
    # print("end of eb")


def announceFingerPrint():
    todaysDate = datetime.datetime.now().date()
    _currenttime = datetime.datetime.now().strftime("%H%M")
    fingerprintData = db.child('fingerPrint').get().val()
    for uid in fingerprintData:
        try:
            for _inTime in fingerprintData[uid][str(todaysDate)]:
                announced = fingerprintData[uid][str(todaysDate)][_inTime]['announce']
                if not announced:
                    name = fingerprintData[uid]['name']
                    print(name)
                    say('welcome ' + name)
                    db.child('fingerPrint').child(uid).child(todaysDate).child(_inTime).update({"announce": True})
                    # if int(_currenttime) > 930:
                    #     _lt = int(_currenttime) - 930
                    #     hours_total = _lt // 60
                    #     minutes_total = _lt % 60
                    #     if hours_total == 0:
                    #         time_string = "{} minutes".format(minutes_total)
                    #     elif hours_total == 1:
                    #         time_string = "{} hour and {} minutes".format(hours_total, minutes_total)
                    #     else:
                    #         time_string = "{} hours and {} minutes".format(hours_total, minutes_total)
                    #     say('you are late for {}'.format(time_string))
                    if int(_currenttime) > 930:
                        time1 = datetime.datetime.strptime('09:30', '%H:%M').time()
                        a = str(datetime.datetime.now().time().hour)+":"+str(datetime.datetime.now().time().minute)
                        time2 = datetime.datetime.strptime(a, '%H:%M').time()
                        mins1 = (time1.minute + 60 * time1.hour)
                        mins2 = (time2.minute + 60 * time2.hour)
                        final_minutes = mins2 - mins1
                        hours = final_minutes // 60
                        minutes = final_minutes % 60
                        if hours == 0:
                            say(f"You are late for {minutes} minutes")
                        elif hours == 1:
                            say(f"You are late for {hours} hour and {minutes} minutes")
                        else:
                            say(f"You are late for {hours} hours and {minutes} minutes")


        except:
            pass
    # print("end of finger print")
    # print(_currenttime)
    # print(fingerprintData)
    # print("todays date ", todaysDate)

    # for uid in fingerprintData:
    #     print(uid)
    #     # print(fingerprintData[uid][todaysDate])
    #     for y in fingerprintData[uid]:
    #         name = fingerprintData[uid]['name']
    #         announcementStatus = fingerprintData[uid][todaysDate][y]['announce']
    #         fingerprintEntryTime = fingerprintData[uid][todaysDate][y]['Time']
    #         try:
    #             entryTime = fingerprintData[uid]["entryTime"]
    #         except:
    #             pass
    #
    #         # print("{}s entryTime is {}".format(name,entryTime))
    #         # print(announcementStatus)

    #         if announcementStatus == "false":
    #             print("welcoming")
    #             say("welcome " + name)
    #             db.child('fingerPrint').child(uid).child(todaysDate).child(y).update({"announce": True})
    #             # need to remove : in time to subtract time
    #             if int(fingerprintEntryTime) > int(entryTime):
    #                 min = int(fingerprintEntryTime) - int(entryTime)
    #                 say("try to be in office before {} minuets next day ".format(str(min)))


def tabStatus():
    global tabAnnounce
    tab_status = requests.get("http://192.168.1.18/tab/1/").json()
    battery = tab_status['Tab_Charge']
    if battery < 50:
        if battery == 30 and tabAnnounce:
            say("Prem Tab battery is 30, Kindly charge the tab")
            tabAnnounce = False
        if battery == 20 and tabAnnounce:
            say("Prem Tab battery is 20, Kindly charge the tab")
            tabAnnounce = False
        if battery == 15 and tabAnnounce:
            say("Prem Tab battery is less than 15, Kindly charge the tab")
            tabAnnounce = False
        if battery == 10 and tabAnnounce:
            say("Prem Tab battery is less than 10, Kindly charge the tab")
            tabAnnounce = False
        if battery == 5 and tabAnnounce:
            say("Prem Tab battery is less than 5, Kindly charge the tab")
            tabAnnounce = False
    else:
        print("Tab is greater than 50")


def announce():
    data = db.child('onyx').get().val()
    onyxAnounncement = data['announcement']
    if onyxAnounncement != 0:
        say(onyxAnounncement)
        db.child('onyx').update({'announcement': 0})
    # print("end of announce")


while True:
    currentTime = datetime.datetime.now().strftime('%I:%M:%S %p')
    print(currentTime)

    try:
        announce()
        ebState()
        announceFingerPrint()
        tabStatus()

    except Exception as e:
        print("error at ", e)
