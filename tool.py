#!/usr/bin/python
# -*- coding: utf-8 -*-
#Required dependencies.
import os,time,threading,urllib,json,rcon # <---  RCON CLASS

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
		'ip': "00.000.00.00",
		'port': 0000,
		'password': 'XXXXXXXX',
		'serverName': "SomeServer"
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
	"joinMessage":  "Welcome on cf-tools 24/7! Please read the rules",
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
global toolConfig,currentFetched,toBeFetched,chatBuffer,adminChatBuffer
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
		self.logsDB  = dbConnector.logsDB()
		self.running = True
	def run(self):
		while self.running  == True:
			self.referenceTime = int(time.time())
			prePlayers = self.rcon.getPlayers()
			if  prePlayers != False:
				prePlayers = prePlayers.split("\r")
				for player in prePlayers:
					player = player.split("\t")
					print player
			time.sleep(1)
playerWatcher = fetchPlayers()
playerWatcher.setDaemon(True)
playerWatcher.start()