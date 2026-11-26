"""Đổi số phiên bản ở mọi tệp trong .version-bump.json. Dùng: python scripts/bump-version.py 1.0.2
python scripts/bump-version.py --check: báo lỗi khi các tệp ghi số khác nhau (CI chạy lệnh này)."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = re.compile(r'("version"\s*:\s*")([^"]+)(")')


def files():
    return [ROOT / p for p in json.loads((ROOT / ".version-bump.json").read_text(encoding="utf-8"))["files"]]


def main(argv):
    if argv == ["--check"]:
        found = {p.relative_to(ROOT).as_posix(): VERSION.search(p.read_text(encoding="utf-8")).group(2) for p in files()}
        print(found)
        return 0 if len(set(found.values())) == 1 else 1
    if len(argv) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", argv[0]):
        print(__doc__)
        return 2
    for p in files():
        text = p.read_text(encoding="utf-8")
        new, n = VERSION.subn(lambda m: m.group(1) + argv[0] + m.group(3), text, count=1)
        if n != 1:
            print(f"{p}: không thấy trường version")
            return 1
        p.write_text(new, encoding="utf-8", newline="\n")
        print(f"{p.relative_to(ROOT).as_posix()}: {VERSION.search(text).group(2)} -> {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
