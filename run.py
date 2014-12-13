import toolNew,time
test = toolNew.Tool({
		'connectionInfo': {
			'IP': "",
			'PORT': ,
			'PASSWORD': ""

		},
		'rights': {
			"2851071969": 60, # CYBERZWERG 

		},
		"cmds": {
			"k" : {
				"cmdAction": "kickPlayer",
				"neededRights": 40
			},
			"help" : {
				"cmdAction": "printHelp",
				"neededRights": 0
			},
			"h" : {
				"cmdAction": "printHelp",
				"neededRights": 0
			}
		},
		"rules": ["No camping","No RPG on Infantry","No insult","No Hacks","No Glitching"],
		"kickSystem": {
			"kickDelay": 3 # 3 Seconds until player gets kicked.
		}
})
test.setDaemon(True)
test.start()

while True:
	time.sleep(1000)
