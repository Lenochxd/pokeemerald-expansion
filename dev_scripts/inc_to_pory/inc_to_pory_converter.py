import os
import subprocess
import sys
from pathlib import Path

"""
this script converts .inc files to .pory files, which are used by poryscript.
It checks for the "DO NOT MODIFY" warning and skips those files, as well as empty files or files that are already in pory format.
After converting, it deletes the original .inc file.
"""

REMOVE_OLD_FILES = False
CONVERT_MAPS = False


def should_skip_file(inc_path: Path, pory_path: Path) -> bool:
    with inc_path.open("r", encoding="utf-8") as inc_file:
        content = inc_file.read()

    if "DO NOT MODIFY" in content:
        return True
    if content.replace(" ", "").replace("\n", "") == "":
        return True
    if pory_path.exists():
        return True
    return False


def iter_inc_files(data_dir: Path):
    for root, _, files in os.walk(data_dir):
        for file_name in files:
            if file_name.endswith(".inc") and (CONVERT_MAPS or not "data/maps" in str(Path(root))):
                yield Path(root) / file_name


def convert_file(converter_path: Path, inc_path: Path) -> Path:
    pory_path = inc_path.with_suffix(".pory")

    print(f"Converting {inc_path}...", flush=True)
    subprocess.run(
        [sys.executable, str(converter_path), str(inc_path), "-o", str(pory_path)],
        check=True,
    )

    if REMOVE_OLD_FILES:
        inc_path.unlink()
    else:
        inc_path.rename(inc_path.with_name(f"{inc_path.stem}_backup{inc_path.suffix}"))

    print(f"Converted {inc_path} to {pory_path}", flush=True)
    return pory_path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    converter_path = Path(__file__).resolve().with_name("inc_to_pory.py")

    if not converter_path.exists():
        print(f"Converter script not found: {converter_path}", file=sys.stderr)
        return 1

    print(f"Scanning {data_dir} for .inc files...", flush=True)

    converted_count = 0
    skipped_count = 0

    try:
        for inc_path in iter_inc_files(data_dir):
            pory_path = inc_path.with_suffix(".pory")
            if should_skip_file(inc_path, pory_path):
                skipped_count += 1
                continue

            convert_file(converter_path, inc_path)
            converted_count += 1
    except KeyboardInterrupt:
        print("Interrupted. Stopping conversion.", file=sys.stderr, flush=True)
        return 130
    except subprocess.CalledProcessError as error:
        print(f"Conversion failed for {inc_path}: exit code {error.returncode}", file=sys.stderr, flush=True)
        return error.returncode

    print(f"Finished. Converted {converted_count} file(s); skipped {skipped_count}.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
