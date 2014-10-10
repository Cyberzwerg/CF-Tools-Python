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

#Import libs that are needed!
import sys,os,time,threading,urllib,json

import util 	# <---  UTIL MODULE
import rcon 	# <---  RCON MODULE
import limiters # <--- IMPORT CUSTOM LIMITERS

#Instantiate globals 
global toolConfig,currentFetched,toBeFetched,chatBuffer,adminChatBuffer,configName

def loadConfig():
	#Set default config name to "default"
	configName = "default"
	#Check if arguments were defined
	if len(sys.argv) > 1:
		#Chekc if the first argument is -c
		if sys.argv[1] == "-c":
			#SetConfig name to the second parameter
			configName = sys.argv[2]	
	else:
		#No config was defined notifying user that there's an option to have multiple

		print "YOU CAN DETERMINE THE USED CONFIG FROM THE toolConfig.json BY USING python tool.py -c <configName>"
	
	#Now try loading the config
	try:
		#Open file 
		json_data=open("toolConfig.json").read()
		#Parse data
		toolConfig = json.loads(json_data)
		#Check if config defined exists
		if configName in toolConfig:
			#set global to be defined config
			toolConfig = toolConfig[configName]
			#Make a path for the logs if it doesnt exist
			if not os.path.exists(configName):
				os.makedirs(configName)
			#Set a property on the toolConfig itself for later use
			toolConfig['configName'] = configName
			#Return the tool-config
			return toolConfig
		else:
			#Unknown tool config
			raise error("Configuration not found in toolConfig.json")
		
	except:
		#Json parse failed
		raise error("Configuration file corrupted.")

####################
#  INITIAL LOADUP  #
####################

toolConfig = loadConfig()
#Global vars default variables
currentFetched = {}
toBeFetched = {}
chatBuffer = []
adminChatBuffer = []


