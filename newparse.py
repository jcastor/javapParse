import sys,os
import csv,re

filepathname=sys.argv[1]
f = open(filepathname, 'rb')

#------ REGEX PATTERNS ------#
classpattern = r'^(public |private | protected )(final|class|final class|interface|abstract class)|^(class)|^(interface)' #pattern used to identify a class
methodpattern = r'^(public)|^(private)|^(protected)' #pattern used to identify a method
signaturepattern = r'^(Signature:)' #pattern used to identify a signature
flagpattern = r'^(flags:)' #pattern used to identify a flag
gvstartpattern = r'^{' #pattern used to identify the start of global variable declarations
localpattern = r'^(LocalVariableTable:)' #pattern used to identify localvariabletable
codepattern = r'^(Code:)' #pattern used to identify Code: segment
exceptpattern = r'^(Exceptions:)' #pattern used to identify Exceptions: segment
constantpattern = r'^(Constant Value:)' #identify Constant Value
lntpattern = r'^(LineNumberTable:)' #identify line number table
excepttablepattern = r'^(Exception table:)' #identify exception table
#------ INIT REGEX ------#
classregex = re.compile(classpattern)
methodregex = re.compile(methodpattern)
gvstartregex = re.compile(gvstartpattern)
sigregex = re.compile(signaturepattern, re.IGNORECASE)
flagregex = re.compile(flagpattern)
localregex = re.compile(localpattern)
coderegex = re.compile(codepattern)
exceptregex = re.compile(exceptpattern)
constantregex = re.compile(constantpattern, re.IGNORECASE)
lntregex = re.compile(lntpattern)
excepttableregex = re.compile(excepttablepattern)

#------ Variables used as flags ------#
gv = 0 #used to signify when GV are starting/ending
local = 0 #used to signify when localvariable table detected
firstlocal = 0 #identifies the first localvartable so that we dont print them all off twice
codesegment = 0
### dict to store variable names and types
listofvars = {}
stackline = ""
for line in f:
	linestripped = line.lstrip().rstrip('\n') #removing leading whitespace and newline characters
	findClass = classregex.match(linestripped)
	findMethod = methodregex.match(linestripped)
	findGV = gvstartregex.match(linestripped)
	findSig = sigregex.match(linestripped)
	findLocal = localregex.match(linestripped)
	findFlag = flagregex.match(linestripped)
	findConstant = constantregex.match(linestripped)
	findCode = coderegex.match(linestripped)
	findExcept = exceptregex.match(linestripped)
	findExceptionTable = excepttableregex.match(linestripped)
	if findClass:
		print "C;" + linestripped #print if class is detected
		firstlocal = 0
	if findMethod and "(" in linestripped  and not findClass:
		print "M;" + linestripped #print if method detected and class not detected
		firstlocal = 0 #reset firstlocal on a new method as it will have a new table
	if findGV: #if the "{" was found start looking for global variables
		gv = 1
	if findLocal and not firstlocal: #detect the first local variable table
		local = 1
	if findCode or findExcept:
		codesegment = 1
	if findSig: #print signatures for methods/gv
		if "length =" in linestripped:
			pass
		else:
			print "Signature;" + linestripped.split("Signature: ")[1]
	if gv: #looking for global variables and signatures for them
		if not findGV and "(" not in linestripped: #if it is not a method (javap's output will go right from GV to methods)
			if linestripped != "": #eliminate blank lines
				findSig = sigregex.match(linestripped)
				if findSig:
					pass
				elif findFlag:
					pass #we do not want to print the flags
				elif findConstant:
					pass
				elif "}" == linestripped:
					pass
				else:
					print "GV;" + linestripped #if it is not a signature or a flag it should be a global variable
		if findMethod and "(" in linestripped or "}" == linestripped: #if a method is found then that is the end of the global variables
			gv = 0
	if local: #if a LocalVariableTable is found and only if its the first local variable table
		findCode = coderegex.match(linestripped)
		findExcept = exceptregex.match(linestripped)
		if not findCode and not findMethod and not findSig and not findFlag and not findExcept:
			if linestripped != "" and "LocalVariableTable:" not in linestripped and "Start  Length" not in linestripped:
				var = linestripped.split()
				varname = var[len(var)-2]
				vartype = var[len(var)-1]
				listofvars[varname] = vartype
		if findCode or findMethod or findExcept or findSig:
			for (lvar,vvar) in listofvars.iteritems():
				print "V;" + lvar + ";" + vvar
			local = 0
			firstlocal = 1
			listofvars = {}
	if codesegment: #if a Code: segment or and Except: segment is found (a method will have one or the other)
		findLNT = lntregex.match(linestripped)

		if "Stack=" in linestripped or "stack=" in linestripped:
			stackline = linestripped
		if not findLNT and not findLocal and linestripped != "}" and not findExceptionTable and not findExcept: #the code segment will end on either a local variable table or a line number table or a exception table
			lastcodeline = linestripped
		if findLNT or findLocal or linestripped == "}" or findExceptionTable or findExcept:
			codesegment = 0
			print "Code;" + stackline + ", length=" + lastcodeline.split(":")[0]
