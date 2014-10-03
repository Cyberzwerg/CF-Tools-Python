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

import sys,os,time,threading,urllib,json

import util # <---  UTIL MODULE
import rcon # <---  RCON MODULE
import limiters
global toolConfig,currentFetched,toBeFetched,chatBuffer,adminChatBuffer,configName
configName = ""
##
##	YOU CAN DETERMINE THE USED CONFIG FROM THE toolConfig.json BY using python tool.py -c <configName>
##
configName = "server1"
if len(sys.argv) > 1:
	if sys.argv[1] == "-c":
		configName = sys.argv[2]	
		
#Loading config
try:
	json_data=open("toolConfig.json").read()
	toolConfig = json.loads(json_data)[configName]
except:
	print "Configuration file corrupted."
####
#### INITITIALIZATION OF GLOBAL VARS
####

currentFetched = {}
toBeFetched = {}
chatBuffer = []
adminChatBuffer = []

####
#### CORE CLASS ITERATING OVER PLAYERS
####

class fetchPlayers(threading.Thread):
	def __init__(self): 
		threading.Thread.__init__(self) 
		self.firstRun = True 
		self.debug = False
		self.rcon = rcon.RCON(toolConfig["connectionInfo"])
		self.Support = rcon.Support()
		self.running = True

		self.classLimiter = limiters.classLimiter(toolConfig['classLimiter'],toolConfig['vipProtections']['classLimiter'])

		self.levelLimiter = limiters.levelLimiter(toolConfig['levelLimiter'],toolConfig['vipProtections']['levelLimiter'])

	###############################
	#  PLAYER UTILITY FUNCTIONS   #
	###############################
	def replaceWithToolVars(self,player,string):
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
	def willCheck(self,limiter,vipStatus):
		if  toolConfig["vipProtections"][limiter] == True:
			if vipStatus == True:
				return False
			else:
				return True
		else:
			return True
	##############################
	#   "EVENT HANDLERS" BELOW   #
	##############################
	def onPlayerDisconnect(self,player):
		print player['profile']['name']+" left"
		self.classLimiter.removePlayer(player)
		
	def onLoadoutReceived(self,player):
		pass
	def onPlayerFinishedLoading(self,player):
		self.classLimiter.checkPlayer(player)
		self.levelLimiter.checkPlayer(player)
		self.rcon.sendChatPrivateByID(player['profile']['slot'],self.replaceWithToolVars(player,toolConfig['joinMessage']))
	def onPlayerKicked(self,player):
		pass
	def run(self):

		print "Running core Player daemon"

		while self.running  == True:
			startTime = time.clock()
			self.referenceTime = int(time.time())
			prePlayers = self.rcon.getPlayers()
			if  prePlayers != False:
				prePlayers = prePlayers.split("\r")
				for player in prePlayers:
					player = player.split("\t")
					if len(player) == 48:
						if not int(player[47]) in currentFetched:
							
							resultClanName = "none"
							for clanTag in toolConfig['clanTagDetection']:
								if player[1][0] == clanTag[0]:
									clanTagExplode = player[1].split(clanTag[0])
									clanName = clanTagExplode[1].split(clanTag[1])[0]
									if len(clanName) < 5:
										resultClanName = clanName
										print player[1]+" has clanTag "+clanName
									else:
										resultClanName = "none"
							tags = ""
							if player[35] == "0":
								vip =  False
							else:
								vip = True
								tags = "[VIP]"
							rights = 0
							for group in toolConfig['ingameRights']:
								if str(player[47]) in toolConfig['ingameRights'][group]['members']:
									rights = int(toolConfig['ingameRights'][group]['rights'])
									tags = tags+"["+toolConfig['ingameRights'][group]['tag']+"]"
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
								"kickReason": "You are being kicked! F0 o l"
							}
							toBeFetched[int(player[47])] = fetchPlayerData(int(player[47]),int(player[10]))
							toBeFetched[int(player[47])].setDaemon(True)
							toBeFetched[int(player[47])].start()
						else:
							playerInMemory = currentFetched[int(player[47])]
							
							######################################
							# Check if player is in kickin phase #
							######################################

							if playerInMemory['kickStatus'] == True:
								if playerInMemory['kickTime'] == 0:
									self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],playerInMemory['kickReason'])
									playerInMemory['kickTime'] = int(toolConfig['kickSystem']['kickDelay'])
								elif playerInMemory['kickTime'] == 1:
									pass
									#self.rcon.kickPlayerInstant(playerInMemory['profile']['slot'])
								else:
									playerInMemory['kickTime'] += -1


										
							
							######################################
							# Apply any changes to global object #
							######################################
							if "US" in player[34]:
								team = "US"
							else:
								team = "RU"

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
							if util.convertToBool(player[4]):
								if playerInMemory['time']['connectedLastCycle'] == False:
									if "US" in player[34]:
										playerInMemory['game']['team'] = "US"
									else:
										playerInMemory['game']['team'] = "RU"
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
									if playerInMemory['game']['deaths'] > 0:
										playerInMemory['game']['KD'] = round(playerInMemory['game']['kills']/playerInMemory['game']['deaths'],2)
									else:
										playerInMemory['game']['KD'] = str(playerInMemory['game']['kills'])+".00"
									self.onPlayerFinishedLoading(playerInMemory)


									playerInMemory['time']['connectedLastCycle'] =  True
								playerInMemory['time']['connected'] =  True
								if int(time.time()) % int(toolConfig['statsMessageFrequency']) == 0:
									self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],self.replaceWithToolVars(playerInMemory,str(toolConfig['statsMessage'])))	
							
							######################################
							# Detect if loadout was just fetched #
							######################################
							if  playerInMemory['checkMe'] == True:
								

								playerInMemory['checkMe'] = False

							currentFetched[int(playerInMemory['profile']['profileID'])] = playerInMemory



									


			for player in currentFetched.keys():
				
				if currentFetched[int(player)]['time']['updated'] < self.referenceTime:

					self.onPlayerDisconnect(currentFetched[player])
					del currentFetched[int(player)]
			#print(time.clock() - startTime)
			

			time.sleep(1)
class fetchPlayerData(threading.Thread):
	def __init__(self,profileID,nucleusID): 
		threading.Thread.__init__(self) 
		self.profileID = profileID
		self.nucleusID = nucleusID
	def getJson(self,url):
		response = urllib.urlopen(url);
		return json.loads(response.read())

	def run(self):
		tempLoadout = self.getJson("http://battlefield.play4free.com/en/profile/loadout/"+str(self.profileID)+"/"+str(self.nucleusID))
		tempLoadout = tempLoadout['data']
   		currentFetched[self.profileID]['loadout']['weapons'] = tempLoadout['equipment']
   		currentFetched[self.profileID]['loadout']['apparel'] = tempLoadout['apparel']

   		soldiers = self.getJson("http://battlefield.play4free.com/en/profile/soldiers/"+str(self.profileID))['data']
   		for soldier in soldiers: 
   			if int(soldier['id']) == int(self.nucleusID): 
				currentFetched[int(self.profileID)]['isMain'] = soldier['isMain']
				currentFetched[int(self.profileID)]['level']  = soldier['level']
				currentFetched[int(self.profileID)]['mugShot'] = soldier['mugShot']
				currentFetched[int(self.profileID)]['xpForNextLevel'] = soldier['xpForNextLevel']
		currentFetched[self.profileID]['checkMe'] = True
playerWatcher = fetchPlayers()
playerWatcher.setDaemon(True)
playerWatcher.start()
while True:
	try:
		time.sleep(21023)
	except:
		os.system("clear")
		print "Exiting..."
		raise SystemExit