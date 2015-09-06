#!/usr/bin/env python3

import sys
import os
import shutil
import time
import json
import hashlib

"""
Returns an array containing the current modified time
and the current hash value.
"""
def get_file_state(path):
	hasher = hashlib.sha256()
	file_modified_time = time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(os.path.getmtime(path)))
	with open(path, 'rb') as afile:
		buf = afile.read()
		hasher.update(buf)
	hash = hasher.hexdigest()
	return [file_modified_time, hash]

def sync_and_create(dir):
	other_dir = "dir2" if dir == "dir1" else "dir1"
	os.mkdir(other_dir)
	sync(dir, other_dir)

def sync(dir1, dir2):
	update_sync_file(dir1)
	update_sync_file(dir2)
	pass

def update_sync_file(dir):
	sync = '%s/.sync' % dir
	files = os.listdir(dir)
	file_dict = {
		#"file1_1.txt" : [
			#[
				#"2015-08-31 13:25:55 +1200", 
				#"a2ebea1d55e6059dfb7b8e8354e0233d501da9d968ad3686c49d6a443b9520a8"
			#]
		#]
	}
	#If the sync file exists read it
	if os.path.isfile(sync):
		with open(sync) as data_file:
			file_dict = json.load(data_file)
	else:
		data_file = open(sync, "a+")

	for dict_file in file_dict:
		#Check the file from the sync file is still in the directory
		if dict_file in files:
			print("Detective Steve has identified that %s exists in %s." % (dict_file, dir))

			disk_file = files[files.index(dict_file)]

			file_state = get_file_state('%s/%s' % (dir, dict_file))
			print(file_state)

			#File has not been changed since last sync
			if hash == dict_file[0]:
				print("Detective Steve has identified that %s has not changed in %s." % (dict_file, dir))
			print(dict_file)

			#file_dict.insert(0, NEW_LIST)

			files.remove(disk_file) #This file has been done now, remove it from the list
		else:
			print("Detective Steve indicates that %s has been deleted from %s" % (dict_file, dir))

	#Loop to check for new files
	for disk_file in files:
		#Ignore hidden files
		if disk_file.startswith('.'):
			continue


	file_dict = {
		"file1_1.txt" : [
			[
				"2015-08-31 13:25:55 +1200", 
				"a2ebea1d55e6059dfb7b8e8354e0233d501da9d968ad3686c49d6a443b9520a8"
			]
		]
	}
	with open('%s/.sync' % dir, 'w') as outfile:
		json.dump(file_dict, outfile)
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

