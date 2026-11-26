# -*- coding: utf-8 -*-
"""Administrative CSV and JSON writers; no finite-element calculations."""
import csv
import json


def write_csv(path, columns, rows):
    """Write a CSV table using the specified column order."""
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def write_json(path, data):
    """Write human-readable UTF-8 JSON."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
