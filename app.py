import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

from handlers.json_handler import export_json
from handlers.csv_handler import export_csv
from handlers.xml_handler import export_xml
from handlers.excel_handler import export_excel
from handlers.zip_handler import export_zip
from handlers.upload_handler import allowed_file, extract_fields
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
            ext = filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            fields = extract_fields(filepath, ext)
            if not fields:
                flash("Could not extract fields from file.")
                return redirect(url_for("home"))
            allowed_data_types = get_allowed_data_types()
            return render_template(
                "configure.html",
                fields=fields,
                filename=filename,
                allowed_data_types=allowed_data_types
            )
        else:
            flash("Invalid file type.")
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/generate", methods=["POST"])
def generate():
    filename = request.form["filename"]
    num_records = int(request.form["num_records"])
    export_type = request.form.get("export_type", "csv")
    separate_files = request.form.get("separate_files") == "true"
    
    # Separate data types and options
    field_types = {}
    field_options = {}
    for k, v in request.form.items():
        if k in ("filename", "num_records", "export_type", "separate_files"):
            continue
        elif k.endswith("_options"):
            field = k[:-8]  # Remove '_options' suffix
            field_options[field] = v
        else:
            field_types[k] = v
    
    data = []
    for _ in range(num_records):
        row = {}
        for field, dtype in field_types.items():
            options = field_options.get(field)
            row[field] = generate_field_value(dtype, options)
        data.append(row)

    if separate_files:
        # Export each record as a separate file (ZIP)
        zip_path = export_zip(data, field_types, filename, UPLOAD_FOLDER, export_type)
        return send_file(zip_path, as_attachment=True)
    else:
        # Export as a single file
        if export_type == "json":
            outpath = export_json(data, field_types, filename, UPLOAD_FOLDER)
        elif export_type == "csv":
            outpath = export_csv(data, field_types, filename, UPLOAD_FOLDER)
        elif export_type == "xml":
            outpath = export_xml(data, field_types, filename, UPLOAD_FOLDER)
        elif export_type in ["xlsx", "xls", "excel"]:
            outpath = export_excel(data, field_types, filename, UPLOAD_FOLDER)
        else:
            flash("Unsupported export type.")
            return redirect(url_for("home"))
        return send_file(outpath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)