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
import os,time,threading,urllib,json,util,rcon # <---  RCON CLASS
global toolConfig,currentFetched,toBeFetched,chatBuffer,adminChatBuffer
print "██████████████████████████████████████████████████████████████████████████████████████████████████████████████████"
print "█																											 	 █"
print "█  ██████╗███████╗     █████╗ ██╗   ██╗████████╗ ██████╗ ██╗  ██╗██╗ ██████╗██╗  ██╗    ██████╗ ██╗  ██╗███████╗ █"
print "█ ██╔════╝██╔════╝    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██║ ██╔╝██║██╔════╝██║ ██╔╝    ██╔══██╗██║  ██║██╔════╝ █"
print "█ ██║     █████╗      ███████║██║   ██║   ██║   ██║   ██║█████╔╝ ██║██║     █████╔╝     ██████╔╝███████║█████╗   █"
print "█ ██║     ██╔══╝      ██╔══██║██║   ██║   ██║   ██║   ██║██╔═██╗ ██║██║     ██╔═██╗     ██╔═══╝ ╚════██║██╔══╝   █"
print "█ ╚██████╗██║         ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██╗██║╚██████╗██║  ██╗    ██║          ██║██║      █"
print "█  ╚═════╝╚═╝         ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝          ╚═╝╚═╝      █"
print "█																										 		 █"    
print "██████████████████████████████████████████████████████████████████████████████████████████████████████████████████"
#Dat fancy text-art

toolConfig = {
	"id":  0,
	"connectionInfo": {
		'ip': "RCON IP",
		'port': RCON PORT,
		'password': 'RCON PW',
		'serverName': "Servername will go here"
	},
	"maxPing": 350,
	"vipProtections": { 

		'levelLimiter'         : False ,

		
		'forbiddenAttachements': False ,
		'preboughtAttachements': False ,

		'forbiddenWeapons'     : False ,
		'preboughtWeapons'     : False ,  


		'pingLimiter'          : False ,  

		'classLimiter'         : True  ,  
	},
	"joinMessage":  "%NAME%, welcome on %SERVERNAME%! Please read the rules",
	"statsMessage": " |ccc| Hello /tags/  |ccc|  /name/  |ccc| , Kills |ccc| /kills/ |ccc| || Deaths |ccc| /deaths/ |ccc| || Your K/D Ratio |ccc| /KD/ |ccc|  || Ping: |ccc| /pingAvg/ |ccc| || Have fun playing.",
	"ingameCmds": {
		"test"  : { "action":"sayPrivate", "requiredRights": "50" , "text": "Some defined text 2"   }, 
		"b"     : { "action":"banPlayer" , "requiredRights": "50" , "text": "Some defined text 2"   }, 
		"ping"  : { "action":"printPing" , "requiredRights":  "0" 									}, 
		"k"     : { "action":"kickPlayer", "requiredRights":  "0"  									}, 
		"tomato": { "action":"sayPublic" , "requiredRights": "50" , "text": "######################"},
		"exit"  : { "action": "exitTool" , "requiredRights": "75"									}
	},
	"ranks" : {
	 "2851071969": 50 
	},
	"clanTagDetection": [
		["(",")"],
		["[","]"],
		["-","-"],
		["{","}"],
		["=","="],
	],
	"kickSystem": {
		"kickDelay": 3
	},
	"weaponLimiter": {
		'prebuyProtection' : {
			'weapons': [],
			'attachments': [],
			'tolerance': 0
		},
		'forbiddenItems' : {
			'weapons': [],
			'attachments': [],
		}
	},
	"classLimiter": {
		'current': {
			'US': {
				"Recon": [], 
				"Medic": [], 
				"Engineer": [], 
				"Assault": [], 
			},
			'RU': {
				"Recon": [], 
				"Medic": [], 
				"Engineer": [], 
				"Assault": [], 
			},
		},
		'max': {
				"Recon": 16, 
				"Medic": 16, 
				"Engineer": 16, 
				"Assault": 16, 
		}
	},
	"levelLimiter": {
		"maxlevel" : 30,
		"minlevel" : -1
	},
	"bans" : [
		{ "profileID": 00000000000, "reason": "ban reason" , "expires": 1410380262 , "by": "some Admin" , "type": "Ingame" },
	],

}

