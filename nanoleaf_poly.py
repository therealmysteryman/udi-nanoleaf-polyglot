#!/usr/bin/env python3

"""
This is a NodeServer for Nanoleaf written by automationgeek (Jean-Francois Tremblay) 
based on the NodeServer template for Polyglot v2 written in Python2/3 by Einstein.42 (James Milne) milne.james@gmail.com
"""

import polyinterface
import time
import json
import sys
from nanoleaf import setup
from nanoleaf import Aurora

LOGGER = polyinterface.LOGGER
SERVERDATA = json.load(open('server.json'))
VERSION = SERVERDATA['credits'][0]['version']

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'NanoLeaf'
        self.initialized = False
        self.host = ""
        self.userid = ""
        self.tries = 0

    def start(self):
        LOGGER.info('Started NanoLeaf for v2 NodeServer version %s', str(VERSION))
        try:
            if 'host' in self.polyConfig['customParams']:
                self.host = self.polyConfig['customParams']['host']
            else:
                self.host = ""

            if self.host == "":
                LOGGER.error('MiLight requires \'host\' parameters to be specified in custom configuration.')
                self.setDriver('ST', o)
                return False
            else:
                self.setDriver('ST', 1)
                self.discover()
        except Exception as ex:
            LOGGER.error('Error starting NanoLeaf NodeServer: %s', str(ex))

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        time.sleep(1)
        LOGGER.error(self.host)
        token = setup.generate_auth_token("172.16.50.27")
        LOGGER.error(token)
        
        self.userid = token
        
        data = { 'bridge_ip': self.host, 'bridge_user': token }
        self.saveCustomData(data)
        
        self.addNode(AuroraNode(self, self.address, 'aurora', 'aurora'))

    def delete(self):
        LOGGER.info('Deleting NanoLeaf')
        
    id = 'controller'
    commands = {}
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    
class AuroraNode(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(AuroraNode, self).__init__(controller, primary, address, name)
        
        self.my_aurora = Aurora(self.parent.host,self.parent.userid)
        self.timeout = 5.0
            
    def start(self):
        pass

    def setOn(self, command):
        self.my_aurora.on = True
        self.setDriver('ST', 100)

    def setOff(self, command):
        self.my_aurora.on = False
        self.setDriver('ST', 0)
        
    def setBrightness(self, command):
        query = command.get('query')
        intBri = int(command.get('value'))
        
        self.setDriver('GV3', intBri)

    def setEffect(self, command):
        query = command.get('query')
        intEffect = int(command.get('value'))
       
        self.setDriver('GV4', intEffect)
       
    def query(self):
        self.reportDrivers()
        
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78},
               {'driver': 'GV3', 'value': 0, 'uom': 51},
               {'driver': 'GV4', 'value': 1, 'uom': 100}]
    id = 'AURORA'
    commands = {
                    'DON': setOn,
                    'DOF': setOff,
                    "SET_BRI": setBrightness,
                    "SET_EFFECT": setEffect
                }
    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('NanoLeafNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
