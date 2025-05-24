import csv
from markupsafe import Markup

def extract_csv_fields(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        if reader:
            headers = list(reader[0].keys())
            # Replace None values with empty strings in the top 3 records
            records = []
            for row in reader[:3]:
                clean_row = {k: (v if v is not None else "") for k, v in row.items()}
                records.append(clean_row)
        else:
            f.seek(0)
            fieldnames = next(csv.reader(f), [])
            headers = list(fieldnames)
            records = [{header: "" for header in headers}]
    return headers, records

def render_csv_with_controls(headers, first_row, allowed_data_types):
    TAG_INDENT = 20
    CONTROL_OFFSET = 180
    max_option_length = max(len(dtype) for dtype in allowed_data_types)
    select_width = max(75, int(max_option_length * 0.65 * 16))

    html = ""
    for header in headers:
        value = first_row.get(header, "")
        tag_style = f"display:inline-block; min-width:80px; color:#b35c00;"
        open_tag = f"<span style='{tag_style}'>{header}</span>"

        value_tag = f"<span style='display:inline-block; min-width:100px; margin-left:10px; color:#333;'>{value}</span>"

        controls = (
            f'<span style="position:relative; left:{CONTROL_OFFSET}px; display:inline-flex; align-items:center;">'
            f'<select name="{header}_type" class="datatype-select" '
            f'data-default-value="{value}" '
            f'style="font-size:11px; height:18px; min-width:{select_width}px; width:auto; white-space:nowrap; margin-right:4px;">'
            f'<option value="Default" selected>Default</option>'
            + "".join(
                f'<option value="{dtype}">{dtype}</option>'
                for dtype in allowed_data_types
            )
            + "</select>"
            f'<input type="text" name="{header}_options" class="options-input" '
            f'data-field="{header}" placeholder="options" value="{value}" '
            f'style="width:70px; font-size:11px; height:16px; padding:0 2px;" />'
            f'<span class="options-error" data-field="{header}"></span>'
            f'</span>'
        )
        html += f"{open_tag}{value_tag}{controls}<br>"

    return Markup(html)