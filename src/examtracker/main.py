from __future__ import annotations
from examtracker.app import ExamTracker
from examtracker.settings import Settings, read_settings_from_config
from examtracker.database import create_database_engine


def main() -> int:
    config: Settings = read_settings_from_config(
        "/Users/samuel/Repositories/Examtracker/data/config.yml"
    )
    db_engine = create_database_engine(config.database_path)
    app = ExamTracker(db_engine)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
