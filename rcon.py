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

class RCON:
	def __init__(self,connectionInfo): 
		self.connectionInfo = connectionInfo

		print "Initial Connect."
		self.connect()
	def connect(self):

		#Create a socket
		self.socket = socket.socket()

		#Connect to server
		try:
			self.socket.connect((str(self.connectionInfo['IP']),int(self.connectionInfo['PORT'])))
		except:
			raise Exception("Connection failed! Please check your IP/PORT")
			time.sleep(2)

			#Re-Trying

			self.connect()

		#Connection established.

		#Set timeout of socket. This is used to prevent the program from getting stuck when server is responding with nothing

		self.socket.settimeout(2)
		
		try:
			#Get the welcome message
			welcomeMessage =  self.socket.recv(1024).split(" ")
			self.rconVersion = welcomeMessage[7].replace("\n","")
			#Get the seed which is then digested
			seed =  self.socket.recv(1024).replace("\n","").split(":")[1][1:]

			#Hash seed+password using md5

			digestedPassword = hashlib.md5(seed+self.connectionInfo['PASSWORD']).hexdigest()

			#Send login cmd

			self.socket.send("login "+digestedPassword+"\n")

			#Chekc if response contains key-word "ready"
			if not "ready" in self.socket.recv(1024):

				raise Exception("Authentication failed! Please check your RCON Password.")

				#Closing socket
				self.socket.close()
				#Sleeping 10 seconds
				time.sleep(10)

				#Starting over.
				self.connect()
		except:
			raise Exception("Connection failed! Please check your IP/PORT")

			#Sleep 2 seconds
			time.sleep(2)

			#Starting over

			self.connect()
		#At this point RCON is ready.
		self.serverName = self.getServerDetails()['server']['name']
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

	def convertToBool(self,value):
		if int(value) > 0:
			return True
		else:
			return False
	##########################################
	#Get players
	##########################################

	def getPlayers(self):
		
		#Get players
		prePlayers = self.query("bf2cc pl")
		returnPlayers = []
		#Check if server is empty

		if prePlayers != False:
			
			#Split into players
			prePlayers = prePlayers.split("\r")

			#Iterate over players
			for player in prePlayers:

				#Split up the player itself
				player = player.split("\t")

				#Check if player is "valid" (48 attributes)
				if len(player) == 48:


					'''

					DETERMINE PLAYER CLASS

					'''
					#Possible classes
					possibleClasses = ["Assault","Recon","Medic","Engineer"]

					#Set default class to "Unknown"
					className = "Loading"

					#Iterate over possible classes
					for possbileClass in  possibleClasses:

						#Check class is in current Kit
						if possbileClass in player[34]:
								
							className = possbileClass


					'''

					DETERMINE TEAM

					'''

					#Possible team names
					teamNames = ["US","RU"]

					# Default team-name
					currentTeam = "N/A"

					#Iterate over possible team names
					for teamName in  teamNames:

						#Check if team name is in current kit
						if teamName in player[34]:

							currentTeam = teamName

					'''

					DETERMINE CLAN TAG

					'''

					#Possible clan tags 
					clanTags  = [

				         ["(",")"],
				         ["[","]"],
				         ["-","-"],
				         ["{","}"],
				         ["=","="],
				         ["_=","=_"],
				         ["-=","=-"],
				         ["-=","=-"]

				    ]

				    #Iterate over clanTags
					resultClanName = ""
					for clanTag in clanTags:

						#
						if player[1].startswith(clanTag[0]):

							#Check if first letter of name is the clantags beginning
							clanTagExplode = player[1].split(clanTag[0])
							#Split ip up
							clanName = clanTagExplode[1].split(clanTag[1])[0]
							#Split up by end of clantag
							if len(clanName) < 5:

								#Check if clanName is longer than 5 ( Names like [SomebodyWithAName] will not be detected)
								resultClanName = clanName

							else:
								
								#No clan is defined
								resultClanName = ""

					'''

					DETERMINE WHETHER PLAYER IS VIP

					'''
					if player[35] == "0":

						#Player is not VIP
						vip =  False

					else:
						
						#Player is VIP
						vip = True


					'''
					
					DETERMINE K/D

					'''
					if int(player[36]) < 1:
						kd = int(player[31])
						flawLess = True
					else:
						kd = round(int(player[31])/int(player[36]),2)
						flawLess = False
					#Create temp dict.
					tempPlayer = {

							"profileID": int(player[47]),
							"nucleusID": int(player[10]),

							"cdKeyHash": str(player[42]),

							"ping": int(player[3]),

							"name": str(player[1]),
							"slot": int(player[0]),

							"rank": int(player[39]),
							"class": className,
							"clanTag": resultClanName,
							"vip": self.convertToBool(player[47]),

							"score": int(player[37]),

							"kills": int(player[31]),
							"deaths": int(player[36]),
							"kd": kd,
							"flawLess": flawLess,
							"teamKills": int(player[32]),

							"score": int(player[37]),

							"idle": int(player[41]),
							"connected": self.convertToBool(player[4]),

							"flagCaps": int(player[25]),
							"flagDefends": int(player[26]),
							"flagAssists": int(player[27]),

							"flagNeutralizes": int(player[28]),
							"flagNeutralizeAssists": int(player[29]),


							"assists": int(player[19]),
							"revives": int(player[22]),
							"team": currentTeam,

							"alive": self.convertToBool(player[8]),
							"manDown": self.convertToBool(player[9]),
							"timeToSpawn": str(player[13]),

							"damageAssists": int(player[19]),
							"passengerAssists": int(player[20]),
							"targetAssists": int(player[21]),



					}
					returnPlayers.append(tempPlayer)
			return returnPlayers
		else:
			return returnPlayers
	
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
	##############################
	#Get the current chat Buffer #
	##############################
	def getChat(self):
		finalChat = { 'admin': [] , 'player': []}
		chat = self.query("bf2cc serverchatbuffer").split("\r\r")
		for message in chat:
			message = message.split("\t")
			thisMessage = {}
			if len(message) == 6:
				message = { 'slot': int(message[0].replace("\n","")), 'origin': message[1] , 'time': message[4].replace("[","").replace("]",""), 'message': message[5].strip() }
				if message['origin'] == "Admin":
					finalChat['admin'].append(message)
				else:
					finalChat['player'].append(message)
		return finalChat

	
	##############################
	#          Get VIPS          #
	##############################
	#Mode profileKey|Name 		 #
	##############################

	def getVips(self,mode="profileKey"):
		preVips = self.query("exec game.getVipList")
		finalVips = {}
		if "\t" in preVips:
			preVips = preVips.split("\r")
			for vip in preVips:
				vip =  vip.split("\t")
				if len(vip) > 1:
					name = vip[0]
					profileKey = vip[1]
					if mode == "profileKey":
						finalVips[profileKey] = name
					else:
						finalVips[name] = profileKey
			return finalVips

	###############################
	#Save server settings Settings#
	###############################
	def saveSettings(self):
		self.query("exec sv.setRoundsPerMapSave 1")
		self.query("exec sv.setServerNameSave 1")
		self.query("exec sv.setTicketRatioSave 1")
		self.query("exec sv.VipSlotsSave 1")
		self.query("exec sv.setWelcomeMessageSave 1")
		self.query("exec sv.saveSave")
		self.query("exec sv.save")
		self.query("exec sv.load")
	
	##############################
	#		Send global chat     #
	##############################
	def sendChat(self,message):
		return self.query('exec game.sayAll " |ccc| '+message+'"')


	##############################
	#  Send private Chat by slot #
	##############################
	def sendChatPrivateByID(self,slot,message):
		print 'exec game.sayToPlayerWithId '+str(slot)+' \"'+str(message)+'\"'
		self.query('exec game.sayToPlayerWithId '+str(slot)+' \"'+str(message)+'\"')
		 
	##############################
	#  Kick player instantly  	 #
	##############################

	def kickPlayerInstant(self,slot):
		return self.query('exec admin.kickPlayer '+str(slot))
	##############################
	# Send a message to one team #
	##############################
	def sendTeamChat(self,team,message):
		return self.query('exec game.sayTeam '+team+' '+message)



	##############################
	#		Get banner url       #
	##############################

	def getBannerUrl(self):
		return self.query('exec sv.bannerURL')
	
	##############################
	# Restart Server (30 seconds)#
	##############################

	def restartServer(self):
		self.saveSettings()
		self.query("exec exit")
		time.sleep(31)
		return True

	##############################
	#Pause server (unranked only)#
	##############################

	def pauseServer(self):
		return self.query('bf2cc pause')

	################################
	# Resume server (unranked only)#
	################################
	def resumeServer(self):
		return self.query('bf2cc unpause')

	##############################
	#  Get autobalance status    #
	##############################

	def getAutoBalanceStatus(self):
		if int(self.query("exec sv.autoBalanceTeam")) == 1:
			return True
		else:  
			return False

	##############################
	#     Get ranked status      #
	##############################

	def getRankedStatus(self):
		if int(self.query("exec sv.ranked")) == 1:
			return True
		else:  
			return False



	##############################
	# Restart current Map 		 #
	##############################
	def restartMap(self):
		return self.query("exec admin.restartMap")


	##############################
	# Append map to maprotation  #
	##############################

	def appendMap(self,map,size=32):
		realMap = self.convertCamelCaseToMap(map)
		self.query('exec mapList.append '+realMap['map']+' '+realMap['mode']+' '+str(size))
		return True


	##############################
	# Get current map ID 		 #
	##############################

	def getNextUpMap(self):
		serverDetails = self.getServerDetails()
		if serverDetails['map']['round'] == serverDetails['map']['roundsPerMap']:
			return self.getNextMapInRotation()
		else:
			return serverDetails['map']['name']

	##########################################
	# Get how many rounds are played per map #
	##########################################

	def getRoundsPerMap(self):
		return int(self.query("exec sv.roundsPerMap"))

	###################################
	#Get current map index in map list#
	###################################

	def getCurrentMapID(self):
		return int(self.query('exec maplist.currentMap'))

	##############################
	#Get map rotation 			 #
	##############################

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

	##############################
	#Get current Map 			 #
	##############################

	def getCurrentMap(self):
		currentMapID = self.getCurrentMapID()
		for map in self.getCurrentMapRotation():
			if map['id'] == currentMapID:
				return map

	##############################
	#Get next map in map rotation#
	##############################

	def getNextMapInRotation(self):
		currentMapID = self.getCurrentMapID()+1
		for map in self.getCurrentMapRotation():
			if map['id'] == currentMapID:
				return map

	##########################################
	#Convert camelCase map model to p4f model#
	##########################################
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


	######################################################################
	# Convert ugly play4free map names to camelCase (camelCase rocks!!!) #
	######################################################################

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

	############################################
	# Do an awesome map restart (unranked only)#
	############################################

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



