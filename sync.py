#!/usr/bin/env python3

import sys
import os
import shutil
import time
from time import gmtime
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

"""
Takes in a time string and converts it to epoch time.
This just does not care about timezones, I spent about an hour googling it
and it turned out to be a total pain in the ass so I am just ignoring it.
If this turns out to be of critical import to the assignment I am going to
make it my life goal to find all the descendants of the idiot who invented
the "human readable" time format and kill them. It's like the imperial system
but covered in spikes. Screw that guy.
"""
def convertTimeEpoch(timezzzz):
	return int(time.mktime(time.strptime(timezzzz[0:19], '%Y-%m-%d %H:%M:%S')))

def convertTimeReadable(timezzzz):
	return time.strftime("%Y-%m-%d %H:%M:%S %z", timezzzz)

def sync_and_create(dir1, dir2):
	os.mkdir(dir2)
	sync(dir1, dir2)

def sync(dir1, dir2):
	update_sync_file(dir1)
	update_sync_file(dir2)
	merge_dirs(dir1, dir2)
	pass

def start_sync(dir1, dir2):
	#Both directories exist
	if os.path.isdir(dir1) and os.path.isdir(dir2):
		sync(dir1, dir2)
	elif os.path.isdir(dir1):
		sync_and_create(dir1, dir2)
	elif os.path.isdir(dir2):
		sync_and_create(dir2, dir1)
	else:
		print("Stop trying to \"Sink\" imaginary directories.")

"""
Updates the sync file to represent the current directory contents.
This handles updated files, deleted files and also creates the sync
file if there is not one already existing.
"""
def update_sync_file(dir):
	sync = '%s/.sync' % dir
	files = os.listdir(dir)
	file_dict = {}

	#If the sync file exists read it
	if os.path.isfile(sync):
		with open(sync) as data_file:
			file_dict = json.load(data_file)
	else:
		#print("Detective Steve has encountered %s for the first time. Creating sync file." % dir)
		data_file = open(sync, "a+")

	for dict_file in file_dict:
		#Check the file from the sync file is still in the directory
		if dict_file in files:
			#print("Detective Steve has identified that %s exists in %s." % (dict_file, dir))

			disk_file = files[files.index(dict_file)]

			[file_modified_time, hash] = get_file_state('%s/%s' % (dir, dict_file))
			#print(file_modified_time)
			#print(hash)

			#File has not been changed since last sync
			if hash == file_dict[dict_file][0][1]:
				#Compare modified times
				if convertTimeEpoch(file_modified_time) != convertTimeEpoch(file_dict[dict_file][0][0]):
					#print("Detective Steve has identified that %s has an incorrect modified time." % dict_file)
					correctTime = convertTimeEpoch(file_dict[dict_file][0][0])
					os.utime("%s/%s" % (dir, dict_file), (correctTime, correctTime))
				else:
					#print("Detective Steve has identified that %s is consistent with the sync file of %s" % (dict_file, dir))
					pass
			else:
				#print("Detective Steve has updated the sync file for %s/%s" % (dir, dict_file))
				file_dict[dict_file].insert(0, [file_modified_time, hash])

			files.remove(disk_file) #This file has been done now, remove it from the list
		else:
			if file_dict[dict_file][0][1] != "deleted":
				#print("Detective Steve indicates that %s has been deleted from %s" % (dict_file, dir))
				file_dict[dict_file].insert(0, [convertTimeReadable(gmtime()), "deleted"])

	#Loop to check for new files
	for disk_file in files:
		#Ignore hidden files
		if disk_file.startswith('.'):
			continue
		if os.path.isdir("%s/%s" % (dir, disk_file)):
			#subdirectories
			if dir in subdir_dict:
				if subdir_dict[dir].count(disk_file) > 0:
					continue
			#print("Detective Steve has found the subdirectory %s in %s." % (disk_file, dir))
			if dir in subdir_dict:
				subdir_dict[dir].append(disk_file)
			else:
				subdir_dict[dir] = []
				subdir_dict[dir].append(disk_file)
			continue
		#print("Detective Steve has found a new file %s in %s adding to sync." % (disk_file, dir))
		file_dict[disk_file] = [get_file_state('%s/%s' % (dir, disk_file))]

	with open('%s/.sync' % dir, 'w') as outfile:
		json.dump(file_dict, outfile)
	pass

"""
This method updates the modified time of a file if it has changed
in the other directory (logic for deciding in merge_dirs), if the file
has been deleted it will deleted it.
"""
def update(filez, time, digest):
	if digest != "deleted": #Update the modified time
		os.utime(filez, (time, time))
	else:
		os.remove(filez) # Delete it if it has been deleted

"""
This method copies a file over the old version in another directory.
If the file has been deleted in the other directory it deletes it in
this directory too. It also handles updating the modified time.
"""
def try_copy(file1, file2, digest, time):
	if digest != "deleted": #Update the modified time
		shutil.copyfile(file1, file2)
		os.utime(file2, (time, time))
	else:
		os.remove(file2) # Delete it if it has been deleted

