
import os
import sys

def printInline(msg):
    print(msg, end=" ", flush=True)

def list_toString(listToDisplay):
    listToDisplay = list(listToDisplay) # In case listToDisplay is e.g. a set
    msg = ""
    for atom in listToDisplay:
        msg += f"\"{atom}\""
        isLastAtom = (atom == listToDisplay[-1])
        msg += "" if isLastAtom else ", "
    return msg

def printBuilder(msg, end='\n', file=sys.stdout, flush=False):
    print("\t\t\t" + msg, end=end, file=file, flush=flush)

def raiseError(errMsg):
    print("") # In case cursor is at the middle of the current line
    print("Error: ", errMsg, file=sys.stderr)
    exit(1)

def raiseWarning(warningMsg):
    print("") # In case cursor is at the middle of the current line
    print("Warning: ", warningMsg, file=sys.stderr)

