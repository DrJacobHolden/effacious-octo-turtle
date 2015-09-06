#!/usr/bin/env python3

import sys
import os
import shutil
import time
import json

def sync_and_create(dir):
	other_dir = "dir2" if dir == "dir1" else "dir1"
	os.mkdir(other_dir)

	pass

def sync(dir1, dir2):
	pass

#Requires two arguments to run.
if len(sys.argv) != 3:
	print("Don't push me buddy. (A few more arguments would be nice.)")

#Both directories exist
if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):
	sync(sys.argv[1], sys.argv[2])
elif os.path.isdir(sys.argv[1]):
	sync_and_create(sys.argv[1])
elif os.path.isdir(sys.argv[2]):
	sync_and_create(sys.argv[2])
else:
	print("Stop trying to \"Sink\" imaginary directories.")

