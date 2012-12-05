import sys,os
import csv,re

filepathname=sys.argv[1]
f = open(filepathname, 'rb')

#REGEX PATTERNS
classpattern = r'(^public final class)|(^public class)' #pattern used to identify a class
methodpattern = r'(^public)|(^private)|(^protected)' #pattern used to identify a method
signaturepattern = r'(^Signature:)' #pattern used to identify a signature
flagpattern = r'(^flags:)' #pattern used to identify a flag
gvstartpattern = r'^{' #pattern used to identify the start of global variable declarations
localpattern = r'(^LocalVariableTable:)' #pattern used to identify localvariabletable
codepattern = r'(^Code:)' #pattern used to identify Code: segment
exceptpattern = r'(^Exceptions:)' #pattern used to identify Exceptions: segment
#INIT REGEX
classregex = re.compile(classpattern)
methodregex = re.compile(methodpattern)
gvstartregex = re.compile(gvstartpattern)
sigregex = re.compile(signaturepattern)
flagregex = re.compile(flagpattern)
localregex = re.compile(localpattern)
coderegex = re.compile(codepattern)
exceptregex = re.compile(exceptpattern)
#Variables used as flags
gv = 0 #used to signify when GV are starting/ending
local = 0
firstlocal = 0 #identifies the first localvartable so that we dont print them all off twice

for line in f:
	linestripped = line.lstrip().rstrip('\n') #removing leading whitespace and newline characters
	findClass = classregex.match(linestripped)
	findMethod = methodregex.match(linestripped)
	findGV = gvstartregex.match(linestripped)
	findSig = sigregex.match(linestripped)
	findLocal = localregex.match(linestripped)
	findFlag = flagregex.match(linestripped)
	if findClass:
		print "C;" + linestripped #print if class is detected
		firstlocal = 0
	if findMethod and "(" in linestripped  and not findClass:
		print "M;" + linestripped #print if method detected and class not detected
		firstlocal = 0 
	if findGV: #if the "{" was found start looking for global variables
		gv = 1
	if findLocal and not firstlocal:
		local = 1
	if findSig: #print signatures for methods/gv
		if "length =" in linestripped:
			pass
		else:
			print linestripped
	if gv: #looking for global variables and signatures for them
		if not findGV and "(" not in linestripped: #if it is not a method (javap's output will go right from GV to methods)
			if linestripped != "": #eliminate blank lines
				findSig = sigregex.match(linestripped)
				if findSig:
					pass
				elif findFlag:
					pass #we do not want to print the flags
				else:
					print "GV;" + linestripped #if it is not a signature or a flag it should be a global variable
		if findMethod and "(" in linestripped: #if a method is found then that is the end of the global variables
			gv = 0
	if local: #if a LocalVariableTable is found and only if its the first local variable table
		findCode = coderegex.match(linestripped)
		findExcept = exceptregex.match(linestripped)
		if not findCode and not findMethod and not findSig and not findFlag and not findExcept:
			if linestripped != "" and "LocalVariableTable:" not in linestripped and "Start  Length" not in linestripped:
				print linestripped
		if findCode or findMethod or findExcept:
			local = 0
			firstlocal = 1
