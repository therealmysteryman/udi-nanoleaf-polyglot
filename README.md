# MiLight V6 Polyglot V2 Node Server

This Poly provides an interface between Milight iBox 1 or 2 and Polyglot v2 server. Has been testing with RBGW Strip and MR16 bulb and  designed to work with the V6 protocol only. http://www.limitlessled.com/dev/

#### Installation

Installation instructions
You can install it manually running

1. cd ~/.polyglot/nodeservers
2. git clone https://github.com/therealmysteryman/udi-milight-polyglot.git
3. Add a custom variable named host containing the IP Address of the Milight iBox ( eg : host 172.16.1.40 )

#### Source

1. Using this Python Library to control the Milight - https://github.com/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library
2. Based on the Node Server Template - https://github.com/Einstein42/udi-poly-template-python
