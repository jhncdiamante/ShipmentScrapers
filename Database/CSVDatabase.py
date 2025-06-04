import csv
import os

class CsvObserver:
    def __init__(self, filename):
        self.filename = filename
        self.header_written = os.path.exists(filename) and os.path.getsize(filename) > 0

    def update(self, data):
        data = data
        if not data:
            print("No data to write.")
            return

        print("Writing to CSV:", data)  # DEBUG

        with open(self.filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())

            # Write header only once
            if not self.header_written:
                writer.writeheader()
                self.header_written = True

            writer.writerow(data)
