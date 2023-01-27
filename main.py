import datetime, schedule
import pyrebase
import pyttsx3
import requests

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


# to check voices in apple
# import pyttsx3
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# for voice in voices:
#     print('v is ', voice, ' id is ', voice.id)
#     engine.setProperty('voice', voice.id)
#     engine.say("Hello World!")
#     engine.runAndWait()
#     engine.stop()
#todo : check
def say(text):
    # voiceId = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
    engine = pyttsx3.init()
    engine.setProperty('voice', 0)
    engine.setProperty('rate', 100)
    engine.say(text)
    engine.runAndWait()
    # voices = engine.getProperty('voices')
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
    _currenttime = datetime.datetime.now().strftime("%H%M%S")
    fingerprintData = db.child('fingerPrint').get().val()

    for uid in fingerprintData:
        try:
            # print(fingerprintData[uid][str(todaysDate)])
            for _inTime in fingerprintData[uid][str(todaysDate)]:
                # print(_inTime)
                announced = fingerprintData[uid][str(todaysDate)][_inTime]['announce']
                # print(announced)
                if not announced:
                    name = fingerprintData[uid]['name']
                    print(name)
                    say('welcome ' + name + ' have a great day')
                    db.child('fingerPrint').child(uid).child(todaysDate).child(_inTime).update({"announce": True})
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

        if 20 < battery >= 30 and tabAnnounce:
            say("Prem Tab battery is 30, Kindly charge the tab")
            tabAnnounce = False
        if 15 < battery >= 20 and tabAnnounce:
            say("Prem Tab battery is 20, Kindly charge the tab")
            tabAnnounce = False
        if 10 < battery <= 15 and tabAnnounce:
            say("Prem Tab battery is less than 15, Kindly charge the tab")
            tabAnnounce = False
        if battery < 10 and tabAnnounce:
            say("Prem Tab battery is less than 10, Kindly charge the tab")
            tabAnnounce = False
        if battery < 5 and tabAnnounce:
            say("Prem Tab battery is less than 5, Kindly charge the tab")
            tabAnnounce = False


def refreshment():
    refreshmentList = []
    presentList = []
    placedList = []
    refreshmentList.clear()
    presentList.clear()
    placedList.clear()
    todaysDate = str(datetime.date.today())
    data = db.get().val()
    staffData = data['staff']
    for staff in staffData:
        if not staffData[staff]['department'] == 'ADMIN':
            fp = db.child('fingerPrint').get().val()
            try:
                fp[staff][todaysDate]
                presentList.append(staffData[staff]['name'])
            except:
                pass

    noOfPresent = len(presentList)
    # noOfAbsent = len(absentList)
    ref = db.child('refreshments').get().val()
    a = 0
    if datetime.datetime.now().strftime("%H:%M") <= "10:50":
        c = ref[todaysDate]['FN']
        try:
            a = a + c['tea_count']
        except:
            a = a
        try:
            a = a + c['coffee_count']
        except:
            a = a
        try:
            a = a + c['nothing_count']
        except:
            a = a
        totalCounts = a
        if totalCounts < noOfPresent:
            for refr in ref[todaysDate]['FN']:
                try:
                    for a in ref[todaysDate]['FN'][refr]:
                        placedList.append(ref[todaysDate]['FN'][refr][a])
                        revisedPL = list(dict.fromkeys(placedList))
                except:
                    pass
            try:
                for x in range(len(presentList)):
                    if presentList[x] not in revisedPL:
                        refreshmentList.append(presentList[x])
                say(f"Kindly place your desired refreshment {refreshmentList}")
            except:
                pass

    if datetime.datetime.now().strftime("%H:%M") > "10:50":
        c = ref[todaysDate]['AN']
        try:
            a = a + c['tea_count']
        except:
            a = a
        try:
            a = a + c['coffee_count']
        except:
            a = a
        try:
            a = a + c['nothing_count']
        except:
            a = a
        totalCounts = a
        if totalCounts < noOfPresent:
            for refr in ref[todaysDate]['AN']:
                try:
                    for a in ref[todaysDate]['AN'][refr]:
                        placedList.append(ref[todaysDate]['AN'][refr][a])
                        revisedPL = list(dict.fromkeys(placedList))
                except:
                    pass
            try:
                for x in range(len(presentList)):
                    if presentList[x] not in revisedPL:
                        refreshmentList.append(presentList[x])
                say(f"Kindly place your desired refreshment {refreshmentList}")
            except:
                pass


# refreshment()
def resetEnergyMonitor():


    requests.put("http://192.168.1.18/eb/1",
                 data={
                     "id": 1,
                     "R_Current": 0,
                     "Y_Current": 0,
                     "B_Current": 0,
                     "R_Voltage": 0,
                     "Y_Voltage": 0,
                     "B_Voltage": 0,
                     "UPS_Voltage": 0,
                     "UPS_Current": 0.0,
                     "UPS_Battery": 0
                 })

def announce():
    data = db.child('onyx').get().val()
    onyxAnounncement = data['announcement']
    if onyxAnounncement != 0:
        say(onyxAnounncement)
        db.child('onyx').update({'announcement': 0})
    # print("end of announce")

schedule.every(5).minutes.do(resetEnergyMonitor())
while True:
    currentTime = datetime.datetime.now().strftime('%I:%M:%S %p')
    print(currentTime)

    try:
        schedule.run_pending()
        announce()
        ebState()
        announceFingerPrint()
        # tabStatus()
        if datetime.datetime.now().strftime("%H:%M:%S") == ("10:45:01" or "14:45:01"):
            refreshment()


    except Exception as e:
        print("error at ", e)
