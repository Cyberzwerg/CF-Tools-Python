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
import support  # <--- IMPORT SUPPORT MODULE
import cmdInterpreter #<-- IMPORT CMD INTERPRETER

#Instantiate globals 

#EVERY TOOL IS A THREAD AUTOMATICLY

class Tool(threading.Thread):
	def __init__(self,config):
		threading.Thread.__init__(self) 

		#Save config to the class itself.

		self.config  = config
		self.startTime = time.clock()

		self.prepare()

	def prepare(self):
		#Clean up in case of restart
		try:
			del self.rcon
			del self.playerChatBuffer
			del self.adminChatBuffer
			del self.players
			del self.firstRun
		except:
			pass
		# Make a new RCON instance
		self.rcon = rcon.RCON(self.config["connectionInfo"])

		# Make a new support instance
		self.support = support.Support()


		# Make a new cmdInterpreter instance
		self.cmdInterpreter = cmdInterpreter.cmdInterpreter(self.config["cmds"],self.config['rules'])

		# Define the "global" vars

		self.playerChatBuffer = []
		self.adminChatBuffer = []
		self.players = {}
		self.running = True
		self.firstRun = True



	'''
	EVENTS ARE BELOW 

	USE THESE TO PROVIDE EXTRA FUNCTIONALITY!!

	
	
	'''


	def onPlayerJoin(self,player):
		pass
		print player['profile']['name']+" joined the sever. Rights: "+str(player['profile']['rights'])

	def onPlayerLeave(self,player):
		pass

	def onPlayerLoadoutReceived(self,player):
		pass

	def onPlayerKicked(self,player):
		pass

	def onPlayerChatMessage(self,player,message):
		print player['profile']['name']+": "+str(message['message'])
		self.cmdInterpreter.checkMessage(message,self.players[player['profile']['slot']],self.players)

	def onPlayerTeamSwitch(self,player,fromTeam,toTeam):
		pass








	'''
			TOOL CORE THREAD IS STARTING HERE!

			LET'S GET STARTED!
	'''
	def run(self):
		
		

		while self.running == True:

			#Take time for reference
			self.referenceTime = time.clock()

			#Get players from server.
			prePlayers = self.rcon.getPlayers()


			#Iterate over players
			for player in prePlayers:

				#Check if player is fetched
				if player['slot'] in self.players:

					#Get player from cache (old values)
					playerInMemory = self.players[player['slot']]

					'''
						Kick System:
							-Check if player is in kicking phase
								-yes
									-Check if kick time is 0
										Send kick reason to player
										Set kick time to defined time in config

									-Check if kick time is 1
										-yes
											kick player
										-no
											subtract 1 from kick time
								-no
									skip

					'''
					#Check if player is in kickin phase
					if playerInMemory['kickStatus'] == True:

							#Check if kick time is 0 
							if playerInMemory['kickTime'] == 0:

								#Send kick reason
								self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],playerInMemory['kickReason'])

								#Set kick time to defined time in config
								playerInMemory['kickTime'] = int(self.config['kickSystem']['kickDelay'])

							# Check if kick time is 1
							elif playerInMemory['kickTime'] == 1:

								#Kick player
								self.rcon.kickPlayerInstant(playerInMemory['profile']['slot'])

								#TODO: INSERT KICK LOG

							else:
								
								#Subtract 1 from kick time	
								playerInMemory['kickTime'] += -1

					#Check if user will receive messages
					if playerInMemory['messageToSend'] != False:
						for message in playerInMemory['messageToSend']:
							self.rcon.sendChatPrivateByID(playerInMemory['profile']['slot'],message)
						playerInMemory['messageToSend'] = False;
					#Player just joined
					
				else:
						rights = 0

						if str(player['profileID']) in self.config["rights"]:
							rights =  self.config["rights"][str(player['profileID'])]

						self.players[player['slot']] = {
							"profile": {
									"profileID": player['profileID'],
									"nucleusID": player['nucleusID'],
									"name": player['name'],
									"slot": player['slot'],
									"rank": player['rank'],
									"class": "loading",
									"rights": rights,
									"clanTag": player['clanTag'],
									"vip": player['vip'],

								},
								"time": {
									"fetched": int(time.time()),
									"connectedLastCycle": False,
									"connected": player['connected'],
									"updated": self.referenceTime,
									"idle": player['idle'],
									"timesUpdated": 0,
								},
								"game": {
									"kills": player['kills'],
									"deaths": player['deaths'],
									"score":  player['score'],
									"flagCaps":  player['flagCaps'],
									"assists":  player['damageAssists'],
									"revives":  player['revives'],
									"team": player['team']
								},
								"ping": {
									"current":  player['ping'],
									"avg":  player['ping'],

								},
								"loadout": {
									"weapons": {},
									"apparel": {},

								},
								"checkMe": False,

								"messageToSend": False,
								"kickStatus": False,
								"kickTime": 0,
								"kickReason": ""
						}
						self.onPlayerJoin(self.players[player['slot']])
			'''
	
			CHAT MODULE BELOW


			'''

			#get chat from server
			chat =  self.rcon.getChat()

			#Iterate over player messages
			for playerMessage in chat['player']:

				#check if playerMessage is in buffer
				if not playerMessage in self.playerChatBuffer:
					if self.firstRun == False:
						#Check if player is still ingame
						if playerMessage['slot'] in self.players :

							#Fire event for player that sent message
							self.onPlayerChatMessage(self.players[playerMessage['slot']],playerMessage)

					#Append to chat buffer so it isnt picked up again
					self.playerChatBuffer.append(playerMessage)
			self.firstRun = False
			#Calculate time 
			tookTime = time.clock()-self.referenceTime
			#Sleep for the rest of 1 sec.
			time.sleep(abs( 1-tookTime ))


