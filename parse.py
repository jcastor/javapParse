import sys,os
import csv

csv_filepathname=sys.argv[1]
fi = open(csv_filepathname, 'rb')
data = fi.read()
fi.close()
fo = open(csv_filepathname, 'wb')
fo.write(data.replace('\x00', '')) #removing any null characters that cause the csv reader to stop functioning
fo.close()
f = open(csv_filepathname, 'rb')

dataReader = csv.reader(f)
flag = 0 #flag identifies the start of a localvartable that identifies the variables in a method
firstlocalvartable = 0 #the localvartable is printed twice for every method, we use this to identify the first one
endofvars = 0 #flag to identify the end of the variable list in the localvartable
listofvars = {} #store the list of variables
allvars = "" #a variable to concatenate the list of variables for easy printing
globalvar = 0 #used to identify globalvariables in between class and methods
bracketflag = 0
codecount = 0
codestore = ""
codeline = ""
ended = 1
for row in dataReader:
	stringrow = str(row).lstrip('[\'').rstrip('\']').lstrip(' ') #strip [' '] from every line
	if "public class" in stringrow or "public final class" in stringrow and not "//" in stringrow: #identify the classname, filtering out comments with "//"
		classname = stringrow
		globalvar = 1
		print "C; " + stringrow
		firstlocalvartable = 0
		bracketflag = 0
	elif stringrow.startswith("public") and not "const #" in stringrow and not "//" in stringrow and "(" in stringrow: #identify a public method (taking out rows with const# which often also have the method name
		globalvar = 0
		bracketflag = 0
		method = stringrow.lstrip()
		print "M; " + method
		firstlocalvartable = 0
	elif stringrow.startswith("private") and not "const #" in stringrow and not "//" in stringrow and "(" in stringrow:
		globalvar = 0
		bracketflag = 0
		method = stringrow.lstrip()
		print "M; " + method
		firstlocalvartable = 0
	elif stringrow.startswith("protected") and not "const #" in stringrow and not "//" in stringrow and "(" in stringrow:
		globalvar = 0
		bracketflag = 0
		method = stringrow.lstrip()
		print "M; " + method
		firstlocalvartable = 0
	elif stringrow == "{":
		bracketflag = 1
	elif globalvar == 1 and bracketflag:
		if "flags:" in stringrow:
			pass
		elif stringrow == "":
			pass
		elif stringrow.startswith("Signature:"):
			print stringrow
		elif stringrow.startswith("Constant"):
			pass
		elif stringrow.startswith("00"): #identify a memory address
			pass
		else:
			print "GV; " + stringrow
	elif "Signature" in stringrow and not "Start" in stringrow and globalvar == 0 and not "length" in stringrow and not "const #" in stringrow:
		print stringrow
		flag = 1
	elif "LocalVariableTable:" in stringrow and not firstlocalvartable: #identifying the first localvariabletable
		firstlocalvartable = 1
		flag = 1
	elif flag:
		if "stack=" in stringrow and "locals=" in stringrow: #after the first local variable table there is a "Code:" segment, we can use this to signify the end of the table
			codecount = 1
			codeline = "Code: " + stringrow + ", length="
			flag = 0
			endofvars = 1
		else:
			if "Code:" in stringrow:
				pass
			elif "Start" in stringrow: #get rid of the header of the LocalVariableTable
				pass
			elif "flags:" in stringrow:
				pass
			elif "" == stringrow:
				endofvars = 1 #strip out blank spacing lines
			else:
				var = stringrow.split() #split the variable table, into segments
				varname = var[len(var)-2] #grab the second last segment from each line of the LocalVariableTable (this is the variable name)
				vartype = var[len(var)-1] #grab last segment which contains the type
				listofvars[varname] = vartype #add the variable name to our list
	if codecount:
		if "LocalVariableTable" in stringrow and firstlocalvartable:
			codecount = 0
			codestore = codestore.split(":")[0]
		elif "}" == stringrow:
			codecount = 0
			codestore = codestore.split(":")[0]
			endofvars = 1
		else:
			codestore = stringrow
	elif endofvars:
		codeline += codestore
		print codeline
		for (lvar,vvar) in listofvars.iteritems(): #formatting the list for printing seperated by commas
			print "V; " + lvar + ";" + vvar
#		print classname + "|" + method + "|" + allvars #our final print line
		listofvars = {}
		allvars = ""
		endofvars = 0
		codeline = ""
		ended = 0
f.close()

if endofvars:
	codeline += codestore
	print codeline
	for (lvar,vvar) in listofvars.iteritems(): #formatting the list for printing seperated by commas
		print "V; " + lvar + ";" + vvar
#		print classname + "|" + method + "|" + allvars #our final print line
	listofvars = {}
	allvars = ""
	endofvars = 0
	codeline = ""
