from __future__ import annotations

from examtracker.app import ExamTracker
from examtracker.database import create_database_engine
from examtracker.settings import Settings


def main() -> int:
    config: Settings = Settings()
    db_engine = create_database_engine(config.database_path)
    app = ExamTracker(db_engine, config)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
