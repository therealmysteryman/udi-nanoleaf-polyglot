## This nodeserver has been converted to run on PG3. The code has been moved to https://github.com/UniversalDevicesInc-PG3/udi-nanoleaf-polyglot

# Nanoleaf Polyglot V2 Node Server

![Build Status](https://travis-ci.org/therealmysteryman/udi-nanoleaf-polyglot.svg?branch=master)

This Poly provides an interface between NanoLeaf Aurora and Polyglot v2 server. Support control of one Aurora Light per Node Server

#### Installation

Installation instructions
You can install from Polyglot V2 store or manually :

1. cd ~/.polyglot/nodeservers
2. git clone https://github.com/therealmysteryman/udi-nanoleaf-polyglot.git
3. run ./install.sh to install the required dependency.
4. Create a custom variable named ip -> ipaddress_of_aurora or list of IP seperated by comma
5. Before starting the Nanoleaf Node Server for the first time. Please make sure to have the Aurora in linking mode to generate the token. (holding the power button until the light flash) If you do have a token already then created a custom variable token -> token_string
6. After the first run, I suggest you click on the Rebuild Profile of the Aurora and restart the Admin Console. This will provide you with and updated list of Effect for your Aurora. If you use more then one Aurora make sure your Effect List are the same. 

If you want to reset the token or the ip of the nanoleaf, add a custom variable requestNewToken -> 1, to force rebuild of the cache.

#### Usage

This will create two nodes of for the Nanoleaf Controller and then one for the Aurora Light.

Support command are :
- Off / On 
- Brightness
- Effet
- Rebuild Effect List

The first time you must press the Rebuild Effect List, to build your effect list from your NanoLeaf app. When you add or remove an effect in your Nanoleaf app you need to rebuild your effect list for the change to appear in ISY.

Note : Everytime you Rebuild your effect list you need to restart ISY Admin Console for the change to take effect.

#### Source

1. Based on the Node Server Template - https://github.com/Einstein42/udi-poly-template-python
2. Library for controlling the NanoLeaf Aurora - https://github.com/Oro/pynanoleaf
