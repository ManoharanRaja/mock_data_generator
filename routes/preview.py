import os
import io
import json
from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash, current_app


from handlers.xml_handler import export_xml, render_xml_with_controls
from handlers.json_handler import export_json, extract_json_fields, render_json_with_controls
from handlers.csv_handler import extract_csv_fields, render_csv_with_controls
from handlers.excel_handler import extract_excel_fields, render_excel_with_controls
from handlers.data_generator import get_allowed_data_types, generate_field_value

preview_bp = Blueprint('preview', __name__)

@preview_bp.route("/preview/<filename>", methods=["GET", "POST"])
def preview(filename):
    UPLOAD_FOLDER = current_app.config.get("UPLOAD_FOLDER", "uploads")
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

    # POST: Handle Save Configuration or Generate Data
    action = request.form.get("action")
    ext = filename.rsplit('.', 1)[-1].lower()
    field_types = {}
    field_options = {}
    for k, v in request.form.items():
        if k in ("filename", "num_records", "export_type", "action"):
            continue
        elif k.endswith("_options"):
            field = k[:-8]
            field_options[field] = v
        elif k.endswith("_type"):
            field = k[:-5]
            field_types[field] = v

    if action == "save":
        config = {
            "source_file": filename,
            "filetype": ext,
            "fields": [
                {
                    "field": field,
                    "type": field_types.get(field, "Default"),
                    "options": field_options.get(field, "")
                }
                for field in field_types
            ]
        }
        config_json = json.dumps(config, indent=2)
        config_bytes = io.BytesIO(config_json.encode("utf-8"))
        download_name = f"{filename}.config.json"
        return send_file(
            config_bytes,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/json"
        )

    # POST: Generate and return the file
    num_records = int(request.form.get("num_records", 1))
    export_type = request.form.get("export_type", ext)
    data = []
    for _ in range(num_records):
        row = {}
        for field, dtype in field_types.items():
            options = field_options.get(field)
            row[field] = generate_field_value(dtype, options)
        data.append(row)

    if export_type == "json":
        outpath = export_json(data, field_types, filename, UPLOAD_FOLDER)
    elif export_type == "xml":
        outpath = export_xml(data, field_types, filename, UPLOAD_FOLDER)
    else:
        flash("Unsupported export type.")
        return redirect(url_for("home"))
    return send_file(outpath, as_attachment=True)