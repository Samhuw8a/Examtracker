![test](https://github.com/Samhuw8a/Examtracker/actions/workflows/test.yml/badge.svg) 
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FSamhuw8a%2FExamtracker%2Fmaster%2Fpyproject.toml&color=d8634c)

# Examtracker

A Python exam tracker for the **"Lernphase"**.  
It allows you to keep track of all exams you have completed and the scores you achieved.

The application uses:

- SQLAlchemy + SQLite for data storage  
- Textual as the TUI backend  

---

# Installation

```bash
python -m pip install examtracker
```

> You might need to add the `--break-system-packages` flag to the install command

---

# Usage

Once installed, you can start the program with:

```bash
examtracker
```

---

# Configuration

You can change the location of the database file using a configuration file.

By default, the program searches for:

```
~/.config/examtracker/config.yml
```

---

## Default `config.yml`

<details>
<summary>default configuration</summary>

```yaml
database_path: "~/.config/examtracker/examtracker.db"
database_uri: "sqllite:///~/.config/examtracker/examtracker.db"
```

</details>

---

## Environment Variables

All configuration options can also be set using environment variables.

You can even change the location where the program searches for the configuration file.

<details>
<summary>Environment variables</summary>

```env
EXAMTRACKER_DATABASE_PATH=/tmp/test.db
EXAMTRACKER_CSS_PATH=/tmp/style.css
EXAMTRACKER_CONFIG=/tmp/config.yml
```

</details>

Environment variables override values defined in `config.yml`.

---

# Database Schema

### `exams`
- `id`
- `name`
- `max_points`
- `scored_points`
- `class_id`

### `classes`
- `id`
- `name`
- `semester_id`
- `exam_grade`

### `semester`
- `id`
- `name` (unique)

---

# TODO

- [x] Handle SQL errors  
- [x] Initialize database  
- [x] Configuration file support  
- [x] Abort edit and add screens  
- [x] Cross-platform config discovery  
- [x] Improve CSS  
- [x] enable Editing Exams and Semester
- [x] Feature where you can add the grade you got in the exams
- [ ] Enable externaly hosted database in config
- [x] write Tests
- [x] automagicly push new pypi versions and make release upon github tag push tag push
