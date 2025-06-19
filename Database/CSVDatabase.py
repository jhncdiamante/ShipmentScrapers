import csv
import os
from prettytable import PrettyTable
from Helpers.logging_config import setup_logger

log = setup_logger()

class CSVDatabase:
    filename: str
    header_written: bool
    def __init__(self, filename):
        self.filename = filename
        self.header_written = os.path.exists(filename) and os.path.getsize(filename) > 0

    def update(self, data: dict) -> None:
        table = PrettyTable()
        table.field_names = [
            "Header",
            "Value",
        ]  # First column: header/key, second: value
        for key, value in data.items():
            table.add_row([key, value])
        log.info("Writing to CSV:\n%s", table)

        with open(self.filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())

            # Write header only once
            if not self.header_written:
                writer.writeheader()
                self.header_written = True

            writer.writerow(data)
