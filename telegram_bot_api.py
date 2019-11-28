#!/usr/bin/python3
# # #
# Telegram Bot API
# Modul als Schnittstelle zur Kommunikation mit Telegram Bot API
# # #

# Import
import requests, json, platform, os

#Debug Modus
debug = False

# Init
staticurl = "https://api.telegram.org/bot"

# Funktionen
def message(name, data):
    if "from" in data:
        name.from_ = data["from"]
    if "chat" in data:
        name.chat = data["chat"]
    else:
        print("Erforderlicher Key nicht enthalten - Fehler, Abbruch")
        return False
    if "forward_from" in data:
        name.forward_from = data["forward_from"]
    if "forward_from_chat" in data:
        name.forward_from_chat = data["forward_from_chat"]
    if "reply_to_message" in data:
        name.reply_to_message = data["reply_to_message"]
    if "entities" in data:
        name.entities = data["entities"]
    if "new_chat_member" in data:
        name.new_chat_member = data["new_chat_member"]
    if "left_chat_member" in data:
        name.left_chat_member = data["left_chat_member"]
    if "pinned_message" in data:
        name.pinned_message = data["pinned_message"]
    return True
    
def check(result):
    if result["ok"] == True:
        return True
    else:
        return False

  
        
def reply_keyboard_markup(data, resize_keyboard, one_time_keyboard, selective):
    """Funktion zur Erstellung der reply_markup Variable zur Übermittlung an die API
    data Format:
    Listindex 0: Keyboardfelder (Typ Liste) Kann alleine übermittelt werden
    Listindex 1: 
    Beispiel:  [["Taste 1", ["Option1", "Option2"]], ["Taste 2"]]"""
   
    keyboard = dict()
    buttons = []
    for daten in data:
        if len(daten) == 1: #Nur Tasten ohne Optionen
            buttons.append({"text" : str(daten[0])}) 
        if len(daten) == 2: #Mit Optionen
            if type(daten[1][0]) and type(daten[1][1]) == bool:
                buttons.append({"text" : str(daten[0]), "request_contact" : daten[1][0], "request_location" : daten[1][1]})
            else:
                print("Optionen müssen Bool werte sein")
                raise ValueError("Nur Bool Werte übermitteln als Optionen")
    keyboard["keyboard"] = [buttons]
    if resize_keyboard != " ":
        keyboard["resize_keyboard"] = resize_keyboard
    if one_time_keyboard != " ":
        keyboard["one_time_keyboard"] = one_time_keyboard
    if selective != " ":
        keyboard["selective"] = selective
    reply_markup = json.dumps(keyboard)
    return reply_markup
    
        

def reply_keyboard_remove(selective):
    keyboard = dict()
    keyboard["remove_keyboard"] = True
    if selective != " ":
        if type(selective) != bool:
            raise TypeError("Nur Boolean erlaubt")    
        keyboard["selective"] = selective
    reply_markup = json.dumps(keyboard)
    return reply_markup

def force_reply(selective):
    daten = dict()
    daten["force_reply"] = True
    if selective != " ":
        if type(selective) != bool:
            raise TypeError("Nur Boolean erlaubt")    
        daten["selective"] = selective
    reply_markup = json.dumps(daten)
    return reply_markup

