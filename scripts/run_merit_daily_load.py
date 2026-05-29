import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOOKBACK_DAYS = 14


def main() -> int:
    end_date = date.today()
    start_date = end_date - timedelta(days=LOOKBACK_DAYS)

    command = [
        sys.executable,
        "scripts/run_merit_backfill.py",
        "--start-date",
        start_date.isoformat(),
        "--end-date",
        end_date.isoformat(),
    ]

    print("=" * 80)
    print("Merit daily incremental load")
    print(f"Periood: {start_date.isoformat()} kuni {end_date.isoformat()}")
    print(f"Lookback: viimased {LOOKBACK_DAYS} päeva")
    print("Käsk:", " ".join(command))
    print("=" * 80)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
    )

    if result.returncode == 0:
        print("Merit daily load õnnestus.")
    else:
        print(f"Merit daily load ebaõnnestus. Return code: {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())