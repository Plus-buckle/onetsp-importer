#!/usr/bin/env python3

import os
import pprint
import re


def conv_min(line):
    time = 0
    h = re.search(r"(\d{1,2})\shour", line)
    if h:
        hours = int(h.group(1))
        time = hours * 60
    m = re.search(r"(\d{1,2})\smin", line)
    if m:
        time += int(m.group(1))
    return time


def rm_numb(line):
    return re.sub(r"^\d{1,2}\.\s", "", line)


def fix_heading(heading):
    clean_head = heading.replace(" --", "")
    clean_head = clean_head.replace("-- ", "#")
    return clean_head


def clean_text(text, handle_ws=False):
    new_text = text.replace("â€™", "'")
    new_text = new_text.replace("Â", "")
    new_text = new_text.replace("Ã—", "x")
    new_text = new_text.replace("â…“", "⅓")
    new_text = new_text.replace("â…›", "⅛")
    if handle_ws:
        new_text = new_text.strip()
    return new_text


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
                current["title"] = clean_text(line, True)
                continue
            if line.startswith("Yield:"):
                clean_line = line.removeprefix("Yield: ")
                current["yield"] = clean_text(clean_line, True)
                continue
            if line.startswith("Prep time:"):
                clean_line = line.removeprefix("Prep time: ")
                clean_line = clean_text(clean_line, True)
                current["prep"] = conv_min(clean_line)
                continue
            if line.startswith("Cooking time:"):
                clean_line = line.removeprefix("Cooking time: ")
                clean_line = clean_text(clean_line, True)
                current["cook"] = conv_min(clean_line)
                continue
            if line.startswith("Total time:"):
                clean_line = line.removeprefix("Total time: ")
                clean_line = clean_text(clean_line, True)
                current["total"] = conv_min(clean_line)
                continue
            if line.startswith("URL:"):
                clean_line = line.removeprefix("URL: ")
                current["url"] = clean_text(clean_line, True)
                continue
            if "INGREDIENTS" in line:
                desc_done = True
                current["ingred"] = ""
                file.readline()
                line = file.readline()
                while "DIRECTIONS" not in line:
                    linetmp = fix_heading(line)
                    current["ingred"] += clean_text(linetmp)
                    line = file.readline()
                current["dir"] = ""
                file.readline()
                line = file.readline()
                while "Recipe end" not in line:
                    linetmp = fix_heading(line)
                    linetmp = rm_numb(linetmp)
                    current["dir"] += clean_text(linetmp)
                    line = file.readline()
                    if "NOTES" in line:
                        current["notes"] = ""
                        file.readline()
                        line = file.readline()
                        while "Recipe end" not in line:
                            current["notes"] += clean_text(line)
                            line = file.readline()
                        break
            if line != "\n" and not desc_done:
                current["desc"] = ""
                desc_done = True
                while line != "\n":
                    current["desc"] += clean_text(line)
                    line = file.readline()
            if not line:
                recipes.append(current)
                break  # Stop when end of file is reached
pprint.pprint(recipes)
