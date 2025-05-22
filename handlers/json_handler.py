import os
import json

def export_json(data, field_types, filename, upload_folder):
    outpath = os.path.join(upload_folder, "mock_data.json")
    with open(outpath, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return outpath