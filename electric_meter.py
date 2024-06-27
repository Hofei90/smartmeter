#! /usr/bin/python3

from time import sleep
import serial
import minimalmodbus


class ModBusRTU:
    """
    Main class for ModBus communication
    """

    # instrument = None
    # log = None
    data = {}

    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte, serial_if_par, serial_if_stop, slave_addr,
                 timeout):
        """
        Init method of ModBusRTU.
        Here will be the serial modbus adapter connected and initialised.
        """

        self.log = logger
        try:
            s = "Init with: serial_if={}, serial_if_baud={}, serial_if_byte={}, serial_if_par={}, " \
                "serial_if_stop={}, slave_addr={}, timeout={}".format(serial_if, serial_if_baud, serial_if_byte,
                                                                      serial_if_par, serial_if_stop, slave_addr,
                                                                      timeout)

            self.log.debug(s)

            self.instrument = minimalmodbus.Instrument(serial_if, slave_addr)  # port name, slave address (in decimal)
            self.instrument.serial.baudrate = serial_if_baud
            self.instrument.serial.bytesize = serial_if_byte
            self.instrument.serial.parity = serial_if_par
            self.instrument.serial.stopbits = serial_if_stop
            self.instrument.serial.timeout = timeout
        except serial.serialutil.SerialException as e:
            self.log.error("Initialisation returns an error: {}".format(e))

    def read_data_point_from_meter(self, func_code=None, reg_addr=None, number_of_reg=None):
        """
        Read a data point, defined per function code, address data and count of readable bytes.

        @param func_code: Function code for ModeBus
        @param reg_addr: Datapoint register address
        @param number_of_reg: Amount of byte to read

        @return: Returns a list of integer, the length of the list is depend of the parameter 'number_of_reg'
        """
        assert (func_code is not None), "Error: No function code given"
        assert (reg_addr is not None), "Error: Register address parameter missing."
        assert (number_of_reg is not None), "Error: Number of registers parameter missing."

        if self.instrument is not None:
            try:
                scale_value_tupel = self.instrument.read_register(functioncode=func_code, registeraddress=reg_addr,
                                                                  number_of_decimals=number_of_reg)
                self.log.debug("RegAddr='{}', NoOfReg='{}', Result tuple (digit array)='{}'".format(reg_addr,
                                                                                                    number_of_reg,
                                                                                                    scale_value_tupel))
                return scale_value_tupel
            except IOError as e:
                self.log.error("read_registers() returns an io error: {}".format(e.message))
        else:
            self.log.error("No device available, measurement not possible, return None")


class DDS353B(ModBusRTU):
    """
    Driver class for energy meter 'DDS353B'
    This energy meter can be deliver only one value: the front displayed energy value.
    """
    # only once of parameter can be read
    registerAdr = {"power": {"port": 0, "digits": 3}}    # Display value (in kWh)

    def get_engine_values(self):
        # (1) power value from front display
        if self.instrument is not None:
            for key in self.registerAdr:
                # Register address "0", get 3 digits
                val_tuple = self.read_data_point_from_meter(func_code=3, reg_addr=self.registerAdr[key]["port"],
                                                            number_of_reg=self.registerAdr[key]["digits"])
                if val_tuple is not None:
                    # 2 nachkommastellen
                    power_value = (65536 * val_tuple[0] + 256 * val_tuple[1] + val_tuple[2]) / 100.0
                    self.log.debug("Display value (val) = '{}'".format(power_value))
                    self.data[key] = power_value  # store as float per default
                else:
                    self.log.warn("Tuple value '{}' not available".format(key))
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data


