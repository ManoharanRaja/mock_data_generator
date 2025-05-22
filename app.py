import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

from handlers.json_handler import export_json
from handlers.csv_handler import export_csv
from handlers.xml_handler import export_xml
from handlers.excel_handler import export_excel
from handlers.zip_handler import export_zip
from handlers.upload_handler import allowed_file, extract_fields

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
            return render_template("configure.html", fields=fields, filename=filename)
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
    field_types = {k: v for k, v in request.form.items() if k not in ("filename", "num_records", "export_type", "separate_files")}
    import random
    import faker
    fake = faker.Faker()
    data = []
    for _ in range(num_records):
        row = {}
        for field, dtype in field_types.items():
            if dtype == "Random Number":
                row[field] = random.randint(1, 1000)
            elif dtype == "Random Name":
                row[field] = fake.name()
            elif dtype == "Boolean":
                row[field] = random.choice([True, False])
            else:
                row[field] = ""
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
