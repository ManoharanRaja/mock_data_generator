import os
import xml.etree.ElementTree as ET

def prettify_xml(elem):
    import xml.dom.minidom
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(rough_string.decode("utf-8"))
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if not line.strip().startswith('<?xml'))
    return pretty_xml.encode("utf-8")

def export_xml(data, field_types, filename, upload_folder):
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
    root = ET.Element(root_tag, root_attrib)
    for record in data:
        rec_elem = ET.SubElement(root, child_tag)
        for k, v in record.items():
            elem = ET.SubElement(rec_elem, k)
            elem.text = str(v)
    xml_str = prettify_xml(root)
    outpath = os.path.join(upload_folder, "mock_data.xml")
    with open(outpath, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)
    return outpath