"""
This will merge the two directories specified as per the assignment spec
"""
def merge_dirs(dir1, dir2):
	with open('%s/.sync' % dir1) as sync1_file:
		sync1 = json.load(sync1_file)
	with open('%s/.sync' % dir2) as sync2_file:
		sync2 = json.load(sync2_file)

	#Loop through all the keys in the first directory
	for key in sync1:
		file1 = "%s/%s" % (dir1, key)
		file2 = "%s/%s" % (dir2, key)
		#File is in both sync files
		if key in sync2.keys():
			#Compare file digests, same?
			if sync1[key][0][1] == sync2[key][0][1]:
				#Earliest modification date applied to both files
				file1_mod = convertTimeEpoch(sync1[key][0][0])
				file2_mod = convertTimeEpoch(sync2[key][0][0])
				if file1_mod > file2_mod:
					#File 2 correct
					update(file1, file2_mod, sync2[key][0][1])
					sync1[key] = sync2[key]
					#print("Detective Steve has identified that %s is the oldest identical version." % file2)
				if file1_mod < file2_mod:
					#File 1 correct
					update(file2, file1_mod, sync1[key][0][1])
					sync2[key] = sync1[key]
					#print("Detective Steve has identified that %s is the oldest identical version." % file1)
			#Digests are different
			else:
				done = False
				#Loop Sync 1 key
				for i in range(len(sync1[key])):
					#Matches with past entry in sync1[key]
					if sync1[key][i][1] == sync2[key][0][1] and not done:
						file1_mod = convertTimeEpoch(sync1[key][0][0])
						try_copy(file1, file2, sync1[key][0][1], file1_mod)
						sync2[key] = sync1[key]
						#print("Detective Steve has identified that %s is the new version." % file1)
						done = True
				#Loop Sync 2 key
				for i in range(len(sync2[key])):
					if sync2[key][i][1] == sync1[key][0][1] and not done:
						#This should probably be a method to avoid code repetition
						#but I'm bored.
						file2_mod = convertTimeEpoch(sync2[key][0][0])
						try_copy(file2, file1, sync2[key][0][1], file2_mod)
						sync1[key] = sync2[key]
						#print("Detective Steve has identified that %s is the new version." % file2)
						done = True
				#both unique
				if not done:
					file1_mod = convertTimeEpoch(sync1[key][0][0])
					file2_mod = convertTimeEpoch(sync2[key][0][0])
					if file1_mod < file2_mod:
						#File 2 correct
						update(file1, file2_mod, sync2[key][0][1])
						sync1[key] = sync2[key]
						#print("Detective Steve has identified that %s is the newest version (both unique)." % file2)
						done = True
					if file1_mod > file2_mod:
						#File 1 correct
						update(file2, file1_mod, sync1[key][0][1])
						sync2[key] = sync1[key]
						#print("Detective Steve has identified that %s is the newest version (both unique)." % file1)
						done = True

		#File is not in the other directory
		else:
			#Add it to the sync file
			sync2[key] = sync1[key]
			if sync1[key][0][1] != "deleted":
				shutil.copyfile(file1, file2)
			pass
		#Loop through all the keys in the first directory
	for key in sync2:
		file1 = "%s/%s" % (dir2, key)
		file2 = "%s/%s" % (dir1, key)
		#File is in both sync files, we have already done this above
		if key in sync1.keys():
			pass
		#File is not in the other directory
		else:
			sync1[key] = sync2[key]
			if sync2[key][0][1] != "deleted":
				shutil.copyfile(file1, file2)
			pass
	
	with open('%s/.sync' % dir1, 'w') as outfile:
		json.dump(sync1, outfile)
	with open('%s/.sync' % dir2, 'w') as outfile2:
		json.dump(sync2, outfile2)
	pass

#Requires two arguments to run.
if len(sys.argv) != 3:
	print("Don't push me buddy. (A few more arguments would be nice.)")

subdir_dict = {}

#Store the starting point
topdir1 = sys.argv[1]
topdir2 = sys.argv[2]

#Initially sync the top level directories
start_sync(topdir1, topdir2)

#Sync the subdirectories
#If the subdirectory is present in both top level dirs, it will be synced twice.
#There is probably a way around it but it doesn't really make that much difference
#and is much easier this way. KISS
while(len(subdir_dict.keys()) != 0):
	for key in subdir_dict.keys():
		for dir in subdir_dict[key]:
			if key is topdir1 or key is topdir2:
				#differentiate between sub directories and sub-sub directories
				start_sync("%s/%s" % (topdir1, dir), "%s/%s" % (topdir2, dir))
			else:
				maindir = "%s/%s" % (key, dir)
				if topdir1 in key:
					otherdir = "%s%s/%s" % (topdir2, key.lstrip(topdir1), dir)
				else:
					otherdir = "%s%s/%s" % (topdir1, key.lstrip(topdir2), dir)
				start_sync(maindir, otherdir)
		del subdir_dict[key]

