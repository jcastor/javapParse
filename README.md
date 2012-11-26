javapParse
==========

This script is meant to identify some useful information taken from the output of the javap command.

Specifically the output of:

javap -s -private -c -l -verbose <filename>

Currently it identifies as follows:

C: class
GV: global variable name
Signature: signature for each global var GV
M: method name
Signature: signature for each method M
Code: stack,locals,args_size
V: variable name;type

I am working on making this better, currently it is fairly rudimentary.