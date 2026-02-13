[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FSamhuw8a%2FExamtracker%2Fmaster%2Fpyproject.toml&color=d8634c)

# A Python examtracker for the "Lernphase"
Allows you to keep track of all the Exams you already finished and the scores you got.
Uses Sqlalchemy and sqlite for storing data and Textual as the TUI backend


# Instalation
Clone the repository to your mashine
```bash
git clone https://github.com/Samhuw8a/Examtracker.git
```

get the location of the config file on your system

MacOS:
```bash
cd Examtracker/data
echo "$(pwd)/config.yml" | pbcopy
```

Linux:
```bash
cd Examtracker/data
echo "$(pwd)/config.yml" | xclip -selection clipboard
```

Change the value in the main.py file
```
cd ../src/examtracker
```

## SQL Tables
__exams__: ID; name; max\_points; scored\_points; class\_id

__classes__: ID; Name; semester\_id

__semester__: ID; Name (Unique),

## TODOS

- [x] Handle SQL Errors
- [x] Initialize DB
- [x] Settings.json file
- [x] Abort edit and add screens
- [ ] system independant config searching
- [ ] better CSS
