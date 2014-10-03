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