class SDM72DM(ModBusRTU):
    """
    Driver class for energy meter 'SDM72D-M-ModBus' (B+G E-Tech EASTRON)
    Data Format: 4 bytes (2 registers) per parameter. Floating point format ( to IEEE 754)
    Most significant register first (Default).
    The default may be changed if required -See Holding Register "Register Order" parameter.
    """

    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte,
                 serial_if_par, serial_if_stop, slave_addr, timeout):
        super().__init__(logger, serial_if, serial_if_baud, serial_if_byte,
                         serial_if_par, serial_if_stop, slave_addr, timeout)
        # Konfiguration der Input Register nach Datenblatt
        self.input_register = {
            "aktuelle_Gesamtwirkleistung": {
                "port": 52, "digits": 2, "Unit": "W", "use": True},
            "Import_Wh_seit_reset": {
                "port": 72, "digits": 2, "Unit": "kWh", "use": True},
            "Export_Wh_seit_reset": {
                "port": 74, "digits": 2, "Unit": "kWh", "use": True},
            "Total_kwh": {
                "port": 342, "digits": 2, "Unit": "kWh", "use": True},
            "Settable_total_kWh": {
                "port": 384, "digits": 2, "Unit": "kWh", "use": True},
            "Settable_import_kWh": {
                "port": 388, "digits": 2, "Unit": "kWh", "use": True},
            "Setabble_export_kWh": {
                "port": 390, "digits": 2, "Unit": "kWh", "use": True},
            "Import_power": {
                "port": 1280, "digits": 2, "Unit": "W", "use": True},
            "Export_power": {
                "port": 1282, "digits": 2, "Unit": "W", "use": True},
        }

    def read_input_values(self, input_register_keys=None):
        """
        Read all in self.input_register defined data points and stored the result as float value
        into self.data dictionary
        :return: self.data dictionary
        """
        self.data = {}
        if input_register_keys is None:
            input_register_keys = self.get_input_keys()
        if self.instrument is not None:
            for key in input_register_keys:
                self.log.debug("try: key='{}', reg='{}', digits='{}'".format(key, self.input_register[key]["port"],
                                                                             self.input_register[key]["digits"]))
                if self.input_register[key]["use"] is True:

                    fehler = 0
                    while True:  # Anzahl der Versuche
                        try:
                            messwert = self.instrument.read_float(functioncode=4,  # fix (!) for this model
                                                                  registeraddress=self.input_register[key]["port"],
                                                                  number_of_registers=self.input_register[key][
                                                                      "digits"])
                        except OSError:
                            fehler += 1
                            self.log.error("Kommunikationserror Nr. {}".format(fehler))
                            sleep(5)
                            if fehler > 5:  # Anzahl der Versuche
                                raise OSError
                        else:
                            break

                    if messwert is None:
                        self.log.warn("Value '{}' not available".format(key))
                    else:
                        self.data[key] = round(messwert, 4)
                    self.log.debug("Value '{}' = '{}'".format(key, self.data[key]))
                else:
                    self.log.debug("Value '{}' not used!".format(key))
                    pass
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data

    def get_input_keys(self):
        """
        Hilfsmethode zur Erstellung der Intervallklassen
        :return:
        """
        input_register_keys = [key for key in self.input_register]
        return input_register_keys


