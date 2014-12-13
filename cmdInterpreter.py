class cmdInterpreter():

	def __init__(self,cmds,rules): 
		self.cmds = cmds
		self.rules = rules
	'''
	
	CHECK IF MESSAGE IS A CMD

	'''
	def checkMessage(self,message,player,players):
		print message
		#Possible triggers
		cmdTriggers = ['!','#','|','>','/','+']

		#Check if first letter of message is a trigger
		if message['message'][0] in cmdTriggers:

			cmdExecuted = message['message'][1:].split(" ")

			cmdExecuted = cmdExecuted[0]

			if cmdExecuted.lower()  in  self.cmds:
				theCmd = self.cmds[cmdExecuted.lower()]

				if theCmd['neededRights'] > player['profile']['rights']:
					self.sendToPlayer("You are not allowed to execute  |ccc| "+message['message']+" ! ",player)	
				else:
					if 	theCmd['cmdAction'] == "kickPlayer":

						self.kickPlayer(player,message,players)

					elif theCmd['cmdAction'] == "printHelp":

						self.printHelp(player)

					elif theCmd['cmdAction'] == "banPlayer":
						
						pass
					elif theCmd['cmdAction'] == "tempBanPlayer":
						pass
					elif theCmd['cmdAction'] == "warnplayer":
						pass
					elif theCmd['cmdAction'] == "sayToPlayer":
						pass
					elif theCmd['cmdAction'] == "globalSay":

						pass
			
			else:
				self.sendToPlayer("Unknown cmd:  |ccc| "+message['message'],player)


	def sendToPlayer(self,message,player):
		print message
		if player['messageToSend'] is list:
			player['messageToSend'].append(message)
		else:
			player['messageToSend'] = [message]

						
	'''

	CMD ACTIONS
	
	'''
	def searchPlayerInCurrentFetched(self,players,searchFor):
		result = []
		for player in players:
			if  searchFor.lower()  in  players[player]['profile']['name'].lower() :
				result.append(players[player])
		return result



	#######################
	# KICK PLAYER BY NAME #
	#######################
	def kickPlayer(self,player,message,players):
		
		cmdMessage = message['message']

		cmdMessage = cmdMessage.split(" ")

		if len(cmdMessage) < 2:
			self.sendToPlayer("Plese specify a target",player)
		
		else:

			cmdTrigger =  cmdMessage[0]

			definedTarget = self.searchPlayerInCurrentFetched(players,cmdMessage[1])
			if len(cmdMessage) < 3:
				reason = "undefined"
			else:
				reason = " ".join(cmdMessage[2:])

			if len(definedTarget) == 1:
				 
				definedTarget[0]['kickStatus'] = True
				definedTarget[0]['kickReason'] = "You got kicked. Reason: |ccc| "+reason


			else:
				self.sendToPlayer("Found "+str(len(definedTarget))+" targets for: "+cmdMessage[1],player)

	#######################
	# PRINT HELP TO PLAYER#
	#######################
	def printHelp(self,player):
		self.sendToPlayer(", ".join(self.rules),player)



