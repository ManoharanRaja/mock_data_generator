import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

from handlers.upload_handler import allowed_file
from handlers.xml_handler import export_xml, render_xml_with_controls
from handlers.json_handler import export_json, extract_json_fields, render_json_with_controls
from handlers.csv_handler import extract_csv_fields, render_csv_with_controls
from handlers.excel_handler import extract_excel_fields, render_excel_with_controls
from handlers.data_generator import get_allowed_data_types, generate_field_value

app = Flask(__name__)
app.secret_key = "mockdatakey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files.get("datafile")
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            return redirect(url_for('preview', filename=filename))
        else:
            flash("Invalid file type.")
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/preview/<filename>", methods=["GET", "POST"])
def preview(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    if request.method == "GET":
        if ext == "xml":
            with open(filepath, "r", encoding="utf-8") as f:
                raw_xml = f.read()
            rendered_xml = render_xml_with_controls(filepath, get_allowed_data_types())
            return render_template(
                "preview_xml.html",
                filename=filename,
                raw_xml=raw_xml,
                rendered_xml=rendered_xml
            )
        elif ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                raw_json = f.read()
                json_data = json.loads(raw_json)
            fields = extract_json_fields(json_data)
            rendered_json = render_json_with_controls(fields, get_allowed_data_types())
            return render_template(
                "preview_json.html",
                filename=filename,
                raw_json=raw_json,
                rendered_json=rendered_json,
                allowed_data_types=get_allowed_data_types()
            )
        elif ext == "csv":
            headers, records = extract_csv_fields(filepath)
            rendered_csv = render_csv_with_controls(headers, records[0], get_allowed_data_types())
            return render_template(
                "preview_csv.html",
                filename=filename,
                rendered_csv=rendered_csv,
                rendered_csv_headers=list(headers),
                rendered_csv_records=records,
                allowed_data_types=get_allowed_data_types()
            )
        elif ext == "xlsx":
            headers, records = extract_excel_fields(filepath)
            rendered_excel = render_excel_with_controls(headers, records[0], get_allowed_data_types())
            return render_template(
                "preview_excel.html",
                filename=filename,
                rendered_excel=rendered_excel,
                rendered_excel_headers=list(headers),
                rendered_excel_records=records,
                allowed_data_types=get_allowed_data_types()
            )
        else:
            flash("Preview only supported for XML and JSON files at this time.")
            return redirect(url_for("home"))

    # POST: Generate and return the file
    num_records = int(request.form.get("num_records", 1))
    export_type = request.form.get("export_type", ext)
    separate_files = request.form.get("separate_files") == "true"
    field_types = {}
    field_options = {}
    for k, v in request.form.items():
        if k in ("filename", "num_records", "export_type", "separate_files"):
            continue
        elif k.endswith("_options"):
            field = k[:-8]
            field_options[field] = v
        elif k.endswith("_type"):
            field = k[:-5]
            field_types[field] = v

    data = []
    template_count = 1

    if ext == "xml":
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()
        template_records = []
        for child in root:
            record = {}
            for elem in child:
                record[elem.tag] = elem.text
            template_records.append(record)
        template_count = len(template_records)

        # For separate files, group each file as a set of persons
        if separate_files:
            grouped_data = []
            for i in range(num_records):
                group = []
                for t_idx, template in enumerate(template_records):
                    row = {}
                    for elem_tag in template.keys():
                        # Remove [t_idx] from the path so it matches the form field name
                        field_path = f"{root.tag}/{child.tag}/{elem_tag}"
                        dtype = field_types.get(field_path, "Default")
                        options = field_options.get(field_path)
                        if dtype == "Default":
                            row[elem_tag] = template.get(elem_tag, "")
                        else:
                            row[elem_tag] = generate_field_value(dtype, options)
                    group.append(row)
                grouped_data.append(group)
            from handlers.zip_handler import export_zip
            zip_path = export_zip(
                grouped_data, field_types, filename, UPLOAD_FOLDER, export_type, group_records=True
            )
            return send_file(zip_path, as_attachment=True)
        else:
            data = []
            for i in range(num_records):
                for t_idx, template in enumerate(template_records):
                    row = {}
                    for elem_tag in template.keys():
                        # Remove [t_idx] from the path so it matches the form field name
                        field_path = f"{root.tag}/{child.tag}/{elem_tag}"
                        dtype = field_types.get(field_path, "Default")
                        options = field_options.get(field_path)
                        if dtype == "Default":
                            row[elem_tag] = template.get(elem_tag, "")
                        else:
                            row[elem_tag] = generate_field_value(dtype, options)
                    data.append(row)
            outpath = export_xml(data, field_types, filename, UPLOAD_FOLDER)
            return send_file(outpath, as_attachment=True)

    elif ext == "json":
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        template_records = json_data if isinstance(json_data, list) else [json_data]
        template_count = len(template_records)

        if separate_files:
            grouped_data = []
            for i in range(num_records):
                group = []
                for t_idx, template in enumerate(template_records):
                    row = {}
                    for field in template.keys():
                        dtype = field_types.get(field, "Default")
                        options = field_options.get(field)
                        if dtype == "Default":
                            row[field] = template.get(field, "")
                        else:
                            row[field] = generate_field_value(dtype, options)
                    group.append(row)
                grouped_data.append(group)
            from handlers.zip_handler import export_zip
            zip_path = export_zip(
                grouped_data, field_types, filename, UPLOAD_FOLDER, export_type, group_records=True
            )
            return send_file(zip_path, as_attachment=True)
        else:
            data = []
            for i in range(num_records):
                for t_idx, template in enumerate(template_records):
                    row = {}
                    for field in template.keys():
                        dtype = field_types.get(field, "Default")
                        options = field_options.get(field)
                        if dtype == "Default":
                            row[field] = template.get(field, "")
                        else:
                            row[field] = generate_field_value(dtype, options)
                    data.append(row)
            outpath = export_json(data, field_types, filename, UPLOAD_FOLDER)
            return send_file(outpath, as_attachment=True)

    else:
        flash("Unsupported export type.")
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)