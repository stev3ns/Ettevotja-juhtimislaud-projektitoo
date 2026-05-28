import subprocess
import sys
from datetime import datetime


def run(command: list[str]) -> None:
    print("=" * 80)
    print(f"Algus: {datetime.now().isoformat(timespec='seconds')}")
    print("Käivitan:", " ".join(command))
    print("=" * 80)

    result = subprocess.run(command, check=False)

    if result.returncode != 0:
        raise RuntimeError(f"Käsk ebaõnnestus: {' '.join(command)}")


def main() -> None:
    print("EMTA maksuvõlgade pipeline START")
    run([sys.executable, "scripts/download_emta_files.py"])
    run([sys.executable, "scripts/load_emta_staging.py"])
    print("EMTA maksuvõlgade pipeline FINISHED")


if __name__ == "__main__":
    main()