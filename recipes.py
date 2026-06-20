#!/usr/bin/env python3

import os
import pprint

dir_path = "/home/plus-buckle/recipes/Recipes_20260618/"
# os.listdir returns everything, so we filter using os.path.isfile
files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

URLs = []
# start loop over files
for thisfile in files:
    with open(os.path.join(dir_path, thisfile), "r") as file:
        while True:
            line = file.readline()
            if line.startswith("URL:"):
                URLs.append(line.strip("URL: "))
                break
            if not line:
                break  # Stop when end of file is reached
# open current file
# read a line at a time
# try to match something
# end loop
pprint.pprint(URLs)
