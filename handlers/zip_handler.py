import os
import csv
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import io

def prettify_xml(elem):
    import xml.dom.minidom
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(rough_string.decode("utf-8"))
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if not line.strip().startswith('<?xml'))
    return pretty_xml.encode("utf-8")

def export_zip(data, field_types, filename, upload_folder, export_type):
    ext = filename.rsplit('.', 1)[1].lower()
    root_tag = "Records"
    root_attrib = {}
    child_tag = "Record"
    if ext == "xml":
        tree = ET.parse(os.path.join(upload_folder, filename))
        uploaded_root = tree.getroot()
        root_tag = uploaded_root.tag
        root_attrib = uploaded_root.attrib
        first_child = next(iter(uploaded_root), None)
        if first_child is not None:
            child_tag = first_child.tag

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
                root = ET.Element(root_tag, root_attrib)
                rec_elem = ET.SubElement(root, child_tag)
                for k, v in record.items():
                    elem = ET.SubElement(rec_elem, k)
                    elem.text = str(v)
                xml_str = prettify_xml(root)
                xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
                zipf.writestr(record_path, xml_bytes)
            else:
                # Optionally handle other formats
                pass
    return zip_path