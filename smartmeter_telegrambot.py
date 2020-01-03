import telegram_api.telegram_bot_api as api
import subprocess
import shlex


class SmartmeterBot:
    def __init__(self, token, logger):
        self.bot = api.Bot(token)
        self.logger = logger
        self.offset = 0

    def get_updates(self):
        """
        Hole neue Nachrichten vom Telegramserver ab und quittiere diese
        :return:
        """
        self.bot.get_updates(self.offset)
        self.logger.debug(self.bot.result)
        # Wenn das Update erfolgreich ist, das Ergebnis vom Objekt in lokale Variable übertragen und auswerten
        if self.bot.result["ok"]:
            result = self.bot.result["result"]
            self.logger.debug("Das Update enthält {anzahl} Nachrichten".format(anzahl=len(result)))
            update_id = []
            for counter, nachricht in enumerate(result):
                self.logger.debug("Inhalt Nachricht {nr}: {inhalt}".format(nr=counter, inhalt=nachricht))
                nachrichten_handler(nachricht, self.bot)
                update_id.append(nachricht["update_id"])
            # Die größte update_id um 1 erhöhen und als Offsetwert für nächste Abfrage speichern
            if len(result) != 0:
                self.offset = max(update_id) + 1
            else:
                self.offset = 0
        else:
            self.logger.info("Telegram Abruf fehlgeschlagen")
        self.bot.get_updates(self.offset)


def nachrichten_handler(nachricht, bot):
    """Handling der vorliegenden Nachricht"""
    telegramid = nachricht["message"]["from"]["id"]
    if "message" in nachricht:
        # Prüfen ob es sich um ein Botkommando handelt
        if "bot_command" in nachricht["message"].get("entities", [{}])[0].get("type", ""):
            bot_command(nachricht, bot, telegramid)


# ---------------------------------------------------------------------------------------------------------------------
# Ab hier kommen die Botkommandos
# ---------------------------------------------------------------------------------------------------------------------
def bot_command(nachricht, bot, telegramid):
    """Hier werden alle Verfügbaren Telegramkommdos angelegt"""
    kommando = nachricht["message"]["text"]
    if kommando == "/start":
        pass
    elif kommando == "/schnelles_messintervall":
        schnelles_messintervall()
        bot.send_message(telegramid, "Intervall verkürzt")


def schnelles_messintervall():
    command = "pkill -f smartmeter -USR2"
    subprocess.run(shlex.split(command))