#Klasse
class bot:
    def __init__(self, token):
        self.token = token
      
    #Empfangen  
    def getMe(self):
        """Auslesen der Botinformationen
        Das Resultat wird self.result abgelegt
        Das Userfeld in self.botuser
        
        Arg: None
        
        Returns:
        
        Bei erfolgreicher Abfrage: True
        Bei fehlerhafter Abfrage: False"""
        #Informationen abholen
        url = staticurl + self.token + "/getMe"
        r = requests.get(url)
        result = r.json()
        if debug: print(result)
        
        #Abfrage auswerten
        if result["ok"] == True:
            self.botuser = result["result"]
            self.result = result
            return True
        else:
            print("Abfrage fehlgeschlagen, Token ok?")
            self.result = result
            return False
            
    #Senden
    def sendMessage(self, chat_id, text, parse_mode = " ", disable_web_page_preview = " ", disable_notification = " ", reply_to_message_id = " ", reply_markup = " "):
        """Funktion zur Übermittlung von Nachrichten
        
        Args:
        chat_id: ID des Chats zur Übermittlung der Nachricht
        text: Inhalt der Nachricht
        parse_mode: optional, Stringinhalt nur "HTML" oder "Markdown", gibt an ob die Nachricht Formatierungen enthält
        disable_web_page_preview: optional,
        disable_notification: optional,
        reply_to_message_id: optional,
        reply_markup: optional,
        
        Returns:
        True: Sendung erfolgreich versendet
        False: Sendung fehlerhaft
        """
        keys = ("chat_id", "text", "parse_mode", "disable_web_page_preview", "disable_notification", "reply_to_message_id", "reply_markup")
        values = [chat_id, text, parse_mode, disable_web_page_preview, disable_notification, reply_to_message_id, reply_markup]
        typ = (str, str, str, bool, bool, int, "")
        merker = []
        counter = 0
        for value in values:
            if value == " ":
                merker.append(False)
            else:
                merker.append(True)
                if typ[counter] != "":
                    values[counter] = typ[counter](values[counter])
            counter += 1
        counter = 0
        params = {}
        for key in keys:
            if merker[counter] == True:
                params[key] = values[counter]
            counter += 1
        url = staticurl + self.token + "/sendMessage"
        r = requests.get(url, params = params)
        
        #Rückmeldung der Sendung
        result = r.json()
        if debug: print(result)
        if check(result) == True:
            if debug: print("Senden erfolgreich")
            self.message = result["result"]
            message(self, self.message)
            
        else:
            print("Senden der Nachricht fehlgeschlagen")
            
    def f_reply_markup(self, methode, data = " ", resize_keyboard = " ", one_time_keyboard = " ", selective = " "):
        """Funktion zur Aufbereitung des reply_markup Felder
        Args:
        methode: 1 = replykeyboardmarkup
                 2 = replykeyboardremove
                 3 = forcereply
        data: für Methode 1: Buttonbeschriftung und Optionen(bool)
              für Methode 2: nicht benötigt
              für Methode 3: True für force_reply
        resize_keyboard: für Methode 1: 
        one_time_keybaord: für Methode 1:
        selective: für Methode 1: Boolean
                   für Methode 2: Boolean
                   für Methode 3: Boolean
        Bsp: #test = bot.f_reply_markup(1, [["Taste 1", [False, False]], ["Taste 2"]], True, True)"""
        if methode == 1 or methode == "replykeyboardmarkup":
            replymarkup = reply_keyboard_markup(data, resize_keyboard, one_time_keyboard, selective)
            return replymarkup
        elif methode == 2 or methode == "replykeyboardremove":
            replymarkup = reply_keyboard_remove(selective)
            return replymarkup
        elif methode == 3 or methode == "forcereply":
            replymarkup = force_reply(selective)          
            return replymarkup
        
    def getUpdates(self, offset = " ", limit = " ", timeout = " ", allowed_updates = " "):
        """ Funktion zum Empfangen von neuen Nachrichten"""
        #Update anhand der Parameter vorbereiten
        url = staticurl + self.token + "/getUpdates"
        if offset != " ":
            if type(offset) == int:
                url = url + "?offset=" + str(offset)
            else:
                print("Nur Integer erlaubt!")
        if limit != " ":
            if 0 <= limit <= 100:
                url = url + "?limit=" + str(limit)
            else:
                print("Nur Zahlenbereich zwischen 0-100 erlaubt")
        if timeout != " ":
            if type(timeout) == int:
                url = url + "?timeout=" + str(timeout)
            else:
                print("Nur Integer erlaubt!")
        if allowed_updates != " ":
            url = url + "?allowed_updates=" + str(allowed_updates)
        #Update abholen
        r = requests.get(url)
        self.result = r.json()
        print(self.result)