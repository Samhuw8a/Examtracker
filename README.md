[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FSamhuw8a%2FExamtracker%2Fmaster%2Fpyproject.toml&color=d8634c)

# A Python examtracker for the "Lernphase"
Allows you to keep track of all the Exams you already finished and the scores
Uses Sqlalchemy and sqlite for storing data


## Data structure
'''
- semster
    - class
        - Exams [data, score]
'''

## Tables
__exams__: ID; name; max\_points; scored\_points; class\_id

__classes__: ID; Name; semester\_id

__semester__: ID; Name,


# TODOS

- [  ] Handle SQL Errors
- [  ] Initialize DB
- [  ] Settings.json file
