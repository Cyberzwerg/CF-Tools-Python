#!/usr/bin/python

def printA(text,style,newLine=False):
	
	if style == "pink":
		finalText = '\033[95m'+text+'\033[0m'
	elif style == "primary":
		finalText = '\033[94m'+text+'\033[0m'
	elif style == "warning":
		finalText = '\033[93m'+text+'\033[0m'
	elif style == "success":
		finalText = '\033[92m'+text+'\033[0m'
	elif style == "danger":
		finalText = '\033[91m'+text+'\033[0m'
	elif style == "bold":
		finalText = '\033[1m'+text+'\033[0m'
	if newLine == True:
		print finalText,
	else:
		print finalText

def convertToBool(input):
	if  int(input) >  0:
		return True
	else:
		return False