class SDM230(ModBusRTU):
    """
    Driver class for energy meter 'SDM230-ModBus' (B+G E-Tech EASTRON)

    Data Format: 4 bytes (2 registers) per parameter. Floating point format ( to IEEE 754)
    Most significant register first (Default).
    The default may be changed if required -See Holding Register "Register Order" parameter.
    """
    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte,
                 serial_if_par, serial_if_stop, slave_addr, timeout):
        super().__init__(logger, serial_if, serial_if_baud, serial_if_byte,
                         serial_if_par, serial_if_stop, slave_addr, timeout)
        # Konfiguration der Input Register nach Datenblatt
        self.input_register = {"Spannung_L1": {
            "port": 0, "digits": 2, "Unit": "V", "use": True},
            "Strom_L1":
                {"port": 6, "digits": 2, "Unit": "A", "use": True},
            "Wirkleistung_L1":
                {"port": 12, "digits": 2, "Unit": "W", "use": True},
            "Scheinleistung_L1":
                {"port": 18, "digits": 2, "Unit": "VA", "use": True},
            "Blindleistung_L1":
                {"port": 24, "digits": 2, "Unit": "VAr", "use": True},
            "Leistungsfaktor_L1":
                {"port": 30, "digits": 2, "Unit": "", "use": True},
            "Phasenwinkel_L1":
                {"port": 36, "digits": 2, "Unit": "Grad", "use": True},
            "Frequenz":
                {"port": 70, "digits": 2, "Unit": "Hz", "use": True},
            "Import_Wh_seit_reset":
                {"port": 72, "digits": 2, "Unit": "kWh", "use": True},
            "Export_Wh_seit_reset":
                {"port": 74, "digits": 2, "Unit": "kWh", "use": True},
            "Import_VArh_seit_reset":
                {"port": 76, "digits": 2, "Unit": "kVArh", "use": False},
            "Export_VArh_seit_reset":
                {"port": 78, "digits": 2, "Unit": "kVArh", "use": False},
            "Gesamtwirkleistung":
                {"port": 84, "digits": 2, "Unit": "W", "use": True},
            "Max_Gesamtwirkleistung":
                {"port": 86, "digits": 2, "Unit": "W", "use": True},
            "CurrentSystemPositivePowerDemand":
                {"port": 88, "digits": 2, "Unit": "W", "use": True},
            "MaximumSystemPositivePowerDemand":
                {"port": 90, "digits": 2, "Unit": "W", "use": True},
            "CurrentSystemReversePowerDemand":
                {"port": 92, "digits": 2, "Unit": "W", "use": True},
            "Strom_L1_demand":
                {"port": 258, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L1_demand":
                {"port": 264, "digits": 2, "Unit": "A", "use": True},
            "Total_kwh":
                {"port": 342, "digits": 2, "Unit": "kWh", "use": True},
            "Total_kvarh":
                {"port": 344, "digits": 2, "Unit": "kVArh", "use": True}
        }

    def read_input_values(self, input_register_keys=None):
        """
        Read all in self.input_register defined data points and stored the result as float value
        into self.data dictionary
        :return: self.data dictionary
        """
        self.data = {}
        if input_register_keys is None:
            input_register_keys = self.get_input_keys()
        if self.instrument is not None:
            for key in input_register_keys:
                self.log.debug("try: key='{}', reg='{}', digits='{}'".format(key, self.input_register[key]["port"],
                                                                             self.input_register[key]["digits"]))
                if self.input_register[key]["use"] is True:

                    fehler = 0
                    while True:  # Anzahl der Versuche
                        try:
                            messwert = self.instrument.read_float(functioncode=4,  # fix (!) for this model
                                                                  registeraddress=self.input_register[key]["port"],
                                                                  number_of_registers=self.input_register[key][
                                                                      "digits"])
                        except OSError:
                            fehler += 1
                            self.log.error("Kommunikationserror Nr. {}".format(fehler))
                            sleep(5)
                            if fehler > 5:  # Anzahl der Versuche
                                raise OSError
                        else:
                            break

                    if messwert is None:
                        self.log.warn("Value '{}' not available".format(key))
                    else:
                        self.data[key] = round(messwert, 4)
                    self.log.debug("Value '{}' = '{}'".format(key, self.data[key]))
                else:
                    self.log.debug("Value '{}' not used!".format(key))
                    pass
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data

    def get_input_keys(self):
        """
        Hilfsmethode zur Erstellung der Intervallklassen
        :return:
        """
        input_register_keys = [key for key in self.input_register]
        return input_register_keys


class SDM530(ModBusRTU):
    """
    Driver class for energy meter 'SDM530-ModBus' (B+G E-Tech EASTRON)

    Data Format: 4 bytes (2 registers) per parameter. Floating point format ( to IEEE 754)
    Most significant register first (Default).
    The default may be changed if required -See Holding Register "Register Order" parameter.
    """
    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte,
                 serial_if_par, serial_if_stop, slave_addr, timeout):
        super().__init__(logger, serial_if, serial_if_baud, serial_if_byte,
                         serial_if_par, serial_if_stop, slave_addr, timeout)
        # Konfiguration der Input Register nach Datenblatt
        self.input_register = {
            "Spannung_L1": {
                "port": 0, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L2": {
                "port": 2, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L3": {
                "port": 4, "digits": 2, "Unit": "V", "use": True},
            "Strom_L1": {
                "port": 6, "digits": 2, "Unit": "A", "use": True},
            "Strom_L2": {
                "port": 8, "digits": 2, "Unit": "A", "use": True},
            "Strom_L3": {
                "port": 10, "digits": 2, "Unit": "A", "use": True},
            "Wirkleistung_L1": {
                "port": 12, "digits": 2, "Unit": "W", "use": True},
            "Wirkleistung_L2": {
                "port": 14, "digits": 2, "Unit": "W", "use": True},
            "Wirkleistung_L3": {
                "port": 16, "digits": 2, "Unit": "W", "use": True},
            "Scheinleistung_L1": {
                "port": 18, "digits": 2, "Unit": "VA", "use": True},
            "Scheinleistung_L2": {
                "port": 20, "digits": 2, "Unit": "VA", "use": True},
            "Scheinleistung_L3": {
                "port": 22, "digits": 2, "Unit": "VA", "use": True},
            "Blindleistung_L1": {
                "port": 24, "digits": 2, "Unit": "VAr", "use": True},
            "Blindleistung_L2": {
                "port": 26, "digits": 2, "Unit": "VAr", "use": True},
            "Blindleistung_L3": {
                "port": 28, "digits": 2, "Unit": "VAr", "use": True},
            "Leistungsfaktor_L1": {
                "port": 30, "digits": 2, "Unit": "", "use": True},
            "Leistungsfaktor_L2": {
                "port": 32, "digits": 2, "Unit": "", "use": True},
            "Leistungsfaktor_L3": {
                "port": 34, "digits": 2, "Unit": "", "use": True},
            "Phasenwinkel_L1": {
                "port": 36, "digits": 2, "Unit": "Grad", "use": True},
            "Phasenwinkel_L2": {
                "port": 38, "digits": 2, "Unit": "Grad", "use": True},
            "Phasenwinkel_L3": {
                "port": 40, "digits": 2, "Unit": "Grad", "use": True},
            "Durchschnittliche_Spannung_zu_N": {
                "port": 42, "digits": 2, "Unit": "V", "use": True},
            "Durchschnittlicher_Strom_zu_N": {
                "port": 46, "digits": 2, "Unit": "A", "use": True},
            "aktueller_Gesamtstrom": {
                "port": 48, "digits": 2, "Unit": "A", "use": True},
            "aktuelle_Gesamtwirkleistung": {
                "port": 52, "digits": 2, "Unit": "W", "use": True},
            "aktuelle_Gesamtscheinleistung": {
                "port": 56, "digits": 2, "Unit": "VA", "use": True},
            "aktuelle_Gesamtblindleistung": {
                "port": 60, "digits": 2, "Unit": "VAr", "use": True},
            "aktueller_Gesamtleistungsfaktor": {
                "port": 62, "digits": 2, "Unit": "", "use": True},
            "aktueller_Gesamtphasenwinkel": {
                "port": 66, "digits": 2, "Unit": "A", "use": True},
            "Frequenz": {
                "port": 70, "digits": 2, "Unit": "Hz", "use": True},
            "Import_Wh_seit_reset": {
                "port": 72, "digits": 2, "Unit": "kWh", "use": True},
            "Export_Wh_seit_reset": {
                "port": 74, "digits": 2, "Unit": "kWH", "use": True},
            "Import_VArh_seit_reset": {
                "port": 76, "digits": 2, "Unit": "kVArh", "use": True},
            "Export_VArh_seit_reset": {
                "port": 78, "digits": 2, "Unit": "kVArh", "use": True},
            "VAh_seit_reset": {
                "port": 80, "digits": 2, "Unit": "kVAh", "use": True},
            "Ah_seit_reset": {
                "port": 82, "digits": 2, "Unit": "Ah", "use": True},
            "Gesamtwirkleistung": {
                "port": 84, "digits": 2, "Unit": "W", "use": True},
            "Max_Gesamtwirkleistung": {
                "port": 86, "digits": 2, "Unit": "W", "use": True},
            "Gesamtscheinleistung": {
                "port": 100, "digits": 2, "Unit": "VA", "use": True},
            "Max_Gesamtscheinleistung": {
                "port": 102, "digits": 2, "Unit": "VA", "use": True},
            "Gesamtstrom_Neutralleiter": {
                "port": 104, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_Neutralleiter": {
                "port": 106, "digits": 2, "Unit": "A", "use": True},
            "Spannung_L1_L2": {
                "port": 200, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L2_L3": {
                "port": 202, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L3_L1": {
                "port": 204, "digits": 2, "Unit": "V", "use": True},
            "Durchschnittsspannung_L_L": {
                "port": 206, "digits": 2, "Unit": "V", "use": True},
            "Strom_Neutralleiter": {
                "port": 224, "digits": 2, "Unit": "A", "use": True},
            "THD_Spannung_L1": {
                "port": 234, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L2": {
                "port": 236, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L3": {
                "port": 238, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L1": {
                "port": 240, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L2": {
                "port": 242, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L3": {
                "port": 244, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittliche_Spannung_zu_N": {
                "port": 248, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittlicher_Strom_zu_N": {
                "port": 250, "digits": 2, "Unit": "%", "use": True},
            "Gesamtsystemleistungsfaktor": {
                "port": 254, "digits": 2, "Unit": "Grad", "use": True},
            "Strom_L1_demand": {
                "port": 258, "digits": 2, "Unit": "A", "use": True},
            "Strom_L2_demand": {
                "port": 260, "digits": 2, "Unit": "A", "use": True},
            "Strom_L3_demand": {
                "port": 262, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L1_demand": {
                "port": 264, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L2_demand": {
                "port": 266, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L3_demand": {
                "port": 268, "digits": 2, "Unit": "A", "use": True},
            "THD_Spannung_L1_L2": {
                "port": 334, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L2_L3": {
                "port": 336, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L3_L1": {
                "port": 338, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittliche_Spannung_zu_L_L": {
                "port": 340, "digits": 2, "Unit": "%", "use": True},
            "Total_kwh": {
                "port": 342, "digits": 2, "Unit": "kwh", "use": True},
            "Total_kvarh": {
                "port": 344, "digits": 2, "Unit": "kvarh", "use": True}
        }

        # Konfiguration der Holding Register nach Datenblatt
        # TODO: Holding Register schreiben
        self.holding_register = {}

    def read_input_values(self, input_register_keys=None):
        """
        Read in self.input_register defined data points and stored the result as float value into self.data
        dictionary
        :return: self.data dictionary
        """
        self.data = {}
        if input_register_keys is None:
            input_register_keys = self.get_input_keys()
        if self.instrument is not None:
            for key in input_register_keys:
                self.log.debug("try: key='{}', reg='{}', digits='{}'".format(key, self.input_register[key]["port"],
                                                                             self.input_register[key]["digits"]))
                if self.input_register[key]["use"] is True:

                    fehler = 0
                    while True:  # Anzahl der Versuche
                        try:
                            messwert = self.instrument.read_float(functioncode=4,  # fix (!) for this model
                                                                  registeraddress=self.input_register[key]["port"],
                                                                  number_of_registers=self.input_register[key][
                                                                      "digits"])
                        except OSError:
                            fehler += 1
                            self.log.error("Kommunikationserror Nr. {}".format(fehler))
                            sleep(5)
                            if fehler > 5:  # Anzahl der Versuche
                                raise OSError
                        else:
                            break

                    if messwert is None:
                        self.log.warn("Value '{}' not available".format(key))
                    else:
                        self.data[key] = round(messwert, 4)
                    self.log.debug("Value '{}' = '{}'".format(key, self.data[key]))
                else:
                    self.log.debug("Value '{}' not used!".format(key))
                    pass
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data

    def get_input_keys(self):
        """
        Hilfsmethode zur Erstellung der Intervallklassen
        :return:
        """
        input_register_keys = [key for key in self.input_register]
        return input_register_keys


