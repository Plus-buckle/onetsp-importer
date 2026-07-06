# Description
Code to take OneTsp backup files and import to other recipe apps.

## Quick Start
1. Clone this repo:

      ```git clone https://github.com/Plus-buckle/onetsp-importer.git```

2. Unzip Onetsp zip file
2. Set an environment variable to the directory that contains the recipes in text files

      ```export RECIPES='<directory path>'```

3. Create a minimal config file: 

```
echo "dir_path: \"${RECIPES}\"" > config.yaml
echo -e "exporter:\n  name: json" >> config.yaml
```

5. Run program: `python3 recipes.py`

## Helper Functions
There are a number of helper functions that transform the text. Currently they are:
* Convert units: Convert all units to abbreviation
* Convert minutes: Converts Onetsp time format
* Remove numbers: Removes Markdown-style numbering from the beginning of a string
* Fix heading: Converts Onetsp headings to Markdown-style
* Clean text: Converts special character format to normal character format

## Data Management
There is built in exporter to JSON file as shown above. Currently there is one supported recipe app to allow to import via API: [Tamari](https://github.com/alexbates/Tamari). See sample config file for needed options.

## Importers for other Recipe Apps
Contributions for importers for other apps are welcome. Use the Tamari importer as an example.
