import os
import csv

def export_csv(data, field_types, filename, upload_folder):
    outpath = os.path.join(upload_folder, "mock_data.csv")
    with open(outpath, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=field_types.keys())
        writer.writeheader()
        writer.writerows(data)
    return outpath