class SDM630(ModBusRTU):
    """
    NEUES Modell muss angepasst werden ********
    Driver class for energy meter 'SDM630-ModBus' (B+G E-Tech EASTRON)

    Data Format: 4 bytes (2 registers) per parameter. Floating point format ( to IEEE 754)
    Most significant register first (Default).
    The default may be changed if required -See Holding Register "Register Order" parameter.
    """

    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte,
                 serial_if_par, serial_if_stop, slave_addr, timeout):
        super().__init__(logger, serial_if, serial_if_baud, serial_if_byte,
                         serial_if_par, serial_if_stop, slave_addr, timeout)
        # Konfiguration der Input Register nach Datenblatt
        self.input_register = {
            "Spannung_L1": {
                "port": 0, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L2": {
                "port": 2, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L3": {
                "port": 4, "digits": 2, "Unit": "V", "use": True},
            "Strom_L1": {
                "port": 6, "digits": 2, "Unit": "A", "use": True},
            "Strom_L2": {
                "port": 8, "digits": 2, "Unit": "A", "use": True},
            "Strom_L3": {
                "port": 10, "digits": 2, "Unit": "A", "use": True},
            "Wirkleistung_L1": {
                "port": 12, "digits": 2, "Unit": "W", "use": True},
            "Wirkleistung_L2": {
                "port": 14, "digits": 2, "Unit": "W", "use": True},
            "Wirkleistung_L3": {
                "port": 16, "digits": 2, "Unit": "W", "use": True},
            "Scheinleistung_L1": {
                "port": 18, "digits": 2, "Unit": "VA", "use": True},
            "Scheinleistung_L2": {
                "port": 20, "digits": 2, "Unit": "VA", "use": True},
            "Scheinleistung_L3": {
                "port": 22, "digits": 2, "Unit": "VA", "use": True},
            "Blindleistung_L1": {
                "port": 24, "digits": 2, "Unit": "VAr", "use": True},
            "Blindleistung_L2": {
                "port": 26, "digits": 2, "Unit": "VAr", "use": True},
            "Blindleistung_L3": {
                "port": 28, "digits": 2, "Unit": "VAr", "use": True},
            "Leistungsfaktor_L1": {
                "port": 30, "digits": 2, "Unit": "", "use": True},
            "Leistungsfaktor_L2": {
                "port": 32, "digits": 2, "Unit": "", "use": True},
            "Leistungsfaktor_L3": {
                "port": 34, "digits": 2, "Unit": "", "use": True},
            "Phasenwinkel_L1": {
                "port": 36, "digits": 2, "Unit": "Grad", "use": True},
            "Phasenwinkel_L2": {
                "port": 38, "digits": 2, "Unit": "Grad", "use": True},
            "Phasenwinkel_L3": {
                "port": 40, "digits": 2, "Unit": "Grad", "use": True},
            "Durchschnittliche_Spannung_zu_N": {
                "port": 42, "digits": 2, "Unit": "V", "use": True},
            "Durchschnittlicher_Strom_zu_N": {
                "port": 46, "digits": 2, "Unit": "A", "use": True},
            "aktueller_Gesamtstrom": {
                "port": 48, "digits": 2, "Unit": "A", "use": True},
            "aktuelle_Gesamtwirkleistung": {
                "port": 52, "digits": 2, "Unit": "W", "use": True},
            "aktuelle_Gesamtscheinleistung": {
                "port": 56, "digits": 2, "Unit": "VA", "use": True},
            "aktuelle_Gesamtblindleistung": {
                "port": 60, "digits": 2, "Unit": "VAr", "use": True},
            "aktueller_Gesamtleistungsfaktor": {
                "port": 62, "digits": 2, "Unit": "", "use": True},
            "aktueller_Gesamtphasenwinkel": {
                "port": 66, "digits": 2, "Unit": "A", "use": True},
            "Frequenz": {
                "port": 70, "digits": 2, "Unit": "Hz", "use": True},
            "Import_Wh_seit_reset": {
                "port": 72, "digits": 2, "Unit": "kWh", "use": True},
            "Export_Wh_seit_reset": {
                "port": 74, "digits": 2, "Unit": "kWH", "use": True},
            "Import_VArh_seit_reset": {
                "port": 76, "digits": 2, "Unit": "kVArh", "use": True},
            "Export_VArh_seit_reset": {
                "port": 78, "digits": 2, "Unit": "kVArh", "use": True},
            "VAh_seit_reset": {
                "port": 80, "digits": 2, "Unit": "kVAh", "use": True},
            "Ah_seit_reset": {
                "port": 82, "digits": 2, "Unit": "Ah", "use": True},
            "Gesamtwirkleistung": {
                "port": 84, "digits": 2, "Unit": "W", "use": True},
            "Max_Gesamtwirkleistung": {
                "port": 86, "digits": 2, "Unit": "W", "use": True},
            "Gesamtscheinleistung": {
                "port": 100, "digits": 2, "Unit": "VA", "use": True},
            "Max_Gesamtscheinleistung": {
                "port": 102, "digits": 2, "Unit": "VA", "use": True},
            "Gesamtstrom_Neutralleiter": {
                "port": 104, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_Neutralleiter": {
                "port": 106, "digits": 2, "Unit": "A", "use": True},
            "Spannung_L1_L2": {
                "port": 200, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L2_L3": {
                "port": 202, "digits": 2, "Unit": "V", "use": True},
            "Spannung_L3_L1": {
                "port": 204, "digits": 2, "Unit": "V", "use": True},
            "Durchschnittsspannung_L_L": {
                "port": 206, "digits": 2, "Unit": "V", "use": True},
            "Strom_Neutralleiter": {
                "port": 224, "digits": 2, "Unit": "A", "use": True},
            "THD_Spannung_L1": {
                "port": 234, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L2": {
                "port": 236, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L3": {
                "port": 238, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L1": {
                "port": 240, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L2": {
                "port": 242, "digits": 2, "Unit": "%", "use": True},
            "THD_Strom_L3": {
                "port": 244, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittliche_Spannung_zu_N": {
                "port": 248, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittlicher_Strom_zu_N": {
                "port": 250, "digits": 2, "Unit": "%", "use": True},
            "Strom_L1_demand": {
                "port": 258, "digits": 2, "Unit": "A", "use": True},
            "Strom_L2_demand": {
                "port": 260, "digits": 2, "Unit": "A", "use": True},
            "Strom_L3_demand": {
                "port": 262, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L1_demand": {
                "port": 264, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L2_demand": {
                "port": 266, "digits": 2, "Unit": "A", "use": True},
            "Max_Strom_L3_demand": {
                "port": 268, "digits": 2, "Unit": "A", "use": True},
            "THD_Spannung_L1_L2": {
                "port": 334, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L2_L3": {
                "port": 336, "digits": 2, "Unit": "%", "use": True},
            "THD_Spannung_L3_L1": {
                "port": 338, "digits": 2, "Unit": "%", "use": True},
            "THD_Durchschnittliche_Spannung_zu_L_L": {
                "port": 340, "digits": 2, "Unit": "%", "use": True},
            "Total_kwh": {
                "port": 342, "digits": 2, "Unit": "kwh", "use": True},
            "Total_kvarh": {
                "port": 344, "digits": 2, "Unit": "kvarh", "use": True},
            "Import_L1_kwh": {
                "port": 346, "digits": 2, "Unit": "kwh", "use": True},
            "Import_L2_kwh": {
                "port": 348, "digits": 2, "Unit": "kwh", "use": True},
            "Import_L3_kwh": {
                "port": 350, "digits": 2, "Unit": "kwh", "use": True},
            "Export_L1_kwh": {
                "port": 352, "digits": 2, "Unit": "kwh", "use": True},
            "Export_L2_kwh": {
                "port": 354, "digits": 2, "Unit": "kwh", "use": True},
            "Export_L3_kwh": {
                "port": 356, "digits": 2, "Unit": "kwh", "use": True},
            "Gesamtstrom_L1_kwh": {
                "port": 358, "digits": 2, "Unit": "kwh", "use": True},
            "Gesamtstrom_L2_kwh": {
                "port": 360, "digits": 2, "Unit": "kwh", "use": True},
            "Gesamtstrom_L3_kwh": {
                "port": 362, "digits": 2, "Unit": "kwh", "use": True},
            "Import_L1_kvarh": {
                "port": 364, "digits": 2, "Unit": "kvarh", "use": True},
            "Import_L2_kvarh": {
                "port": 366, "digits": 2, "Unit": "kvarh", "use": True},
            "Import_L3_kvarh": {
                "port": 368, "digits": 2, "Unit": "kvarh", "use": True},
            "Export_L1_kvarh": {
                "port": 370, "digits": 2, "Unit": "kvarh", "use": True},
            "Export_L2_kvarh": {
                "port": 372, "digits": 2, "Unit": "kvarh", "use": True},
            "Export_L3_kvarh": {
                "port": 374, "digits": 2, "Unit": "kvarh", "use": True},
            "Total_L1_kvarh": {
                "port": 376, "digits": 2, "Unit": "kvarh", "use": True},
            "Total_L2_kvarh": {
                "port": 378, "digits": 2, "Unit": "kvarh", "use": True},
            "Total_L3_kvarh": {
                "port": 380, "digits": 2, "Unit": "kvarh", "use": True},
        }

        # Konfiguration der Holding Register nach Datenblatt
        # TODO: Holding Register schreiben
        self.holding_register = {}

    def read_input_values(self, input_register_keys=None):
        """
        Read in self.input_register defined data points and stored the result as float value into self.data
        dictionary
        :return: self.data dictionary
        """
        self.data = {}
        if input_register_keys is None:
            input_register_keys = self.get_input_keys()
        if self.instrument is not None:
            for key in input_register_keys:
                self.log.debug("try: key='{}', reg='{}', digits='{}'".format(key, self.input_register[key]["port"],
                                                                             self.input_register[key]["digits"]))
                if self.input_register[key]["use"] is True:

                    fehler = 0
                    while True:  # Anzahl der Versuche
                        try:
                            messwert = self.instrument.read_float(functioncode=4,  # 3,4,8,16 for SDM630  4 ok?
                                                                  registeraddress=self.input_register[key]["port"],
                                                                  number_of_registers=self.input_register[key][
                                                                      "digits"])
                        except OSError:
                            fehler += 1
                            self.log.error("Kommunikationserror Nr. {}".format(fehler))
                            sleep(5)
                            if fehler > 5:  # Anzahl der Versuche
                                raise OSError
                        else:
                            break

                    if messwert is None:
                        self.log.warn("Value '{}' not available".format(key))
                    else:
                        self.data[key] = round(messwert, 4)
                    self.log.debug("Value '{}' = '{}'".format(key, self.data[key]))
                else:
                    self.log.debug("Value '{}' not used!".format(key))
                    pass
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data

    def get_input_keys(self):
        """
        Hilfsmethode zur Erstellung der Intervallklassen
        :return:
        """
        input_register_keys = [key for key in self.input_register]
        return input_register_keys


