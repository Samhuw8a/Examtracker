[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FSamhuw8a%2FExamtracker%2Fmaster%2Fpyproject.toml&color=d8634c)

# A Python examtracker for the "Lernphase"
Allows you to keep track of all the Exams you already finished and the scores you got.
Uses Sqlalchemy and sqlite for storing data and Textual as the TUI backend


# Instalation
- Clone the repository to your Computer
```bash
git clone https://github.com/Samhuw8a/Examtracker.git
```

- Install the Project on your computer
```bash
cd Examtracker
python -m pip install -e .
```
_You might have to add the --break-system-packages flag to the install command._


# Usage
Once installed the programm can be used like so:
```bash
examtracker
```

## Configuration
If you want to change the location of the db file you can do so inside a config file.
The Programm searches for a file called __config.yml__ at __~/.config/examtracker/__

<details>
<summary> default config.yml </summary>
```yaml
database_path: "<path to repo>/data/test.db"
css_path: "<path to repo>/data/style.css"
```
</details>

### Enviroment variables
All the configuration can be done with env-variables.
You can also change to location the programm searches for the config at.

<details>
<summary> Enviroment variables overview</summary>
```env
EXAMTRACKER_DATABASE_PATH=/tmp/test.db
EXAMTRACKER_CSS_PATH=/tmp/style.css

EXAMTRACKER_CONFIG=/tmp/config.yml
```
</details>
 

## SQL Tables
__exams__: ID; name; max\_points; scored\_points; class\_id

__classes__: ID; Name; semester\_id

__semester__: ID; Name (Unique),

## TODOS

- [x] Handle SQL Errors
- [x] Initialize DB
- [x] Settings.json file
- [x] Abort edit and add screens
- [x] system independant config searching
- [ ] better CSS
