#!/usr/bin/python3

import sys, getopt
    

try:
    _, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

with open(args[0], mode='rb') as file: # b is important -> binary
    print(file.read()[:100])
