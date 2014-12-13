class Player():
	def __init__(self,constructData):
		self.p = {
			"profile": {
				"profileID": constructData['profileID'],
				"nucleusID": constructData['nucleusID'],
				"name": constructData['name'],
				"slot": constructData['slot'],
				"rank": constructData['rank'],
				"class": "loading",
				"rights": rights,
				"clanTag": constructData['clanTag'],
				"vip": constructData['vip'],

			},
			"soldiers": [],
			"time": {
				"fetched": int(time.time()),
				"connectedLastCycle": False,
				"connected": constructData['connected'],
				"updated": self.referenceTime,
				"idle": constructData['idle'],
				"timesUpdated": 0,
			},
			"game": {
				"kills": constructData['kills'],
				"deaths": constructData['deaths'],
				"score":  constructData['score'],
				"flagCaps":  constructData['flagCaps'],
				"assists":  constructData['damageAssists'],
				"revives":  constructData['revives'],
				"team": constructData['team']
			},
			"ping": {
				"current":  constructData['ping'],
				"avg":  constructData['ping'],

			},
			"loadout": {
				"weapons": {},
				"apparel": {},
				"checkLoadout": False,

			},
			"messageSystem": {
				"messageToSend": False,
			},
			"kickSystem": {
				"kickInProgress": False,
				"kickTime": 0
			}
		}
	def message(self,message):
		if self.p['messageSystem']['messageToSend'] == False:
			self.p['messageSystem']['messageToSend'] = [message]
		else:
			self.p['messageSystem']['messageToSend'].append(message)



	def kick(self,reason,time):

		self.p['kickSystem']['kickInProgress'] = True
		self.p['kickSystem']['kickTime'] = time


'''
	
	THIS CLASS IS USED TO FETCH PLAYER DATA FROM JSON APIS IN THE BACKGROUND

'''

class fetchPlayerData(threading.Thread):
	def __init__(self,player): 
		threading.Thread.__init__(self) 
		self.profileID = player.p['profile']['profileID']
		self.nucleusID = player.p['profile']['nucleusID']
	#Get json function 
	def getJson(self,url):
		response = urllib.urlopen(url);
		return json.loads(response.read())
	#Thread to fetch json stuff!
	def run(self):

		'''
			EASY API QUERIES
		'''

		#Loadout
		tempLoadout = self.getJson("http://battlefield.play4free.com/en/profile/loadout/"+str(self.profileID)+"/"+str(self.nucleusID))['data']
		
   		#Soldiers
   		soldiers = self.getJson("http://battlefield.play4free.com/en/profile/soldiers/"+str(self.profileID))['data']

   		#Iterate over soldiers
   		for soldier in soldiers: 

   			#Get soldier that is currently playing
   			if int(soldier['id']) == int(self.nucleusID): 

   				#Apply properties to global dict.
				player.p['profile']['mugShot'] = soldier['mugShot']
				player.p['profile']['xpForNextLevel'] = soldier['xpForNextLevel']
		
		#Make sure player will get checked next iteration!
		currentFetched[self.profileID]['checkMe'] = True