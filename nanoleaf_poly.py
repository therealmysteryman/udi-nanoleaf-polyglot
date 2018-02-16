#!/usr/bin/env python3

"""
This is a NodeServer for Nanoleaf Aurora written by automationgeek (Jean-Francois Tremblay) 
based on the NodeServer template for Polyglot v2 written in Python2/3 by Einstein.42 (James Milne) milne.james@gmail.com.
Using this Python Library to control NanoLeaf by Software2 https://github.com/software-2/nanoleaf
"""

import polyinterface
import time
import json
import sys
import os
import zipfile
from nanoleaf import setup
from nanoleaf import Aurora

LOGGER = polyinterface.LOGGER

with open('server.json') as data:
    SERVERDATA = json.load(data)
try:
    VERSION = SERVERDATA['credits'][0]['version']
except (KeyError, ValueError):
    LOGGER.info('Version not found in server.json.')
    VERSION = '0.0.0'

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'NanoLeaf'
        self.initialized = False
        self.tries = 0
        self.nano_ip = None
        self.nano_token = None
        self.requestNewToken = 0
        
    def start(self):
        LOGGER.info('Started NanoLeaf Aurora for v2 NodeServer version %s', str(VERSION))
        try:
            custom_data_token = False
            
            if 'requestNewToken' in self.polyConfig['customParams']:
                self.requestNewToken = self.polyConfig['customParams']['requestNewToken']    
            
            if 'ip' in self.polyConfig['customParams'] and self.nano_ip is None:
                self.nano_ip = self.polyConfig['customParams']['ip']
                LOGGER.info('Custom IP address specified: {}'.format(self.nano_ip))
            else:
                LOGGER.error('Need to have ip address in custom param ip')
                self.setDriver('ST', 0, True)
                return False
            
            if 'token' in self.polyConfig['customParams'] and self.nano_token is None:
                self.nano_token = self.polyConfig['customParams']['token']
                LOGGER.info('Custom Token specified: {}'.format(self.nano_token))
            else:
                if 'nano_token' in self.polyConfig['customData']:
                    self.nano_token = self.polyConfig['customData']['nano_token']
                    custom_data_token = True
                    LOGGER.info('Nano token found in the Database.')
                else:
                    LOGGER.info('Custom Data is not found in the DB')

            # Obtain NanoLeaf token, make sure to push on the power button of Aurora until Light is Flashing
            if self.nano_token is None or self.requestNewToken == 1:
                LOGGER.debug('Requesting Token')
                for myHost in self.nano_ip.split(','):
                    mytoken = setup.generate_auth_token(myHost)
                    if mytoken is None:
                        LOGGER.error('Unable to obtain the token, make sure the NanoLeaf is in Linking mode')
                        self.setDriver('ST', 0, True)
                        return False
                    elseif self.nano_token is None:
                        self.nano_token = mytoken
                    else:
                        self.nano_token = self.nano_token + ',' + mytoken
                        
            if  custom_data_token == False:
                LOGGER.debug('Saving access credentials to the Database')
                data = { 'nano_token': self.nano_token }
                self.saveCustomData(data)
            
            self.setDriver('ST', 1, True)
            self.discover()
                                                            
        except Exception as ex:
            LOGGER.error('Error starting NanoLeaf NodeServer: %s', str(ex))
            self.setDriver('ST', 0)
            return False

    def shortPoll(self):
        pass

    def longPoll(self):
        self.query()

    def query(self):
        self.setDriver('ST', 1, True)
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].query()

    def write_profile_zip(self):
        try:
            src = 'profile'
            abs_src = os.path.abspath(src)
            with zipfile.ZipFile('profile.zip', 'w') as zf:
                for dirname, subdirs, files in os.walk(src):
                    for filename in files:
                        if filename.endswith('.xml') or filename.endswith('txt'):
                            absname = os.path.abspath(os.path.join(dirname, filename))
                            arcname = absname[len(abs_src) + 1:]
                            LOGGER.info('write_profile_zip: %s as %s' % (os.path.join(dirname, filename),arcname))
                            zf.write(absname, arcname)
            zf.close()
        except Exception as ex:
            LOGGER.error('Error zipping profile: %s', str(ex))
        
    def install_profile(self):
        try:
            self.poly.installprofile()
            LOGGER.info('Please restart the Admin Console for change to take effect')
        except Exception as ex:
            LOGGER.error('Error installing profile: %s', str(ex))
        return True
        
    def discover(self, *args, **kwargs):
        time.sleep(1)
        count = 0
        arrToken = self.nano_token.split(',')
        for myHost in self.nano_ip.split(','):
            self.addNode(AuroraNode(self, self.address, 'aurora' + str(count+1) , 'Aurora' + str(count+1), myHost, arrToken[count]))
            count = count + 1
            
    def delete(self):
        LOGGER.info('Deleting NanoLeaf')
        
    id = 'controller'
    commands = {}
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    
class AuroraNode(polyinterface.Node):

    def __init__(self, controller, primary, address, name, ip, token):
        super(AuroraNode, self).__init__(controller, primary, address, name)
        self.do_poll = True
        self.timeout = 5.0
        self.nano_ip = ip
        self.nano_token = token
        self.arrEffects = None
        
        try:
            self.my_aurora = Aurora(self.nano_ip,self.nano_token)
        except Exception as ex:
            LOGGER.error('Error unable to connect to NanoLeaf Aurora: %s', str(ex))
            
        self.__getEffetsList()
        self.__BuildProfile()
        self.query()

    def start(self):
        pass
        
    def setOn(self, command):
        self.my_aurora.on = True
        self.setDriver('ST', 100, True)

    def setOff(self, command):
        self.my_aurora.on = False
        self.setDriver('ST', 0, True)
        
    def setBrightness(self, command):
        intBri = int(command.get('value'))
        self.my_aurora.brightness = intBri                                                   
        self.setDriver('GV3', intBri, True)

    def setEffect(self, command):
        intEffect = int(command.get('value'))
        self.my_aurora.effect = self.arrEffects[intEffect-1]
        self.setDriver('GV4', intEffect, True)
    
    def setProfile(self, command):
        self.__saveEffetsList()
        self.__BuildProfile()
    
    def query(self):
        self.__updateValue()

    def __updateValue(self):
        try:
            if self.my_aurora.on is True:
                self.setDriver('ST', 100, True)
            else:
                self.setDriver('ST', 0, True)
            self.setDriver('GV3', self.my_aurora.brightness, True)
            self.setDriver('GV4', self.arrEffects.index(self.my_aurora.effect)+1, True)
        except Exception as ex:
            LOGGER.error('Error updating Aurora value: %s', str(ex))
    
    def __saveEffetsList(self):
        try:
            self.arrEffects = self.my_aurora.effects_list
        except Exception as ex:
            LOGGER.error('Unable to get NanoLeaf Effet List: %s', str(ex))
            
        #Write effectLists to Json
        try:
            with open(".effectLists.json", "w+") as outfile:
                json.dump(self.arrEffects, outfile)
        except IOError:
            LOGGER.error('Unable to write effectLists.json')
              
    def __getEffetsList(self):
        try:
            with open(".effectLists.json", "r") as infile:
                self.arrEffects = json.load(infile)
        except IOError:
            self.__saveEffetsList()
    
    def __BuildProfile(self):
        try:
            # Build File NLS from Template
            with open("profile/nls/en_us.template") as f:
                with open("profile/nls/en_us.txt", "w+") as f1:
                    for line in f:
                        f1.write(line) 
                    f1.write("\n") 
                f1.close()
            f.close()

            # Add Effect to NLS Profile        
            with open("profile/nls/en_us.txt", "a") as myfile:
                intCounter = 1
                for x in self.arrEffects:  
                    myfile.write("EFFECT_SEL-" + str(intCounter) + " = " + x + "\n")
                    intCounter = intCounter + 1
            myfile.close()

            intArrSize = len(self.arrEffects)
            if intArrSize is None or intArrSize == 0 :
                intArrSize = 1

            with open("profile/editor/editors.template") as f:
                with open("profile/editor/editors.xml", "w+") as f1:
                    for line in f:
                        f1.write(line) 
                    f1.write("\n") 
                f1.close()
            f.close()

            with open("profile/editor/editors.xml", "a") as myfile:
                myfile.write("\t<editor id=\"MEFFECT\">"  + "\n")
                myfile.write("\t\t<range uom=\"25\" subset=\"1-"+ str(intArrSize) + "\" nls=\"EFFECT_SEL\" />"  + "\n")
                myfile.write("\t</editor>" + "\n")
                myfile.write("</editors>")
            myfile.close()
        
        except Exception as ex:
            LOGGER.error('Error generating profile: %s', str(ex))
        
        self.parent.write_profile_zip()
        self.parent.install_profile()

        
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78},
               {'driver': 'GV3', 'value': 0, 'uom': 51},
               {'driver': 'GV4', 'value': 1, 'uom': 25}]
    
    id = 'AURORA'
    commands = {
                    'QUERY': query,            
                    'DON': setOn,
                    'DOF': setOff,
                    'SET_PROFILE' : setProfile,
                    'SET_BRI': setBrightness,
                    'SET_EFFECT': setEffect
                }
    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('NanoLeafNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
