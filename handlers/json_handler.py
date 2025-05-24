import os
import json
from markupsafe import Markup

def export_json(data, field_types, filename, upload_folder):
    outpath = os.path.join(upload_folder, "mock_data.json")
    with open(outpath, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return outpath

def extract_json_fields(data, prefix=""):
    fields = []
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                fields.extend(extract_json_fields(v, path))
            else:
                fields.append({"path": path, "value": v})
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            path = f"{prefix}[{idx}]"
            fields.extend(extract_json_fields(item, path))
    return fields

def render_json_with_controls(json_fields, allowed_data_types):
    # Similar to render_xml_with_controls, but for JSON fields
    TAG_INDENT = 20
    CONTROL_OFFSET = 180

    # Calculate the max option length for dropdown width
    max_option_length = max(len(dtype) for dtype in allowed_data_types)
    select_width = max(75, int(max_option_length * 0.65 * 16))  # 0.65em per char, 16px base font

    html = ""
    for field in json_fields:
        path = field["path"]
        value = field["value"]
        level = path.count('.') + path.count('[')  # crude indent for nested fields

        tag_style = f"display:inline-block; min-width:80px; margin-left:{level * TAG_INDENT}px; color:#b35c00;"
        open_tag = f"<span style='{tag_style}'>{path}</span>"

        controls = (
            f'<span style="position:relative; left:{CONTROL_OFFSET - (level * TAG_INDENT)}px; display:inline-flex; align-items:center;">'
            f'<select name="{path}_type" class="datatype-select" '
            f'data-default-value="{value}" '
            f'style="font-size:11px; height:18px; min-width:{select_width}px; width:auto; white-space:nowrap; margin-right:4px;">'
            f'<option value="Default" selected>Default</option>'
            + "".join(
                f'<option value="{dtype}">{dtype}</option>'
                for dtype in allowed_data_types
            )
            + "</select>"
            f'<input type="text" name="{path}_options" class="options-input" '
            f'data-field="{path}" placeholder="options" value="{value}" '
            f'style="width:70px; font-size:11px; height:16px; padding:0 2px;" />'
            f'<span class="options-error" data-field="{path}"></span>'
            f'</span>'
        )
        html += f"{open_tag}{controls}<br>"

    return Markup(html)