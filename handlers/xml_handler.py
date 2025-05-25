import os
import xml.etree.ElementTree as ET
from markupsafe import Markup

def prettify_xml(elem):
    import xml.dom.minidom
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(rough_string.decode("utf-8"))
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if not line.strip().startswith('<?xml'))
    return pretty_xml.encode("utf-8")

def export_xml(data, field_types, filename, upload_folder):
    ext = filename.rsplit('.', 1)[1].lower()
    root_tag, root_attrib, child_tag = "Records", {}, "Record"
    if ext == "xml":
        tree = ET.parse(os.path.join(upload_folder, filename))
        uploaded_root = tree.getroot()
        root_tag = uploaded_root.tag
        root_attrib = uploaded_root.attrib
        first_child = next(iter(uploaded_root), None)
        child_tag = first_child.tag if first_child is not None else "Record"
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

def extract_nodes_with_values(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    nodes = []

    def walk(node, path=""):
        tag = node.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        full_path = f"{path}/{tag}" if path else tag
        if node.text and node.text.strip():
            nodes.append({
                "path": full_path,
                "tag": tag,
                "value": node.text.strip()
            })
        for child in node:
            walk(child, full_path)
    walk(root)
    return nodes

def render_xml_with_controls(filepath, allowed_data_types):
    import xml.etree.ElementTree as ET

    tree = ET.parse(filepath)
    root = tree.getroot()

    TAG_INDENT = 20
    CONTROL_OFFSET = 180

    max_option_length = max(len(dtype) for dtype in allowed_data_types)
    select_width = max(75, int(max_option_length * 0.65 * 16))

    def render_node(node, allowed_data_types, path="", level=0, index=None):
        tag = node.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        # Always add index for repeated tags
        if index is not None:
            full_path = f"{path}/{tag}[{index}]"
        else:
            full_path = f"{path}/{tag}" if path else tag

        tag_style = f"display:inline-block; min-width:80px; margin-left:{level * TAG_INDENT}px; color:#b35c00;"
        open_tag = f"<span style='{tag_style}'>{tag}</span>"

        children = list(node)
        if children:
            # Count repeated tags among siblings
            tag_counts = {}
            for child in children:
                child_tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag
                tag_counts[child_tag] = tag_counts.get(child_tag, 0) + 1
            # Assign index to each child if there are multiple with the same tag
            tag_indices = {}
            inner = ""
            for child in children:
                child_tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag
                tag_indices[child_tag] = tag_indices.get(child_tag, 0) + 1
                child_index = tag_indices[child_tag] if tag_counts[child_tag] > 1 else None
                inner += render_node(child, allowed_data_types, full_path, level+1, child_index)
            return f"{open_tag}<br>{inner}"
        else:
            value = node.text.strip() if node.text and node.text.strip() else ""
            controls = ""
            if value:
                controls = (
                    f'<span style="position:relative; left:{CONTROL_OFFSET - (level * TAG_INDENT)}px; display:inline-flex; align-items:center;">'
                    f'<select name="{full_path}_type" class="data-type-select" '
                    f'data-field="{full_path}" '
                    f'data-default-value="{value}" '
                    f'style="font-size:11px; height:18px; min-width:{select_width}px; width:auto; white-space:nowrap; margin-right:4px;">'
                    f'<option value="Default" selected>Default</option>'
                    + "".join(
                        f'<option value="{dtype}">{dtype}</option>'
                        for dtype in allowed_data_types
                    )
                    + "</select>"
                    f'<input type="text" name="{full_path}_options" class="options-input" '
                    f'data-field="{full_path}" placeholder="options" value="{value}" '
                    f'style="width:70px; font-size:11px; height:16px; padding:0 2px;" />'
                    f'<span class="options-error" data-field="{full_path}"></span>'
                    f'</span>'
                )
                return f"{open_tag}{controls}<br>"
            else:
                return f"{open_tag}<br>"

    rendered = render_node(root, allowed_data_types)
    return Markup(rendered)

def extract_xml_structure(filepath):
    tree = ET.parse(filepath)
    uploaded_root = tree.getroot()
    root_tag = uploaded_root.tag
    root_attrib = uploaded_root.attrib
    first_child = next(iter(uploaded_root), None)
    child_tag = first_child.tag if first_child is not None else "Record"
    return root_tag, root_attrib, child_tag

def build_xml_tree(root_tag, root_attrib, child_tag, record):
    root = ET.Element(root_tag, root_attrib)
    rec_elem = ET.SubElement(root, child_tag)
    for k, v in record.items():
        elem = ET.SubElement(rec_elem, k)
        elem.text = str(v)
    return root