currentFetched = {}
toBeFetched = {}
chatBuffer = []
adminChatBuffer = []

class fetchPlayers(threading.Thread):
	def __init__(self): 
		threading.Thread.__init__(self) 
		self.firstRun = True 
		self.iterationCount = 0
		self.debug = False
		self.rcon = rcon.RCON(toolConfig["connectionInfo"])
		self.Support = rcon.Support()
		self.running = True
	###############################
	#  PLAYER UTILITY FUNCTIONS   #
	###############################
	def replaceWithToolVars(self,player,string):
		print string
		string = string.replace("%KILLS%",str(player['game']['kills']))
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
		string = string.replace("%SERVERNAME%",toolConfig['connectionInfo']['serverName'])
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
		pass
	def onLoadoutReceived(self,player):
		pass
	def onPlayerFinishedLoading(self,player):
		self.rcon.sendChatPrivateByID(player['profile']['slot'],self.replaceWithToolVars(player,toolConfig['joinMessage']))
	def onPlayerKicked(self,player):
		pass
	
	def run(self):
		while self.running  == True:
			startTime = time.clock()
			self.referenceTime = int(time.time())
			prePlayers = self.rcon.getPlayers()
			if  prePlayers != False:
				prePlayers = prePlayers.split("\r")
				for player in prePlayers:
					player = player.split("\t")
					if len(player) == 48:
						if not player[47] in currentFetched:
							if "US" in player[34]:
								team = "US"
							else:
								team = "RU"
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
							if "Assault" in player[34]:
								playerClass = "Assault"
							elif "Recon" in player[34]:
								playerClass = "Recon"
							elif "Medic" in player[34]:
								playerClass = "Medic"
							elif "Engineer" in player[34]:
								playerClass = "Engineer"
							else:
								playerClass = "Unknown"
							if player[35] == "0":
								vip =  False
								rights = 0
							else:
								vip = True
								rights = 10
							for person in toolConfig["ranks"]:
								if int(player[47]) == person:
									rights = rights+toolConfig["ranks"][person]
							currentFetched[player[47]] = {
								"profile": {
									"profileID": int(player[47]),
									"nucleusID": int(player[10]),
									"name": player[1],
									"slot": int(player[0]),
									"rank": int(player[39]),
									"class": playerClass,
									"rights": rights,
									"clanTag": resultClanName,
									"vip": vip

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
									"team": team
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
						else:
							playerInMemory = currentFetched[player[47]]

							######################################
							# Check if player is in kickin phase #
							######################################

							if playerInMemory['kickStatus'] == True:
								if playerInMemory['kickTime'] == 0:
									self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],playerInMemory['kickReason'])
									playerInMemory['kickTime'] = toolConfig['kickSystem']['kickDelay']
								elif playerInMemory['kickTime'] == 1:
									self.rcon.kickPlayerInstant(playerInMemory['profile']['slot'])
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
									##
									# Player finished loading...
									##
									self.onPlayerFinishedLoading(playerInMemory)


									playerInMemory['time']['connectedLastCycle'] =  True
								playerInMemory['time']['connected'] =  True
							
							currentFetched[playerInMemory['profile']['profileID']] = playerInMemory



									




			for player in currentFetched.keys():
				if currentFetched[player]['time']['updated'] < self.referenceTime:
					##
					# Do something when player leaves here.
					##
					self.onPlayerDisconnect(currentFetched[player])
					del currentFetched[player]
			print(time.clock() - startTime)
			time.sleep(1)
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