class WS100(ModBusRTU):
    def __init__(self, logger, serial_if, serial_if_baud, serial_if_byte,
                 serial_if_par, serial_if_stop, slave_addr, timeout):
        super().__init__(logger, serial_if, serial_if_baud, serial_if_byte,
                         serial_if_par, serial_if_stop, slave_addr, timeout)
        # Konfiguration der Input Register nach Datenblatt
        self.input_register = {
            "Gesamtwirkleistung": {
                "port": 261, "digits": 0, "Unit": "W", "use": True},
            "Total_kwh": {
                "port": 271, "digits": 2, "Unit": "kWh", "use": True},
        }


    def read_input_values(self, input_register_keys=None):
        """
        Read all in self.input_register defined data points and stored the result as float value
        into self.data dictionary
        :return: self.data dictionary
        """
        self.data = {}
        if input_register_keys is None:
            input_register_keys = self.get_input_keys()
        if self.instrument is not None:
            for key in input_register_keys:
                self.log.debug("try: key='{}', reg='{}', digits='{}'".format(key, self.input_register[key]["port"],
                                                                             self.input_register[key]["digits"]))
                if self.input_register[key]["use"] is True:

                    fehler = 0
                    while True:  # Anzahl der Versuche
                        try:
                            messwert = self.read_data_point_from_meter(func_code=4,
                                                                       reg_addr=self.input_register[key]["port"],
                                                                       number_of_reg=self.input_register[key]["digits"])

                        except OSError:
                            fehler += 1
                            self.log.error("Kommunikationserror Nr. {}".format(fehler))
                            sleep(5)
                            if fehler > 5:  # Anzahl der Versuche
                                raise OSError
                        else:
                            break

                    if messwert is None:
                        self.log.warn("Value '{}' not available".format(key))
                    else:
                        self.data[key] = messwert
                    self.log.debug("Value '{}' = '{}'".format(key, self.data[key]))
                else:
                    self.log.debug("Value '{}' not used!".format(key))
                    pass
        else:
            err_msg = "No instrument available!"
            self.log.error(err_msg)
            return None
        return self.data


    def get_input_keys(self):
        """
        Hilfsmethode zur Erstellung der Intervallklassen
        :return:
        """
        input_register_keys = [key for key in self.input_register]
        return input_register_keys


def get_device_list():
    device_list = {
        "DDS353B": DDS353B,
        "SDM72DM": SDM72DM,
        "SDM230": SDM230,
        "SDM530": SDM530,
        "SDM630": SDM630,
        "WS100": WS100,
    }
    return device_list


# for test or stand alone work
if __name__ == '__main__':
    import logging
    try:
        em = SDM530(logger=logging,
                    serial_if="/dev/ttyUSB0",
                    serial_if_baud=38400,
                    # serial_if_baud=9600,
                    serial_if_byte=8,
                    serial_if_par=serial.PARITY_EVEN,
                    serial_if_stop=1,
                    slave_addr=1,
                    timeout=0.6)

        for wert in em.input_register:
            curEnergie = em.instrument.read_float(em.input_register[wert]["port"], 4, 2)
            print("{} = {}{}".format(wert, curEnergie, em.input_register[wert]["Unit"]))
    except KeyboardInterrupt:
        print("Zählerstand nicht auslesbar")