###
###	CORE LOOP 
###
class fetchPlayers(threading.Thread):
	### INIT THE CLASS (no args given)

	def __init__(self): 
		threading.Thread.__init__(self) 
		self.firstRun = True 
		self.debug = False
		#RCON Instance for this thread
		self.rcon = rcon.RCON(toolConfig["connectionInfo"])

		self.Support = rcon.Support()
		
		#Running property will determine if thread keeps running
		self.running = True

		##############################
		# LIMITER INSTANCES GO BELOW #
		##############################

		#create an instance of a class defined in limiter.py ( params are  the config for the limiter and the VIP protection )

		self.classLimiter = limiters.classLimiter(toolConfig['classLimiter'],toolConfig['vipProtections']['classLimiter'])

		self.levelLimiter = limiters.levelLimiter(toolConfig['levelLimiter'],toolConfig['vipProtections']['levelLimiter'])	
																																	
		self.weaponLimiter = limiters.weaponLimiter(toolConfig['weaponLimiter'],toolConfig['vipProtections']['weaponLimiter'])		
																																	
		self.nameFilter = limiters.nameFilter(toolConfig['nameFilter'],toolConfig['vipProtections']['nameFilter'])					
																																	
		self.bans = limiters.bans(toolConfig['bans'])																				



	###############################
	#		 UTILITY FUNCTIONS    #
	###############################

	def replaceWithToolVars(self,player,string):
		#Possible params are: kills,deaths,tags,kd,ping,pingAvg,timesUpdated,class,profileID,clanTag,serverName

		string = string.replace("%KILLS%",str(player['game']['kills']))
		string = string.replace("%KD%",str(player['game']['KD']))
		string = string.replace("%TAGS%",str(player['profile']['tags']))
		string = string.replace("%DEATHS%",str(player['game']['deaths']))
		string = string.replace("%SCORE%",str(player['game']['score']))
		string = string.replace("%PING%",str(player['ping']['current']))
		string = string.replace("%PINGAVG%",str(player['ping']['avg']))
		string = string.replace("%TIMESUPDATED%",str(player['time']['timesUpdated']))
		string = string.replace("%CLASS%",str(player['profile']['class']))
		string = string.replace("%NAME%",str(player['profile']['name']))
		string = string.replace("%PROFILEID%",str(player['profile']['profileID']))
		string = string.replace("%RANK%",str(player['profile']['rank']))
		string = string.replace("%CLANTAG%",str(player['profile']['clanTag']))
		string = string.replace("%SERVERNAME%",self.rcon.serverName)
		return string


	##############################
	#   "EVENT HANDLERS" BELOW   #
	##############################

	#Player disconnected.
	def onPlayerDisconnect(self,player):
		print player['profile']['name']+" left"

		#remove player from classlimiter index

		self.classLimiter.removePlayer(player)
		
	# json from easy arrived!
	def onLoadoutReceived(self,player):
		#check weapon limiter
		self.weaponLimiter.checkPlayer(player)
	def playerOnTeamSwitch(self,player):
		pass
		#Player got team-switched
	def onPlayerFinishedLoading(self,player):
		#check classlimiter
		self.classLimiter.checkPlayer(player)
		#check levelLimiter
		self.levelLimiter.checkPlayer(player)
		#check nameFilter
		self.nameFilter.checkPlayer(player)
		#check Bans
		self.bans.checkPlayer(player)
		#Send join message to player
		self.rcon.sendChatPrivateByID(player['profile']['slot'],self.replaceWithToolVars(player,toolConfig['joinMessage']))

	def onPlayerKicked(self,player):
		#Do something once a player got kicked
		pass
	def run(self):

		print "Running core Player daemon"

		#Check if tool should still be running
		while self.running  == True:
			#Take start time
			startTime = time.clock()
			#Take reference time
			self.referenceTime = int(time.time())
			#Get players via rcon
			prePlayers = self.rcon.getPlayers()
			#Check if result is false (no players)
			if  prePlayers != False:
				#Split up players 
				prePlayers = prePlayers.split("\r")
				#Iterate over players
				for player in prePlayers:
					#Split up the player itself
					player = player.split("\t")
					#Check if player is "valid" (48 attributes)
					if len(player) == 48:
						#Check if player just joined / isnt fetched yet
						if not int(player[47]) in currentFetched:
							#Clan-name detection
							resultClanName = "none"
							for clanTag in toolConfig['clanTagDetection']:
								#Iterate over clantags
								if player[1][0] == clanTag[0]:
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
										resultClanName = "none"
							# Set default value for tags
							tags = ""
							if player[35] == "0":
								#Player is not VIP
								vip =  False
							else:
								#Player is VIP
								vip = True
								#Adding VIP Tag to tags
								tags = "[VIP]"
							#Set default rights to 0
							rights = 0
							#Iterate through groups
							for group in toolConfig['ingameRights']:
								#Check if player is member of group
								if str(player[47]) in toolConfig['ingameRights'][group]['members']:
									#Set rights to rights of group (change to += if you want to add up)
									rights = int(toolConfig['ingameRights'][group]['rights'])
									#Append to tags
									tags += "["+toolConfig['ingameRights'][group]['tag']+"]"
							# Create player dict.
							currentFetched[int(player[47])] = {
								"profile": {
									"profileID": int(player[47]),
									"nucleusID": int(player[10]),
									"name": player[1],
									"slot": int(player[0]),
									"rank": int(player[39]),
									"class": "loading",
									"rights": rights,
									"clanTag": resultClanName,
									"vip": vip,
									"tags": tags

								},
								"time": {
									"fetched": int(time.time()),
									"connectedLastCycle": False,
									"connected": util.convertToBool(player[4]),
									"updated": self.referenceTime,
									"idle": player[41],
									"timesUpdated": 0,
								},
								"game": {
									"kills": int(player[31]),
									"deaths": int(player[36]),
									"score": int(player[37]),
									"flagCaps": int(player[25]),
									"assists": int(player[19]),
									"revives": int(player[22]),
									"team": "loading"
								},
								"ping": {
									"current": int(player[3]),
									"avg": int(player[3]),

								},
								"loadout": {
									"weapons": {},
									"apparel": {},

								},
								"checkMe": False,

								"kickStatus": False,
								"kickTime": 0,
								"kickReason": ""
							}
							#Begin fetching loadout/other API requests
							toBeFetched[int(player[47])] = fetchPlayerData(int(player[47]),int(player[10]))
							toBeFetched[int(player[47])].setDaemon(True)
							toBeFetched[int(player[47])].start()

						else:
							#Playeris already fetched

							#Create a  shorter var for currentFetched[int(player[47])] 
							playerInMemory = currentFetched[int(player[47])]
							

							###############
							# Kick System #
							###############

							if playerInMemory['kickStatus'] == True:
								if playerInMemory['kickTime'] == 0:

									self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],playerInMemory['kickReason'])
									playerInMemory['kickTime'] = int(toolConfig['kickSystem']['kickDelay'])
								elif playerInMemory['kickTime'] == 1:
									self.rcon.kickPlayerInstant(playerInMemory['profile']['slot'])
									#Write to kicklog
									kickInfo = [playerInMemory['profile']['name'],playerInMemory['profile']['profileID'] , playerInMemory['kickReason']  , int(time.time()) ],toolConfig['configName']
									util.log("kick",kickInfo )
								else:
									#Countdown kickTime
									playerInMemory['kickTime'] += -1


							######################################
							# Apply any changes to global object #
							######################################


							if "US" in player[34]:
								team = "US"
							elif "RU" in player[34]:
								team = "RU"
							else:
								team ="Unknown"
							if playerInMemory["game"]["team"] != "Unknown" and team != "Unknown" and team != playerInMemory["game"]["team"]:
								self.playerOnTeamSwitch(playerInMemory)


							playerInMemory['time']['updated'] =  self.referenceTime
							playerInMemory['time']['timesUpdated'] += 1

							playerInMemory['profile']['rank'] = player[39]

							playerInMemory['game']['rank'] = int(player[39])
							playerInMemory['game']['kills'] = int(player[31])
							playerInMemory['game']['deaths'] = int(player[36])
							playerInMemory['game']['score'] = int(player[37])
							playerInMemory['game']['flagCaps'] = int(player[25])
							playerInMemory['game']['assists'] = int(player[19])
							playerInMemory['game']['revives'] = int(player[22])
							playerInMemory['game']['team'] = team



							######################################
							# Detect if player finished loading  #
							######################################

							#Check if player finished loading
							if util.convertToBool(player[4]):
								#Check if player was already loaded
								if playerInMemory['time']['connectedLastCycle'] == False:

									#Determine class
									if "Assault" in player[34]:
										playerInMemory['profile']['class'] = "Assault"
									elif "Recon" in player[34]:
										playerInMemory['profile']['class'] = "Recon"
									elif "Medic" in player[34]:
										playerInMemory['profile']['class'] = "Medic"
									elif "Engineer" in player[34]:
										playerInMemory['profile']['class'] = "Engineer"
									else:
										playerInMemory['profile']['class'] = "Unknown"

									#Calculate KD

									#Prevent division by 0
									if playerInMemory['game']['deaths'] > 0:
										#Calculate K/D
										playerInMemory['game']['KD'] = round(playerInMemory['game']['kills']/playerInMemory['game']['deaths'],2)
									else:
										#KD is kills
										playerInMemory['game']['KD'] = str(playerInMemory['game']['kills'])+".00"
									# Launch playerFinishedLoading event
									self.onPlayerFinishedLoading(playerInMemory)

									# Set connectedLastCycle to true
									playerInMemory['time']['connectedLastCycle'] =  True
								#Set connected to true

								playerInMemory['time']['connected'] =  True

								#Check if statsmessage will be sent 
								if int(time.time()) % int(toolConfig['statsMessageFrequency']) == 0:
									#Send stats message
									self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],self.replaceWithToolVars(playerInMemory,str(toolConfig['statsMessage'])))	
							
							######################################
							# Detect if loadout was just fetched #a
							######################################
							if  playerInMemory['checkMe'] == True:
								#Launch event
								self.onLoadoutReceived(playerInMemory)
								#Prevent re-checking
								playerInMemory['checkMe'] = False

							#currentFetched[int(playerInMemory['profile']['profileID'])] = playerInMemory



									

			#Check if player didnt get updated
			for player in currentFetched.keys():
				#Check if player updatedTime is smaller than referenceTime
				if currentFetched[int(player)]['time']['updated'] < self.referenceTime:
					#Player didnt get updated!
					self.onPlayerDisconnect(currentFetched[player])
					#Remove the player from global dict.
					del currentFetched[int(player)]
			

			time.sleep(1)
		print "Player Deamon stopped!"

