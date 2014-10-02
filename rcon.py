#!/usr/bin/python
# -*- coding: utf-8 -*-
# #!/usr/bin/python
# Copyright (C) 2014  CF-TOOLS

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License along
#     with this program; if not, write to the Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import socket,hashlib,sys,time,datetime

###
#	RCON CLASS VERSION 0.0.2
###

# CONNECTION INFO IS A DICTIONARY WITH THE FOLLOWING STRUCTURE:
	#{
	#	'ip': "00.000.00.00", # RCON IP
	#	'port': 0000, ### RCON PORT
	#	'password': 'RCON PASSWORD', 
	#	'serverName': "SOME SERVER NAME"  ### THIS CAN BE ANYTHING 
	#}

class RCON:
	def __init__(self,connectionInfo): 
		self.connectionInfo = connectionInfo

		#Initial Connect.
		self.connect()
	def connect(self):

		#Create a socket
		self.socket = socket.socket()

		#Connect to server
		try:
			self.socket.connect((self.connectionInfo['ip'],self.connectionInfo['port']))
		except:
			#Connection failed! Port or IP Wrong.
			time.sleep(2)

			#Re-Trying

			self.connect()
		#Connection established.

		#Set timeout of socket. This is used to prevent the program from getting stuck when server is responding with nothing

		self.socket.settimeout(0.2)
		
		try:
			#Get the welcome message
			welcomeMessage =  self.socket.recv(1024).split(" ")
			self.rconVersion = welcomeMessage[7].replace("\n","")
			#Get the seed which is then digested
			seed =  self.socket.recv(1024).replace("\n","").split(":")[1][1:]

			#Hash seed+password using md5

			digestedPassword = hashlib.md5(seed+self.connectionInfo['password']).hexdigest()

			#Send login cmd

			self.socket.send("login "+digestedPassword+"\n")

			#Chekc if response contains key-word "ready"
			if not "ready" in self.socket.recv(1024):

				#Password is wrong!

				#Closing socket
				self.socket.close()
				#Sleeping 10 seconds
				time.sleep(10)

				#Starting over.
				self.connect()
		except:
			#Connection failed

			#Sleep 2 seconds
			time.sleep(2)

			#Starting over

			self.connect()
		#At this point RCON is ready.
		print "Connected to "+self.connectionInfo['ip']+":"+str(self.connectionInfo['port'])+" RCON version "+self.rconVersion+" ready"
	##########################################
	#Main Query method
	##########################################
	def query(self,cmd,buffersize=10000,sleep=0.1):
		try:
			#Send query & adding \n to finish line.
			self.socket.send(cmd+"\n")
			#Sleep certain amount of time (wait for response) required for bf2cc pl or cmds alike.
			time.sleep(sleep)

			#Get response in variable
			response = self.socket.recv(buffersize)

			#Check if server returned nothing
			if len(response) < 1:
				return False

		except:
			return False
		return response 

	##########################################
	#Get players
	##########################################

	def getPlayers(self):
		return self.query("bf2cc pl")
	
	##########################################
	#Get server Details
	##########################################	
	def getServerDetails(self):
		preServerDetails = self.query("bf2cc si")
		#Check if we can split up
		if("\t" in preServerDetails):
			#Split up details.
			preServerDetails = preServerDetails.split("\t")
			#Check if all variables are actually set.
			if len(preServerDetails) > 30:
				return { 
					"server": { 
						"name": preServerDetails[7],
						"autobalance": int(preServerDetails[24]),
					},
					"map": {
						"name": self.convertMapToCamelCase(preServerDetails[5],preServerDetails[20]) ,
						"round": preServerDetails[31].replace("\n",""),
						"roundsPerMap": self.getRoundsPerMap(),
						"timeElapsed": preServerDetails[18],
					},
					"players": {
						"current": preServerDetails[3],
						"maximum": preServerDetails[2],
						"joining": preServerDetails[4],
					},
					"teams": {
						preServerDetails[8] : {
							"tickets": preServerDetails[11],
							"size": preServerDetails[26],
						},
						preServerDetails[13] : {
							"tickets": preServerDetails[16],
							"size": preServerDetails[27],
						}
					}

				}
			else:
				return False
		else: 
			return False

	#Get the current chat Buffer
	def getChat(self):
		finalChat = { 'admin': [] , 'player': []}
		chat = self.query("bf2cc serverchatbuffer").split("\r\r")
		for message in chat:
			message = message.split("\t")
			thisMessage = {}
			if len(message) == 6:
				message = { 'slot': message[0].replace("\n",""), 'origin': message[1] , 'time': message[4].replace("[","").replace("]",""), 'message': message[1] }
				if message['origin'] == "Admin":
					finalChat['admin'].append(message)
				else:
					finalChat['player'].append(message)
		return finalChat

	#Get vips
	#Mode profileKey|Name
	def getVips(self,mode="profileKey"):
		preVips = self.query("exec game.getVipList")
		finalVips = {}
		if "\t" in preVips:
			preVips = preVips.split("\r")
			for vip in preVips:
				vip =  vip.split("\t")
				if len(vip) > 1:
				 	print vip
					name = vip[0]
					profileKey = vip[1]
					if mode == "profileKey":
						finalVips[profileKey] = name
					else:
						finalVips[name] = profileKey
			return finalVips

	#Save server settings Settings
	def saveSettings(self):
		self.query("exec sv.setRoundsPerMapSave 1")
		self.query("exec sv.setServerNameSave 1")
		self.query("exec sv.setTicketRatioSave 1")
		self.query("exec sv.VipSlotsSave 1")
		self.query("exec sv.setWelcomeMessageSave 1")
		self.query("exec sv.saveSave")
		self.query("exec sv.save")
		self.query("exec sv.load")
	
	####################
	##  CHAT  METHODS ##
	####################
	#Send global chat
	def sendChat(self,message):
		return self.query('exec game.sayAll " |ccc| '+message+'"')
	#Send private Chat by slot.
	def sendChatPrivateByID(self,slot,message):
		return self.query('exec game.sayToPlayerWithId '+str(slot)+' \" |ccc| '+str(message)+'\"',1024,0)
	
	#Kick player instantly
	def kickPlayerInstant(self,slot):
		return self.query('exec admin.kickPlayer '+slot)
	#Send a message to one team
	def sendTeamChat(self,team,message):
		return self.query('exec game.sayTeam '+team+' '+message)

	####################
	##UTILITLY METHODS##
	####################
	#Get banner url
	def getBannerUrl(self):
		return self.query('exec sv.bannerURL')
	
	#Restart Server (30 seconds)
	def restartServer(self):
		self.saveSettings()
		self.query("exec exit")
		time.sleep(31)
		return True
	# Pause server (ranked only)
	def pauseServer(self):
		return self.query('bf2cc pause')
	# Resume server (unranked only)
	def resumeServer(self):
		return self.query('bf2cc unpause')
	#Get autobalance status
	def getAutoBalanceStatus(self):
		if int(self.query("exec sv.autoBalanceTeam")) == 1:
			return True
		else:  
			return False
	#Get ranked status
	def getRankedStatus(self):
		if int(self.query("exec sv.ranked")) == 1:
			return True
		else:  
			return False

	####################
	##  MAP ROTATION  ##
	####################
	# Restart current Map
	def restartMap(self):
		return self.query("exec admin.restartMap")

	def appendMap(self,map,size=32):
		realMap = self.convertCamelCaseToMap(map)
		self.query('exec mapList.append '+realMap['map']+' '+realMap['mode']+' '+str(size))
		return True
	# Get current map ID
	def getNextUpMap(self):
		serverDetails = self.getServerDetails()
		if serverDetails['map']['round'] == serverDetails['map']['roundsPerMap']:
			return self.getNextMapInRotation()
		else:
			return serverDetails['map']['name']
	#Get how many rounds are played per map
	def getRoundsPerMap(self):
		return int(self.query("exec sv.roundsPerMap"))
	#Get current map index in map list
	def getCurrentMapID(self):
		return int(self.query('exec maplist.currentMap'))
	#Get map rotation
	def getCurrentMapRotation(self):
		finalMapRotation = []
		for map in self.query('exec maplist.list').split("\n"):
			if len(map) > 0:
				map     = map.split(":")
				id      = int(map[0])
				map     = map[1].replace(' \" ',"").split(" ")
				mapName = self.convertMapToCamelCase(map[1], map[2])
				size    = map[3]
				finalMapRotation.append({ "id": id , "mapName": mapName  , "size": size})

		return finalMapRotation
	#Get current Map
	def getCurrentMap(self):
		currentMapID = self.getCurrentMapID()
		for map in self.getCurrentMapRotation():
			if map['id'] == currentMapID:
				return map
	#Get next map in map rotation
	def getNextMapInRotation(self):
		currentMapID = self.getCurrentMapID()+1
		for map in self.getCurrentMapRotation():
			if map['id'] == currentMapID:
				return map
	#Convert camelCase map model to p4f model
	def convertCamelCaseToMap(self,map):
		finalMap = {}
		if "rush" in map:
			finalMap['mode'] = "gpm_rush"
		else: 
			finalMap['mode'] = "gpm_sa"
		if "sharqi" in map:
			finalMap['map'] = "sharqi"
		elif "karkand" in map:
			if "rush" in map:
				finalMap['map'] = "karkand_rush"
			else:
				finalMap['map'] = "strike_at_karkand"
		elif "myanmar" in map:
			finalMap['map'] = "trail"
		elif "oman" in map:
			finalMap['map'] = "gulf_of_oman"		
		elif "mashtuur" in map:
			finalMap['map'] = "mashtuur_city"
		elif "dragon" in map:
			finalMap['map'] = "dragon_valley"
		elif "basra" in map:
			finalMap['map'] = "downtown"
		elif "dalian" in map:
			if "rush" in map:
				finalMap['map'] = "dalian_rush"
			else:
				finalMap['map'] = "dalian"	
		return finalMap			
	# Convert ugly play4free map names to camelCase
	def convertMapToCamelCase(self,map,mode):
		
		if "gpm_rush" in mode:
			gameMode = "Rush"
		elif "gpm_sa" in mode:
			gameMode = "Assault"
		else:
			return map+"-"+mode
		map = map.lower()

		if "sharqi" in  map:
			finalMap = "sharqi"

		elif "karkand" in map:
			finalMap = "karkand"

		elif "trail" in map:
			finalMap = "myanmar"

		elif "oman" in map:
			finalMap = "oman"

		elif "mashtuur" in map:
			finalMap = "mashtuur"

		elif "dragon" in map:
			finalMap = "dragonValley"
		elif "dalian" in map:
			finalMap = "dalian"
		else:
			return map+"-"+mode
		return finalMap+gameMode
	# Do an awesome map restart (unranked only)
	def awesomeRestart(self):
		self.sendChat("CF-Tools awesome restart started")
		self.restartMap()
		self.pauseServer()
		limiters = 10
		while limiters >= 1:

			self.sendChat("Starting in "+limiters+" seconds")

			time.sleep(1)
			limiters = limiters-1
		self.resumeServer()

