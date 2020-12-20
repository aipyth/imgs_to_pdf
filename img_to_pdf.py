#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import math
import re
from PIL import Image, ExifTags
import argparse


def fix_orientation_from_exif(image):
	try:
		for orientation in ExifTags.TAGS.keys():
			if ExifTags.TAGS[orientation] == 'Orientation':
				break

		exif = dict(image._getexif().items())

		if exif[orientation] == 3:
			image = image.rotate(180, expand=True)
		elif exif[orientation] == 6:
			image=image.rotate(270, expand=True)
		elif exif[orientation] == 8:
			image=image.rotate(90, expand=True)

	    #image.save(filepath)
	except (AttributeError, KeyError, IndexError):
		# cases: image don't have getexif
		pass
	return image


# Some flags
OPTIMIZE = True
QUALITY = 95
SORT_BY_NUMB = True


ext = ['.jpg', '.png', '.JPEG']

print("Looking for files in current working directory...")

files = []
for file_name in os.listdir():
    if os.path.isfile(file_name) and os.path.splitext(file_name)[1] in ext:
        filesize = os.path.getsize(file_name)
        files.append({'filename': file_name, 'filesize': filesize})

print(f"Got {len(files)} file{'s' if len(files) > 1 else ''}.")


if SORT_BY_NUMB:
	sbn = input("Sort files by number in filenames? (Y/n): ")
	if sbn.lower() == 'y':
		print("Sorting...")
		try:
			files.sort(key=lambda x: int(re.search(r'\d+', x['filename']).group(0)))
		except AttributeError:
			print("Can't do sort. Some files got no number in name.")

			sbs = input("Perform string-based sorting? (Y/n): ")
			if sbs.lower() == 'y':
				files.sort(key=lambda x: x['filename'])




if OPTIMIZE:
	compression_level = int(input("Compression (from 0 to 100): ")) % 100
	comp_info = input("Show compression information? (Y/n): ")

	use_greyscale = input("Use greyscale instead of RGB? (Y/n): ")


images = []
for image_inf in files:
	image = Image.open(image_inf['filename'])
	image = fix_orientation_from_exif(image)
	if OPTIMIZE:
		width, height = image.size
		# get new size
		width, height = math.floor(width * ((100 - compression_level) / 100)), math.floor(height * ((100 - compression_level) / 100))
		# resize and save optimizing

		image = image.resize((width, height), Image.ANTIALIAS)
		if use_greyscale.lower() == 'y':
			image = image.convert('L')
		else:
			image = image.convert('RGB')
		image.save(image_inf['filename'], optimize=True, quality=QUALITY)

		if comp_info.lower() == 'y':
			compressed_by = (image_inf['filesize'] - os.path.getsize(image_inf['filename'])) / image_inf['filesize'] * 100
			print(f"Image \'{image_inf['filename']}\' has been comresssed. File size {-compressed_by}%.")
	images.append(image)


filename = input("Enter file name: ") + '.pdf'
images[0].save(filename, save_all=True, append_images=images[1:])

print(f"Output file {filename} has been created.")

df = input("Delete source files? (Y/n): ")
if df.lower() == 'y':
	for file in files:
		os.remove(file['filename'])
	print(f"{len(files)} file{'s' if len(files) > 1 else ''} deleted.")
