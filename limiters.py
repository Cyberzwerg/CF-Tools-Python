#CLASSLIMITER CLASS
class classLimiter():
	def __init__(self,classLimiterConfig,classLimiterVipProtection):
		self.classLimiterConfig = classLimiterConfig
		self.classLimiterVipProtection = classLimiterVipProtection
	def checkPlayer(self,player):
		if player['profile']['vip'] == True and self.classLimiterVipProtection == True:
			return False
		else:
			if len(self.classLimiterConfig["current"][player['game']['team']][player['profile']['class']]) >= int(self.classLimiterConfig["max"][player['profile']['class']]):
				player['kickStatus'] = True
				player['kickReason'] = player['profile']['name']+" you are being kicked. Reason: |ccc| Classlimiter |ccc|  Max  |ccc|  "+player['profile']['class']+"s |ccc| of |ccc| "+self.classLimiterConfig["max"][player['profile']['class']]+" |ccc| reached"
				self.classLimiterConfig["current"][player['game']['team']][player['profile']['class']].append(player['profile']['profileID'])
				return True
			else:
				self.classLimiterConfig["current"][player['game']['team']][player['profile']['class']].append(player['profile']['profileID'])
				return False
	def removePlayer(self,player):
		self.classLimiterConfig["current"][player['game']['team']][player['profile']['class']].remove(player['profile']['profileID'])

class levelLimiter():
	def __init__(self,levelLimiterConfig,levelLimiterVipProtection):
		self.levelLimiterConfig = levelLimiterConfig
		self.levelLimiterVipProtection = levelLimiterVipProtection
	def checkPlayer(self,player):
		if int(player['profile']['rank']) > int(self.levelLimiterConfig['maxLevel']):
			player['kickStatus'] = True
			player['kickReason'] = player['profile']['name']+" you are being kicked. Reason: |ccc| Level-limiter:  Max  |ccc| Level  of |ccc| "+self.levelLimiterConfig['maxLevel']+" |ccc| reached!"
		if int(player['profile']['rank']) < int(self.levelLimiterConfig['minLevel']):
			player['kickStatus'] = True
			player['kickReason'] = player['profile']['name']+" you are being kicked. Reason: |ccc| Level-limiter:  Min  |ccc| Level  of |ccc| "+self.levelLimiterConfig['minLevel']+" |ccc| too high!"

class weaponLimiter():
	def __init__(self,weaponLimiterConfig,weaponLimiterVipProtection):
		self.weaponLimiterConfig = weaponLimiterConfig
		self.weaponLimiterVipProtection = weaponLimiterVipProtection
	def checkPlayer(self,player):
		#print player['loadout']['weapons']
		for weapon in player['loadout']['weapons']:
			if weapon['id'] in self.weaponLimiterConfig['weapons']:
				if self.weaponLimiterConfig['weapons'][str(weapon['id'])]['forbidden'] == True:
					player['kickStatus'] = True
					player['kickReason'] = " |ccc| "+player['profile']['name']+" |ccc| , you are being kicked. Reason: |ccc| Weapon-Limiter |ccc|  Weapon  |ccc|  "+weapon['name']+" |ccc| is forbidden"
				elif self.weaponLimiterConfig['weapons'][str(weapon['id'])]['prebuy'] == True:
					if int(player['profile']['rank']) < int(weapon['lockCriteria'])-int(self.weaponLimiterConfig['prebuyTolerance']):
						player['kickStatus'] = True
						player['kickReason'] = " |ccc| "+player['profile']['name']+" |ccc| , you are being kicked. Reason: |ccc| Weapon-Limiter |ccc|  Your rank  |ccc|  "+str(player['profile']['rank'])+" |ccc| is too low to use |ccc|  "+weapon['name']
					
	def removePlayer(self,player):
		pass