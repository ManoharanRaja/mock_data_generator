import os
import csv
import json
from zipfile import ZipFile
import io
from handlers.xml_handler import prettify_xml, extract_xml_structure, build_xml_tree

def export_zip(data, field_types, filename, upload_folder, export_type):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == "xml":
        root_tag, root_attrib, child_tag = extract_xml_structure(os.path.join(upload_folder, filename))
    else:
        root_tag, root_attrib, child_tag = "Records", {}, "Record"

    zip_path = os.path.join(upload_folder, "mock_data_records.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for idx, record in enumerate(data):
            record_num = idx + 1
            if export_type == "json":
                record_path = f"record_{record_num}.json"
                zipf.writestr(record_path, json.dumps(record, ensure_ascii=False, indent=2))
            elif export_type == "csv":
                record_path = f"record_{record_num}.csv"
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=field_types.keys())
                writer.writeheader()
                writer.writerow(record)
                zipf.writestr(record_path, output.getvalue())
            elif export_type == "xml":
                record_path = f"record_{record_num}.xml"
                root = build_xml_tree(root_tag, root_attrib, child_tag, record)
                xml_str = prettify_xml(root)
                xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
                zipf.writestr(record_path, xml_bytes)
            else:
                # Optionally handle other formats
                pass
    return zip_path