#################################################
# THREAD TO FETCH PLAYER DATA FROM EASY 		#
# YOU MAY USE THIS THREAD TO ADD DIFFERENT APIS #
#################################################

class fetchPlayerData(threading.Thread):
	def __init__(self,profileID,nucleusID): 
		threading.Thread.__init__(self) 
		#Set player info in constructor
		self.profileID = profileID
		self.nucleusID = nucleusID
	#Get json function 
	def getJson(self,url):
		response = urllib.urlopen(url);
		return json.loads(response.read())
	#Thread to fetch json stuff!
	def run(self):
		###
		###	RECEIVE LOADOUT
		###
		tempLoadout = self.getJson("http://battlefield.play4free.com/en/profile/loadout/"+str(self.profileID)+"/"+str(self.nucleusID))
		tempLoadout = tempLoadout['data']
		# Apply loadout and apparel to global player dict.
   		currentFetched[self.profileID]['loadout']['weapons'] = tempLoadout['equipment']
   		currentFetched[self.profileID]['loadout']['apparel'] = tempLoadout['apparel']

   		#Get soldiers
   		soldiers = self.getJson("http://battlefield.play4free.com/en/profile/soldiers/"+str(self.profileID))['data']
   		#Iterate over soldiers
   		for soldier in soldiers: 
   			#Get soldier that is currently playing
   			if int(soldier['id']) == int(self.nucleusID): 
   				#Apply properties to global dict.
				currentFetched[int(self.profileID)]['profile']['isMain'] = soldier['isMain']
				currentFetched[int(self.profileID)]['profile']['level']  = soldier['level']
				currentFetched[int(self.profileID)]['profile']['mugShot'] = soldier['mugShot']
				#Will be used for level-up message!
				currentFetched[int(self.profileID)]['profile']['xpForNextLevel'] = soldier['xpForNextLevel']
		#Make sure player will get checked next iteration!
		currentFetched[self.profileID]['checkMe'] = True



########################
# TOOL IS STARTED HERE #
########################

playerWatcher = fetchPlayers()
playerWatcher.setDaemon(True)
playerWatcher.start()


##########################
#  SHELL CMD INTERPRETER #
##########################

while True:
	try:
		userInput = raw_input("\nEnter cmd:\n").lower()
		if userInput == "exit":
			print "Exiting...waiting for dependencies..."
			playerWatcher.running = False
			time.sleep(2)
			print "System going down now!"
			raise SystemExit
		if userInput == "restart":
			print "Restarting...waiting for dependencies..."

			##	STOP CORE THREADS

			playerWatcher.running = False

			##	RELOAD CONFIG!

			time.sleep(2)
			toolConfig = loadConfig()

			##	RESET TO DEFAULT VARS

			currentFetched = {}
			toBeFetched = {}
			chatBuffer = []
			adminChatBuffer = []

			##	RESTART CORE THREADS

			playerWatcher = fetchPlayers()
			playerWatcher.setDaemon(True)
			playerWatcher.start()

		elif userInput == "help" or userInput == "?":
			print "Known commands:"
			print "\t exit - Terminates the tool."
		else:
			print "Unkown cmd! Type help/? for help"
	except:
		raise SystemExit