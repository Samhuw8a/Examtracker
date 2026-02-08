from __future__ import annotations
from examtracker.app import ExamTracker


def main() -> int:
    app = ExamTracker()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
