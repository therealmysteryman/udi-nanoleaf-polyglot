#!/usr/bin/env python3

"""
This is a NodeServer for MiLight Protocol V6 written by automationgeek (Jean-Francois Tremblay) 
based on the NodeServer template for Polyglot v2 written in Python2/3 by Einstein.42 (James Milne) milne.james@gmail.com
MiLight functionality based on 'Milight-Wifi-Bridge-3.0-Python-Library' project by QuentinCG (https://github.com/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library)
"""

import polyinterface
import time
import json
import sys
from MilightWifiBridge import MilightWifiBridge

LOGGER = polyinterface.LOGGER
SERVERDATA = json.load(open('server.json'))
VERSION = SERVERDATA['credits'][0]['version']

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'MiLight'
        self.initialized = False
        self.host = ""
        self.port = 5987
        self.tries = 0

    def start(self):
        LOGGER.info('Started MiLight for v2 NodeServer version %s', str(VERSION))
        try:
            if 'host' in self.polyConfig['customParams']:
                self.host = self.polyConfig['customParams']['host']
            else:
                self.host = ""

            if 'port' in self.polyConfig['customParams']:
                self.port = self.polyConfig['customParams']['port']
            else:
                self.port = 5987

            if self.host == "" or self.port == "" :
                LOGGER.error('MiLight requires \'host\' parameters to be specified in custom configuration.')
                self.setDriver('ST', o)
                return False
            else:
                self.setDriver('ST', 1)
                self.discover()
        except Exception as ex:
            LOGGER.error('Error starting MiLight NodeServer: %s', str(ex))

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        time.sleep(1)
        self.addNode(MiLightBridge(self, self.address, 'bridge', 'Bridge'))
        self.addNode(MiLightLight(self, self.address, 'zone1', 'Zone1'))
        self.addNode(MiLightLight(self, self.address, 'zone2', 'Zone2'))
        self.addNode(MiLightLight(self, self.address, 'zone3', 'Zone3'))
        self.addNode(MiLightLight(self, self.address, 'zone4', 'Zone4'))

    def delete(self):
        LOGGER.info('Deleting MiLight')
        
    id = 'controller'
    commands = {}
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    
class MiLightLight(polyinterface.Node):

    def __init__(self, controller, primary, address, name):

        super(MiLightLight, self).__init__(controller, primary, address, name)
        self.host = self.parent.host
        self.port = self.parent.port
        self.timeout = 5.0
        
        # Light Group 1-4 0=ALL
        if name == 'Zone1':
            self.grpNum = 1
        elif name == 'Zone2':
            self.grpNum = 2
        elif name == 'Zone3':
            self.grpNum = 3
        elif name == 'Zone4':
            self.grpNum = 4
            
    def start(self):
        pass

    def setOn(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.turnOn(zoneId=self.grpNum)
        myMilight.close()
        self.setDriver('ST', 100)

    def setOff(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.turnOff(zoneId=self.grpNum)
        myMilight.close()
        self.setDriver('ST', 0)
        
    def setColor(self, command):
        query = command.get('query')
        intColor = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setColor(color=intColor, zoneId=self.grpNum) 
        myMilight.close()
        self.setDriver('GV1', intColor)
        
    def setSaturation(self, command):
        query = command.get('query')
        intSat = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setSaturation(saturation=intSat, zoneId=self.grpNum) 
        myMilight.close()
        self.setDriver('GV2', intSat)
        
    def setBrightness(self, command):
        query = command.get('query')
        intBri = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setBrightness(brightness=intBri, zoneId=self.grpNum) 
        myMilight.close()
        self.setDriver('GV3', intBri)

    def setTempColor(self, command):
        query = command.get('query')
        intTemp = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setTemperature(temperature=intTemp, zoneId=self.grpNum) 
        myMilight.close()
        self.setDriver('CLITEMP', intTemp)
        
    def setEffect(self, command):
        query = command.get('query')
        intEffect = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setDiscoMode(discoMode=intEffect, zoneId=self.grpNum)
        myMilight.close()
        self.setDriver('GV4', intEffect)
        
    def setWhiteMode(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setWhiteMode(zoneId=self.grpNum)
        myMilight.close()
        
    def setNightMode(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setNightMode(zoneId=self.grpNum)
        myMilight.close()
        
    def query(self):
        self.reportDrivers()
        
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78},
               {'driver': 'GV1', 'value': 0, 'uom': 100},
               {'driver': 'GV2', 'value': 0, 'uom': 51},
               {'driver': 'GV3', 'value': 0, 'uom': 51},
               {'driver': 'CLITEMP', 'value': 0, 'uom': 26},
               {'driver': 'GV4', 'value': 1, 'uom': 100}]
    id = 'MILIGHT_LIGHT'
    commands = {
                    'DON': setOn,
                    'DOF': setOff,
                    "SET_COLOR": setColor,
                    "SET_SAT": setSaturation,
                    "SET_BRI": setBrightness,
                    "CLITEMP": setTempColor,
                    "SET_EFFECT": setEffect,
                    "WHITE_MODE": setWhiteMode,
                    "NIGHT_MODE": setNightMode
                }
    
class MiLightBridge(polyinterface.Node):

    def __init__(self, controller, primary, address, name):

        super(MiLightBridge, self).__init__(controller, primary, address, name)
        self.host = self.parent.host
        self.port = self.parent.port
        self.timeout = 5.0
            
    def start(self):
        pass

    def setOn(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.turnOnWifiBridgeLamp()
        myMilight.close()
        self.setDriver('ST', 100)

    def setOff(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.turnOffWifiBridgeLamp()
        myMilight.close()
        self.setDriver('ST', 0)
        
    def setColor(self, command):
        query = command.get('query')
        intColor = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setColorBridgeLamp(color=intColor) 
        myMilight.close()
        self.setDriver('GV1', intColor)
        
    def setBrightness(self, command):
        query = command.get('query')
        intBri = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setBrightnessBridgeLamp(brightness=intBri) 
        myMilight.close()
        self.setDriver('GV3', intBri)
        
    def setEffect(self, command):
        query = command.get('query')
        intEffect = int(command.get('value'))
        
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setDiscoModeBridgeLamp(discoMode=intEffect)
        myMilight.close()
        self.setDriver('GV4', intEffect)
        
    def setWhiteMode(self, command):
        myMilight = MilightWifiBridge()
        myMilight.setup(ip=self.host, port=self.port, timeout_sec=self.timeout)
        myMilight.setWhiteModeBridgeLamp()
        myMilight.close()
  
    def query(self):
        self.reportDrivers()
        
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78},
               {'driver': 'GV1', 'value': 0, 'uom': 100},
               {'driver': 'GV3', 'value': 0, 'uom': 51},
               {'driver': 'GV4', 'value': 1, 'uom': 100}]
    id = 'MILIGHT_BRIDGE'
    commands = {
                    'DON': setOn,
                    'DOF': setOff,
                    "SET_COLOR": setColor,
                    "SET_BRI": setBrightness,
                    "SET_EFFECT": setEffect,
                    "WHITE_MODE": setWhiteMode
                }
    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('MiLightNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
