"""Recalculate Excel workbooks in LibreOffice and fail if any formula returns an error.

xlsxwriter stores formulas without cached values, so this is the only way to check
that the formulas actually work outside Excel.

Usage:
  python scripts/check_excel.py data/processed/knesset_25_2022.xlsx [...]
"""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import openpyxl
import uno
from com.sun.star.beans import PropertyValue

PORT = 2002


def prop(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p


def connect():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            return resolver.resolve(f"uno:socket,host=localhost,port={PORT};urp;StarOffice.ComponentContext")
        except Exception:
            time.sleep(1)
    raise RuntimeError("LibreOffice did not start")


def recalc(desktop, src: Path, dst: Path) -> None:
    doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(src.resolve())), "_blank", 0,
                                       (prop("Hidden", True),))
    doc.calculateAll()
    doc.storeToURL(uno.systemPathToFileUrl(str(dst)), (prop("FilterName", "Calc MS Excel 2007 XML"),))
    doc.close(True)


def count_errors(path: Path) -> dict[str, int]:
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    return {
        ws.title: sum(isinstance(v, str) and v.startswith("#") for row in ws.iter_rows(values_only=True) for v in row)
        for ws in wb
    }


def main(paths: list[str]) -> int:
    office = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
                               f"--accept=socket,host=localhost,port={PORT};urp;"],
                              stderr=subprocess.DEVNULL)
    failed = False
    try:
        ctx = connect()
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        with tempfile.TemporaryDirectory() as tmp:
            for path in map(Path, paths):
                out = Path(tmp) / path.name
                recalc(desktop, path, out)
                errors = count_errors(out)
                failed |= any(errors.values())
                print(f"{path}: {sum(errors.values())} error cells {errors}")
    finally:
        office.terminate()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
