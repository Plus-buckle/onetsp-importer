#!/usr/bin/env python3

import json
import os
import pprint
import re
import sys

import requests
import yaml


def tamari_import(url, user, pw, recipes, insecure=False):
    """
    import all recipe data into the Tamari app (https://github.com/alexbates/Tamari)

        Parameters are:
            url to app
            username for login
            password for login
            recipe data as list of dicts
            insecure option
    """
    # create a list of the optional sections
    optional = ["description", "prep_time", "cook_time", "total_time", "url"]
    login = requests.post(
        f"{url}/api/user/authenticate",
        json={"email": user, "password": pw},
        verify=insecure,
    )
    if login.json()["message"] == "success":
        token = login.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        for recipe in recipes:
            instructions = []
            for line in recipe["dir"].split("\n"):
                # tamari expects headings like "#Heading"
                linetmp = fix_heading(line)
                # tamari expects no line numbers
                linetmp = rm_numb(linetmp)
                instructions.append(linetmp)
            ingredients = []
            for line in recipe["ingred"].split("\n"):
                # tamari expects headings like "#Heading"
                linetmp = fix_heading(line)
                ingredients.append(linetmp)
            upload = {
                "title": recipe["title"],
                "category": "Miscellaneous",
                "ingredients": ingredients,
                "instructions": instructions,
            }
            for o in optional:
                v = recipe.get(o)
                if v:
                    upload[o] = v

            notes = recipe.get("notes")
            if notes:
                upload["notes"] = notes.split("\n")

            _ = requests.post(
                f"{url}/api/my-recipes/recipe/add",
                json=upload,
                headers=auth_header,
                verify=insecure,
            )
    return


def conv_units(text):
    """
    convert all units to abbreviation

    parameters:
        text (str): string in the format "2 ounces cherry tomatos"

    returns:
        text (str): string in the format "2 oz. cherry tomatos"
    """
    # order matters when converting units!
    new_text = text.replace("ounces", "oz")
    new_text = new_text.replace("ounce", "oz")
    new_text = new_text.replace("pounds", "lbs")
    new_text = new_text.replace("pound", "lb")
    new_text = new_text.replace("teaspoons", "tsp")
    new_text = new_text.replace("Teaspoons", "tsp")
    new_text = new_text.replace("Teaspoon", "tsp")
    new_text = new_text.replace("teaspoon", "tsp")
    new_text = new_text.replace("tbsp", "Tbsp")
    new_text = new_text.replace("Tablespoons", "Tbsp")
    new_text = new_text.replace("tablespoons", "Tbsp")
    new_text = new_text.replace("Tablespoon", "Tbsp")
    new_text = new_text.replace("tablespoon", "Tbsp")
    return new_text


def conv_min(line):
    """
    converts Onetsp time format

    parameters:
        line: string in the format "2 hours, 30 minutes"

    returns:
        time (int): total number of minutes
    """
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
    """
    removes Markdown-style numbering from the beginning of a string

    parameters:
        line: string in the format "3. add flour to mix and stir"

    returns:
        line: string in the format "add flour to mix and stir"
    """
    return re.sub(r"^\d{1,2}\.\s", "", line)


def fix_heading(heading):
    """
    converts Onetsp headings to Markdown-style

    parameters:
        heading (str): line with possible heading

    returns:
        line (str): line with Markdown heading
    """
    clean_head = heading.replace(" --", "")
    clean_head = clean_head.replace("-- ", "#")
    return clean_head


def clean_text(text, handle_ws=False):
    """
    converts special character format to normal character format

    parameters:
        text (str): string in the format " â„ cup of flour "
        handle_ws (ws): white space in a string

    returns:
        text (str): string in the format "¾ cup of flour"
    """
    new_text = text.replace("â€™", "'")
    new_text = new_text.replace("Â", "")
    new_text = new_text.replace("Ã—", "x")
    new_text = new_text.replace("â…“", "⅓")
    new_text = new_text.replace("â…›", "⅛")
    new_text = new_text.replace("â€¦", "...")
    new_text = new_text.replace("Ã±", "ñ")
    new_text = new_text.replace("Ã©", "é")
    new_text = new_text.replace("▢", "")
    new_text = new_text.replace("â„", "¾")
    if handle_ws:
        new_text = new_text.strip()
    return new_text


def read_recipes(config, files):
    """
    opens each recipe file and loads the contents

    parameters:
        config: parameters from config file
        files: list of recipe files

    returns:
        recipes (list): list of dicts containing recipes
    """
    recipes = []
    dir_path = config["dir_path"]
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
                    current["prep_time"] = conv_min(clean_line)
                    continue
                if line.startswith("Cooking time:"):
                    clean_line = line.removeprefix("Cooking time: ")
                    clean_line = clean_text(clean_line, True)
                    current["cook_time"] = conv_min(clean_line)
                    continue
                if line.startswith("Total time:"):
                    clean_line = line.removeprefix("Total time: ")
                    clean_line = clean_text(clean_line, True)
                    current["total_time"] = conv_min(clean_line)
                    continue
                if line.startswith("URL:"):
                    clean_line = line.removeprefix("URL: ")
                    current["url"] = clean_text(clean_line, True)
                    continue
                if "INGREDIENTS" in line:
                    # if we hit ingredients section, we had to have
                    # already passed the (optional) description section
                    desc_done = True
                    current["ingred"] = ""
                    file.readline()
                    line = file.readline()
                    # while we haven't found the directions heading,
                    # we are in the ingredients section
                    while "DIRECTIONS" not in line:
                        if config.get("convert"):
                            linetmp = conv_units(line)
                        else:
                            linetmp = line
                        current["ingred"] += clean_text(linetmp)
                        line = file.readline()
                    current["dir"] = ""
                    file.readline()
                    line = file.readline()
                    while "Recipe end" not in line:
                        current["dir"] += clean_text(line)
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
                    current["description"] = ""
                    desc_done = True
                    while line != "\n":
                        current["description"] += clean_text(line)
                        line = file.readline()
                if not line:
                    recipes.append(current)
                    break  # Stop when end of file is reached
    return recipes


try:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Config file not found")
    sys.exit()
except PermissionError:
    print("Permission denied on config file")
    sys.exit()

# os.listdir returns everything, so we filter using os.path.isfile
dir_path = config["dir_path"]
files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

recipes = read_recipes(config, files)

if config["exporter"]["name"] == "json":
    export_file = config["exporter"].get("file", "recipes.json")
    with open(export_file, "w") as file:
        json.dump(recipes, file)
elif config["exporter"]["name"] == "tamari":
    url = config["exporter"].get("url")
    user = config["exporter"].get("user")
    pw = config["exporter"].get("pw")
    insec = config["exporter"].get("insecure", False)
    if not url:
        print("url parameter not found in config file")
        sys.exit()
    if not user:
        print("user parameter not found in config file")
        sys.exit()
    if not pw:
        print("pw parameter not found in config file")
        sys.exit()
    tamari_import(url, user, pw, recipes, insec)
