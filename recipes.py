#!/usr/bin/env python3

import os
import pprint

dir_path = "/home/plus-buckle/recipes/Recipes_20260618/"
# os.listdir returns everything, so we filter using os.path.isfile
files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

recipes = []
# start loop over files
for thisfile in files:
    with open(os.path.join(dir_path, thisfile), "r") as file:
        current = {}
        while True:
            line = file.readline()
            if "Recipe exported from One tsp" in line:
                continue
            if line != "\n" and not current.get("title", False):
                current["title"] = line.rstrip("\n")
            if line.startswith("Yield:"):
                clean_line = line.removeprefix("Yield: ")
                clean_line = clean_line.rstrip("\n")
                current["yield"] = clean_line
            if line.startswith("Prep time:"):
                clean_line = line.removeprefix("Prep time: ")
                clean_line = clean_line.rstrip("\n")
                current["prep"] = clean_line
            if line.startswith("Cooking time:"):
                clean_line = line.removeprefix("Cooking time: ")
                clean_line = clean_line.rstrip("\n")
                current["cook"] = clean_line
            if line.startswith("Total time:"):
                clean_line = line.removeprefix("Total time: ")
                clean_line = clean_line.rstrip("\n")
                current["total"] = clean_line
            if line.startswith("URL:"):
                clean_line = line.removeprefix("URL: ")
                clean_line = clean_line.rstrip("\n")
                current["url"] = clean_line
            if not line:
                print(current)
                recipes.append(current)
                break  # Stop when end of file is reached
# open current file
# read a line at a time
# try to match something
# end loop
pprint.pprint(recipes)
