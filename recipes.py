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
        desc_done = False
        while True:
            line = file.readline()
            if "Recipe exported from One tsp" in line:
                continue
            if line != "\n" and not current.get("title", False):
                current["title"] = line.rstrip("\n")
                continue
            if line.startswith("Yield:"):
                clean_line = line.removeprefix("Yield: ")
                clean_line = clean_line.rstrip("\n")
                current["yield"] = clean_line
                continue
            if line.startswith("Prep time:"):
                clean_line = line.removeprefix("Prep time: ")
                clean_line = clean_line.rstrip("\n")
                current["prep"] = clean_line
                continue
            if line.startswith("Cooking time:"):
                clean_line = line.removeprefix("Cooking time: ")
                clean_line = clean_line.rstrip("\n")
                current["cook"] = clean_line
                continue
            if line.startswith("Total time:"):
                clean_line = line.removeprefix("Total time: ")
                clean_line = clean_line.rstrip("\n")
                current["total"] = clean_line
                continue
            if line.startswith("URL:"):
                clean_line = line.removeprefix("URL: ")
                clean_line = clean_line.rstrip("\n")
                current["url"] = clean_line
                continue
            if "INGREDIENTS" in line:
                desc_done = True
                current["ingred"] = ""
                file.readline()
                line = file.readline()
                while "DIRECTIONS" not in line:
                    current["ingred"] += line
                    line = file.readline()
                current["dir"] = ""
                file.readline()
                line = file.readline()
                while "Recipe end" not in line:
                    current["dir"] += line
                    line = file.readline()
                    if "NOTES" in line:
                        current["notes"] = ""
                        file.readline()
                        line = file.readline()
                        while "Recipe end" not in line:
                            current["notes"] += line
                            line = file.readline()
                        break
            if line != "\n" and not desc_done:
                current["desc"] = ""
                desc_done = True
                while line != "\n":
                    current["desc"] += line
                    line = file.readline()
            if not line:
                recipes.append(current)
                break  # Stop when end of file is reached
pprint.pprint(recipes)