class Support:
	def __init__(self):
		self.weapons = {"2004": { "name": "Medic Box" , "category": "Gadget" , "unlock": 0},"2005": { "name": "Grenade" , "category": "Gadget" , "unlock": 0},"2009": { "name": "Front Line Spawn" , "category": "Gadget" , "unlock": 12},"2017": { "name": "Motion Sensor" , "category": "Gadget" , "unlock": 1},"2021": { "name": "Vehicle Repair Tool" , "category": "Gadget" , "unlock": 0},"2023": { "name": "Ammo Box" , "category": "Gadget" , "unlock": 0},"2024": { "name": "Request Reinforcements" , "category": "Gadget" , "unlock": 0},"2025": { "name": "Mortar Strike" , "category": "Gadget" , "unlock": 12},"2030": { "name": "Defibrillator" , "category": "Gadget" , "unlock": 7},"2034": { "name": "C-4" , "category": "Gadget" , "unlock": 12},"2043": { "name": "Satellite Scan" , "category": "Gadget" , "unlock": 12},"2046": { "name": "Anti-Vehicle Mine" , "category": "Gadget" , "unlock": 0},"2048": { "name": "Claymore" , "category": "Gadget" , "unlock": 7},"2050": { "name": "Smoke Grenade" , "category": "Gadget" , "unlock": 7},"2051": { "name": "XM-25 AGL" , "category": "Gadget" , "unlock": 12},"2054": { "name": "Anti-Vehicle RPG" , "category": "Gadget" , "unlock": 0},"2168": { "name": "Tracer Dart" , "category": "Gadget" , "unlock": 0},"3000": { "name": "870 Combat" , "category": "Shotgun" , "unlock": 4},"3001": { "name": "M16A2" , "category": "AssaultRifle" , "unlock": 12},"3002": { "name": "870 Combat BF3 Edition" , "category": "Shotgun" , "unlock": 4},"3003": { "name": "M249 SAW" , "category": "LMG" , "unlock": 20},"3004": { "name": "SV98" , "category": "SniperRifle" , "unlock": -5},"3005": { "name": "G3A4" , "category": "AssaultRifle" , "unlock": -5},"3006": { "name": "M9" , "category": "Pistol" , "unlock": -2},"3007": { "name": "AEK971" , "category": "AssaultRifle" , "unlock": 3},"3008": { "name": "SPAS-12" , "category": "Shotgun" , "unlock": 10},"3009": { "name": "M9 ONLYTHEFEW" , "category": "Pistol" , "unlock": -2},"3011": { "name": "SCARL" , "category": "AssaultRifle" , "unlock": 6},"3012": { "name": "UMP" , "category": "SMG" , "unlock": 6},"3013": { "name": "MG3" , "category": "LMG" , "unlock": -5},"3014": { "name": "PKM" , "category": "LMG" , "unlock": 3},"3015": { "name": "M60" , "category": "LMG" , "unlock": 12},"3016": { "name": "MP7" , "category": "SMG" , "unlock": 12},"3017": { "name": "P90" , "category": "SMG" , "unlock": 3},"3018": { "name": "PP2000" , "category": "SMG" , "unlock": -5},"3019": { "name": "M1911" , "category": "Pistol" , "unlock": 11},"3020": { "name": "MP-412 Rex" , "category": "Pistol" , "unlock": 14},"3021": { "name": "MP-443" , "category": "Pistol" , "unlock": 5},"3022": { "name": "M95" , "category": "SniperRifle" , "unlock": 20},"3023": { "name": "SVD" , "category": "SniperRifle" , "unlock": 3},"3024": { "name": "M24" , "category": "SniperRifle" , "unlock": 12},"3025": { "name": "SAIGA" , "category": "Shotgun" , "unlock": 7},"3026": { "name": "USAS-12" , "category": "Shotgun" , "unlock": 17},"3027": { "name": "Knife" , "category": "CQC" , "unlock": 0},"3029": { "name": "USAS-12 Veteran" , "category": "Shotgun" , "unlock": 21},"3037": { "name": "M1911 Veteran" , "category": "Pistol" , "unlock": 18},"3038": { "name": "SPAS-12 Veteran" , "category": "Shotgun" , "unlock": 19},"3041": { "name": "MP-443 Veteran" , "category": "Pistol" , "unlock": 16},"3043": { "name": "P226" , "category": "Pistol" , "unlock": 8},"3044": { "name": "SPAS-15" , "category": "Shotgun" , "unlock": 13},"3045": { "name": "SVU-A" , "category": "SniperRifle" , "unlock": 6},"3046": { "name": "STG77AUG" , "category": "AssaultRifle" , "unlock": 9},"3047": { "name": "MP5" , "category": "SMG" , "unlock": 20},"3048": { "name": "MG36" , "category": "LMG" , "unlock": 18},"3050": { "name": "USAS-12 Elite" , "category": "Shotgun" , "unlock": 25},"3051": { "name": "MP-443 Elite" , "category": "Pistol" , "unlock": 20},"3052": { "name": "M1911 Elite" , "category": "Pistol" , "unlock": 22},"3061": { "name": "SPAS-12 Elite" , "category": "Shotgun" , "unlock": 23},"3062": { "name": "M4A1" , "category": "AssaultRifle" , "unlock": 18},"3063": { "name": "M240B" , "category": "LMG" , "unlock": 16},"3064": { "name": "UZI" , "category": "SMG" , "unlock": 16},"3065": { "name": "M14 EBR" , "category": "SniperRifle" , "unlock": 9},"3066": { "name": "M110" , "category": "SniperRifle" , "unlock": 16},"3067": { "name": "AN94" , "category": "AssaultRifle" , "unlock": 15},"3068": { "name": "QJY-88" , "category": "LMG" , "unlock": 9},"3069": { "name": "AKS-74U" , "category": "SMG" , "unlock": 18},"3070": { "name": "VSS" , "category": "SniperRifle" , "unlock": 15},"3071": { "name": "416-Carbine" , "category": "AssaultRifle" , "unlock": 16},"3072": { "name": "FN Minimi Para" , "category": "LMG" , "unlock": 6},"3073": { "name": "9A-91" , "category": "SMG" , "unlock": 9},"3074": { "name": "M249 SAW +3" , "category": "LMG" , "unlock": 0},"3075": { "name": "XM8" , "category": "AssaultRifle" , "unlock": 22},"3076": { "name": "XM8AR" , "category": "LMG" , "unlock": 15},"3077": { "name": "GOL" , "category": "SniperRifle" , "unlock": 18},"3078": { "name": "XM8C" , "category": "SMG" , "unlock": 15},"3079": { "name": "M60 +3" , "category": "LMG" , "unlock": 0},"3080": { "name": "PKM +3" , "category": "LMG" , "unlock": 0},"3081": { "name": "M240B +3" , "category": "LMG" , "unlock": 0},"3082": { "name": "QJY-88 +3" , "category": "LMG" , "unlock": 0},"3083": { "name": "FN Minimi Para +3" , "category": "LMG" , "unlock": 0},"3084": { "name": "XM8AR +3" , "category": "LMG" , "unlock": 0},"3085": { "name": "UMP +3" , "category": "SMG" , "unlock": 0},"3086": { "name": "MP7 +3" , "category": "SMG" , "unlock": 0},"3087": { "name": "P90 +3" , "category": "SMG" , "unlock": 0},"3088": { "name": "MP5 +3" , "category": "SMG" , "unlock": 0},"3089": { "name": "UZI +3" , "category": "SMG" , "unlock": 0},"3090": { "name": "AKS-74U +3" , "category": "SMG" , "unlock": 0},"3091": { "name": "9A-91 +3" , "category": "SMG" , "unlock": 0},"3092": { "name": "XM8C +3" , "category": "SMG" , "unlock": 0},"3093": { "name": "SCARL +3" , "category": "AssaultRifle" , "unlock": 0},"3094": { "name": "STG77AUG +3" , "category": "AssaultRifle" , "unlock": 0},"3095": { "name": "M16A2 +3" , "category": "AssaultRifle" , "unlock": 0},"3096": { "name": "AEK971 +3" , "category": "AssaultRifle" , "unlock": 0},"3097": { "name": "M4A1 +3" , "category": "AssaultRifle" , "unlock": 0},"3098": { "name": "AN-94 +3" , "category": "AssaultRifle" , "unlock": 0},"3099": { "name": "416-Carbine +3" , "category": "AssaultRifle" , "unlock": 0},"3100": { "name": "XM8 +3" , "category": "AssaultRifle" , "unlock": 0},"3101": { "name": "MG36 +3" , "category": "LMG" , "unlock": 0},"3102": { "name": "M95 +3" , "category": "SniperRifle" , "unlock": 0},"3103": { "name": "M24 +3" , "category": "SniperRifle" , "unlock": 0},"3104": { "name": "SVD +3" , "category": "SniperRifle" , "unlock": 0},"3105": { "name": "SVU-A +3" , "category": "SniperRifle" , "unlock": 0},"3106": { "name": "M14 EBR +3" , "category": "SniperRifle" , "unlock": 0},"3107": { "name": "M110 +3" , "category": "SniperRifle" , "unlock": 0},"3108": { "name": "VSS Vintorez +3" , "category": "SniperRifle" , "unlock": 0},"3109": { "name": "GOL +3" , "category": "SniperRifle" , "unlock": 0},"3110": { "name": "AK47" , "category": "AssaultRifle" , "unlock": 20},"3111": { "name": "L96" , "category": "SniperRifle" , "unlock": 24},"3112": { "name": "PP-19" , "category": "SMG" , "unlock": 24},"3113": { "name": "RPK-74M" , "category": "LMG" , "unlock": 22},"3114": { "name": "F2000" , "category": "AssaultRifle" , "unlock": 24},"3115": { "name": "Deagle 50" , "category": "Pistol" , "unlock": 24},"3116": { "name": "M27IAR" , "category": "LMG" , "unlock": 24},"3117": { "name": "PDWR" , "category": "SMG" , "unlock": 22},"3118": { "name": "Steel Deagle 50" , "category": "Pistol" , "unlock": 24},"3119": { "name": "SKS" , "category": "SniperRifle" , "unlock": 21},"3120": { "name": "FAMAS" , "category": "AssaultRifle" , "unlock": 21},"3121": { "name": "QBB-95" , "category": "LMG" , "unlock": 21},"3122": { "name": "AS-VAL" , "category": "SMG" , "unlock": 21},"3123": { "name": "Scattergun" , "category": "Pistol" , "unlock": 21},"3124": { "name": "Nosferatu" , "category": "Pistol" , "unlock": 0},"3125": { "name": "EASY-Piece" , "category": "Pistol" , "unlock": 0},"3126": { "name": "M82A3" , "category": "SniperRifle" , "unlock": 27},"3127": { "name": "L85A2" , "category": "AssaultRifle" , "unlock": 27},"3128": { "name": "PKP" , "category": "LMG" , "unlock": 27},"3129": { "name": "G53" , "category": "SMG" , "unlock": 27},"3130": { "name": "MK3A1" , "category": "Shotgun" , "unlock": 27},"3131": { "name": "93R" , "category": "Pistol" , "unlock": 0},"3132": { "name": "ACWR" , "category": "AssaultRifle" , "unlock": 28},"3133": { "name": "A91" , "category": "AssaultRifle" , "unlock": 30},"3134": { "name": "LSAT" , "category": "LMG" , "unlock": 30},"3135": { "name": "L86A2" , "category": "LMG" , "unlock": 28},"3136": { "name": "MTAR21" , "category": "SMG" , "unlock": 30},"3137": { "name": "M5K" , "category": "SMG" , "unlock": 28},"3138": { "name": "M98B" , "category": "SniperRifle" , "unlock": 30},"3139": { "name": "JNG90" , "category": "SniperRifle" , "unlock": 28},"3140": { "name": "Khukri" , "category": "CQC" , "unlock": 30},"8000": { "name": "Adrenaline Shot" , "category": "Gadget" , "unlock": 0},"8002": { "name": "Field Bandage" , "category": "Gadget" , "unlock": 0},"8003": { "name": "Advanced Adrenaline Shot" , "category": "Gadget" , "unlock": 0},"8004": { "name": "Combat Bandage" , "category": "Gadget" , "unlock": 0}}
		self.attachements = {"4000": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4001": { "name": "CQC Ammo" , "category": "Ammo" , "unlock": 8}, "4002": { "name": "Balanced Stock" , "category": "Stock" , "unlock": 11}, "4003": { "name": "Stand-off Barrel" , "category": "Barrel" , "unlock": 9}, "4005": { "name": "Holographic sight" , "category": "Scope" , "unlock": 7}, "4006": { "name": "Holographic sight" , "category": "Scope" , "unlock": 7}, "4007": { "name": "Holographic sight" , "category": "Scope" , "unlock": 7}, "4008": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4009": { "name": "Standard Sniper Scope" , "category": "Scope" , "unlock": 0}, "4010": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4011": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4012": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4013": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4014": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4015": { "name": "Standard Marksman Scope" , "category": "Scope" , "unlock": 0}, "4016": { "name": "Standard Marksman Scope" , "category": "Scope" , "unlock": 0}, "4017": { "name": "Close-in Barrel" , "category": "Barrel" , "unlock": 6}, "4018": { "name": "Precision Barrel" , "category": "Barrel" , "unlock": 19}, "4019": { "name": "Heavy Barrel" , "category": "Barrel" , "unlock": 14}, "4020": { "name": "Soft Point Ammo" , "category": "Ammo" , "unlock": 2}, "4021": { "name": "Hi-Power Ammo" , "category": "Ammo" , "unlock": 20}, "4022": { "name": "Casket Mags" , "category": "Ammo" , "unlock": 15}, "4023": { "name": "High Capacity Mags" , "category": "Ammo" , "unlock": 18}, "4024": { "name": "Extra Magazines" , "category": "Ammo" , "unlock": 3}, "4025": { "name": "Precision Stock" , "category": "Stock" , "unlock": 5}, "4026": { "name": "Tactical Stock" , "category": "Stock" , "unlock": 16}, "4027": { "name": "Stand-off Barrel" , "category": "Barrel" , "unlock": 9}, "4028": { "name": "Close-in Barrel" , "category": "Barrel" , "unlock": 6}, "4029": { "name": "Precision Barrel" , "category": "Barrel" , "unlock": 19}, "4030": { "name": "Heavy Barrel" , "category": "Barrel" , "unlock": 14}, "4031": { "name": "CQC Ammo" , "category": "Ammo" , "unlock": 8}, "4032": { "name": "Soft Point Ammo" , "category": "Ammo" , "unlock": 2}, "4033": { "name": "Hi-Power Ammo" , "category": "Ammo" , "unlock": 20}, "4034": { "name": "Casket Mags" , "category": "Ammo" , "unlock": 15}, "4035": { "name": "High Capacity Mags" , "category": "Ammo" , "unlock": 18}, "4036": { "name": "Extra Magazines" , "category": "Ammo" , "unlock": 3}, "4037": { "name": "Balanced Stock" , "category": "Stock" , "unlock": 11}, "4038": { "name": "Precision Stock" , "category": "Stock" , "unlock": 5}, "4039": { "name": "Tactical Stock" , "category": "Stock" , "unlock": 16}, "4040": { "name": "Stand-off Barrel" , "category": "Barrel" , "unlock": 9}, "4041": { "name": "Close-in Barrel" , "category": "Barrel" , "unlock": 6}, "4042": { "name": "Precision Barrel" , "category": "Barrel" , "unlock": 19}, "4043": { "name": "Heavy Barrel" , "category": "Barrel" , "unlock": 14}, "4044": { "name": "CQC Ammo" , "category": "Ammo" , "unlock": 8}, "4045": { "name": "Soft Point Ammo" , "category": "Ammo" , "unlock": 2}, "4046": { "name": "Hi-Power Ammo" , "category": "Ammo" , "unlock": 20}, "4047": { "name": "Casket Mags" , "category": "Ammo" , "unlock": 15}, "4048": { "name": "High Capacity Mags" , "category": "Ammo" , "unlock": 18}, "4049": { "name": "Extra Magazines" , "category": "Ammo" , "unlock": 3}, "4050": { "name": "Precision Stock" , "category": "Stock" , "unlock": 5}, "4051": { "name": "Balanced Stock" , "category": "Stock" , "unlock": 11}, "4052": { "name": "Tactical Stock" , "category": "Stock" , "unlock": 16}, "4053": { "name": "Stand-off Barrel" , "category": "Barrel" , "unlock": 9}, "4054": { "name": "Close-in Barrel" , "category": "Barrel" , "unlock": 5}, "4055": { "name": "Precision Barrel" , "category": "Barrel" , "unlock": 19}, "4056": { "name": "Heavy Barrel" , "category": "Barrel" , "unlock": 14}, "4057": { "name": "CQC Ammo" , "category": "Ammo" , "unlock": 2}, "4058": { "name": "Soft Point Ammo" , "category": "Ammo" , "unlock": 11}, "4059": { "name": "Hi-Power Ammo" , "category": "Ammo" , "unlock": 21}, "4060": { "name": "Casket Mags" , "category": "Ammo" , "unlock": 3}, "4061": { "name": "High Capacity Mags" , "category": "Ammo" , "unlock": 16}, "4062": { "name": "Extra Magazines" , "category": "Ammo" , "unlock": 8}, "4063": { "name": "Precision Stock" , "category": "Stock" , "unlock": 15}, "4064": { "name": "Tactical Stock" , "category": "Stock" , "unlock": 12}, "4065": { "name": "Stabilized Stock" , "category": "Stock" , "unlock": 21}, "4066": { "name": "Stabilized Stock" , "category": "Stock" , "unlock": 21}, "4067": { "name": "Stabilized Stock" , "category": "Stock" , "unlock": 21}, "4068": { "name": "Stabilized Stock" , "category": "Stock" , "unlock": 20}, "4069": { "name": "Standard Marksman Scope" , "category": "Scope" , "unlock": 0}, "4070": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4071": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4072": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4073": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4074": { "name": "Standard Sharpshooter Scope" , "category": "Scope" , "unlock": 0}, "4075": { "name": "Standard Sharpshooter Scope" , "category": "Scope" , "unlock": 0}, "4076": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4077": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4102": { "name": "Elite Legacy Holo Sight" , "category": "Scope" , "unlock": 0}, "4139": { "name": "M145" , "category": "Scope" , "unlock": 12}, "4140": { "name": "M145" , "category": "Scope" , "unlock": 10}, "4141": { "name": "M145" , "category": "Scope" , "unlock": 12}, "4142": { "name": "Elite Legacy Holo Sight" , "category": "Scope" , "unlock": 0}, "4180": { "name": "M145" , "category": "Scope" , "unlock": 12}, "4181": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4182": { "name": "Predator Barrel" , "category": "Barrel" , "unlock": 23}, "4220": { "name": "Standard Sniper Scope" , "category": "Scope" , "unlock": 0}, "4221": { "name": "Ballistic RangeAce" , "category": "Scope" , "unlock": 24}, "4222": { "name": "Desert M145" , "category": "Scope" , "unlock": 17}, "4223": { "name": "Elite Legacy Enhanced Scope" , "category": "Scope" , "unlock": 0}, "4239": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4240": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4241": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4242": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4243": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4244": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4245": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4246": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4247": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4248": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4249": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4250": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4251": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4252": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4253": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4254": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4255": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4256": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4257": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4258": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4259": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4260": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4261": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4262": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4263": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4264": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4265": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4266": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4267": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4268": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4269": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4270": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4271": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4272": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4273": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4274": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4276": { "name": "Standard Sharpshooter Scope" , "category": "Scope" , "unlock": 0}, "4277": { "name": "Standard Marksman Sight" , "category": "Scope" , "unlock": 0}, "4278": { "name": "Standard Marksman Scope" , "category": "Scope" , "unlock": 0}, "4279": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4294": { "name": "Veteran Legacy Iron Sight" , "category": "Scope" , "unlock": 0}, "4295": { "name": "Elite Legacy Iron Sight" , "category": "Scope" , "unlock": 0}, "4298": { "name": "Veteran Legacy Iron Sight" , "category": "Scope" , "unlock": 0}, "4299": { "name": "Elite Legacy Iron Sight" , "category": "Scope" , "unlock": 0}, "4301": { "name": "Elite Legacy Iron Sight" , "category": "Scope" , "unlock": 0}, "4302": { "name": "Elite Legacy Scope" , "category": "Scope" , "unlock": 0}, "4303": { "name": "Veteran Legacy Scope" , "category": "Scope" , "unlock": 0}, "4304": { "name": "Veteran Legacy Scope" , "category": "Scope" , "unlock": 0}, "4306": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4307": { "name": "Holographic sight" , "category": "Scope" , "unlock": 6}, "4309": { "name": "Desert Paint Job" , "category": "Skin" , "unlock": 9}, "4310": { "name": "Desert Paint Job" , "category": "Skin" , "unlock": 9}, "4311": { "name": "Desert Holographic Sight" , "category": "Scope" , "unlock": 10}, "4312": { "name": "Desert Paint Job" , "category": "Skin" , "unlock": 23}, "4313": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4314": { "name": "Desert Paint Job" , "category": "Skin" , "unlock": 23}, "4315": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4316": { "name": "Predator Barrel" , "category": "Barrel" , "unlock": 23}, "4317": { "name": "Predator Barrel" , "category": "Barrel" , "unlock": 23}, "4318": { "name": "Predator Barrel" , "category": "Barrel" , "unlock": 23}, "4319": { "name": "Viper Mags" , "category": "Ammo" , "unlock": 24}, "4320": { "name": "Viper Mags" , "category": "Ammo" , "unlock": 24}, "4321": { "name": "Viper Mags" , "category": "Ammo" , "unlock": 24}, "4322": { "name": "Viper Mags" , "category": "Ammo" , "unlock": 24}, "4323": { "name": "Thunderbolt Stock" , "category": "Stock" , "unlock": 25}, "4324": { "name": "Thunderbolt Stock" , "category": "Stock" , "unlock": 25}, "4325": { "name": "Thunderbolt Stock" , "category": "Stock" , "unlock": 25}, "4326": { "name": "Thunderbolt Stock" , "category": "Stock" , "unlock": 25}, "4327": { "name": "Desert Ballistic Scope" , "category": "Scope" , "unlock": 23}, "4328": { "name": "Desert M145" , "category": "Scope" , "unlock": 17}, "4329": { "name": "PSO-1 SVD" , "category": "Scope" , "unlock": 4}, "4330": { "name": "Panthera RangeAce" , "category": "Scope" , "unlock": 11}, "4331": { "name": "Vulcan RangeAce" , "category": "Scope" , "unlock": 21}, "4332": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4333": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4334": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4335": { "name": "RapidAim RedDot" , "category": "Scope" , "unlock": 19}, "4336": { "name": "RapidAim RedDot" , "category": "Scope" , "unlock": 17}, "4337": { "name": "RapidAim RedDot" , "category": "Scope" , "unlock": 19}, "4338": { "name": "RapidAim RedDot" , "category": "Scope" , "unlock": 19}, "4339": { "name": "Vulcan DeadEye" , "category": "Scope" , "unlock": 22}, "4340": { "name": "Panthera DeadEye" , "category": "Scope" , "unlock": 13}, "4341": { "name": "PSO-1 Simonov" , "category": "Scope" , "unlock": 8}, "4342": { "name": "Barrakuda Barrel" , "category": "Barrel" , "unlock": 10}, "4344": { "name": "Barrakuda Stock" , "category": "Stock" , "unlock": 14}, "4347": { "name": "Barrakuda Barrel" , "category": "Barrel" , "unlock": 10}, "4348": { "name": "Barrakuda Barrel" , "category": "Barrel" , "unlock": 10}, "4350": { "name": "Barrakuda Stock" , "category": "Stock" , "unlock": 14}, "4351": { "name": "Barrakuda Barrel" , "category": "Barrel" , "unlock": 10}, "4353": { "name": "Ballistic DeadEye" , "category": "Scope" , "unlock": 25}, "4354": { "name": "Nimrod Mags" , "category": "Ammo" , "unlock": 13}, "4355": { "name": "Nimrod Mags" , "category": "Ammo" , "unlock": 13}, "4356": { "name": "Nimrod Mags" , "category": "Ammo" , "unlock": 13}, "4357": { "name": "Nimrod Mags" , "category": "Ammo" , "unlock": 13}, "4358": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4359": { "name": "Jungle Paint Job" , "category": "Skin" , "unlock": 9}, "4360": { "name": "Jungle Paint Job" , "category": "Skin" , "unlock": 22}, "4361": { "name": "Jungle Paint Job" , "category": "Skin" , "unlock": 18}, "4362": { "name": "Jungle Paint Job" , "category": "Skin" , "unlock": 17}, "4364": { "name": "Jungle PSO-1 SVD" , "category": "Scope" , "unlock": 7}, "4366": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4367": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4368": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4369": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4370": { "name": "Scorpio Barrel" , "category": "Barrel" , "unlock": 24}, "4371": { "name": "Piranha Mags" , "category": "Ammo" , "unlock": 25}, "4372": { "name": "Nemesis Stock" , "category": "Stock" , "unlock": 23}, "4373": { "name": "Scorpio Barrel" , "category": "Barrel" , "unlock": 24}, "4374": { "name": "Scorpio Barrel" , "category": "Barrel" , "unlock": 24}, "4375": { "name": "Scorpio Barrel" , "category": "Barrel" , "unlock": 24}, "4376": { "name": "Piranha Mags" , "category": "Ammo" , "unlock": 25}, "4377": { "name": "Piranha Mags" , "category": "Ammo" , "unlock": 25}, "4378": { "name": "Piranha Mags" , "category": "Ammo" , "unlock": 25}, "4379": { "name": "Nemesis Stock" , "category": "Stock" , "unlock": 23}, "4380": { "name": "Nemesis Stock" , "category": "Stock" , "unlock": 23}, "4381": { "name": "Nemesis Stock" , "category": "Stock" , "unlock": 23}, "4382": { "name": "Standard Marksman Scope" , "category": "Scope" , "unlock": 0}, "4383": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4384": { "name": "Copperhead Barrel" , "category": "Barrel" , "unlock": 17}, "4386": { "name": "Stingray Mags" , "category": "Ammo" , "unlock": 22}, "4388": { "name": "Cerberus Stock" , "category": "Stock" , "unlock": 20}, "4390": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4391": { "name": "Copperhead Barrel" , "category": "Barrel" , "unlock": 17}, "4393": { "name": "Stingray Mags" , "category": "Ammo" , "unlock": 22}, "4395": { "name": "Cerberus Stock" , "category": "Stock" , "unlock": 20}, "4397": { "name": "Copperhead Barrel" , "category": "Barrel" , "unlock": 17}, "4399": { "name": "Stingray Mags" , "category": "Ammo" , "unlock": 22}, "4401": { "name": "Cerberus Stock" , "category": "Stock" , "unlock": 20}, "4403": { "name": "Copperhead Barrel" , "category": "Barrel" , "unlock": 17}, "4404": { "name": "Sidewinder Barrel" , "category": "Barrel" , "unlock": 12}, "4405": { "name": "Stingray Mags" , "category": "Ammo" , "unlock": 20}, "4406": { "name": "Sidewinder Mags" , "category": "Ammo" , "unlock": 15}, "4407": { "name": "Cerberus Stock" , "category": "Stock" , "unlock": 22}, "4409": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4410": { "name": "Standard Sniper Scope" , "category": "Scope" , "unlock": 0}, "4411": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4412": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4413": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4414": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4415": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4416": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4417": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4418": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4419": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4420": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4421": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4422": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4423": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4424": { "name": "Standard Iron Sight" , "category": "Scope" , "unlock": 0}, "4425": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4426": { "name": "Standard Super Sniper Scope" , "category": "Scope" , "unlock": 0}, "4427": { "name": "Standard Sharpshooter Scope" , "category": "Scope" , "unlock": 0}, "4428": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, "4429": { "name": "Regular Paint Job" , "category": "Skin" , "unlock": 0}, }
	def getAttachmentByID(self,id):
		if str(id) in self.attachements:
			return self.attachements[str(id)]
		else:
			return False

