import os
import csv
import json
import xml.etree.ElementTree as ET
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

app = Flask(__name__)
app.secret_key = "mockdatakey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'csv', 'json', 'xml', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_fields(filepath, ext):
    if ext == 'csv':
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return reader.fieldnames
    elif ext in ['xlsx', 'xls']:
        df = pd.read_excel(filepath)
        return list(df.columns)
    elif ext == 'json':
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return list(data[0].keys())
            elif isinstance(data, dict):
                return list(data.keys())
    elif ext == 'xml':
        tree = ET.parse(filepath)
        root = tree.getroot()
        first = next(iter(root))
        return [elem.tag for elem in first]
    return []

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
    field_types = {k: v for k, v in request.form.items() if k not in ("filename", "num_records")}
    # Generate mock data
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
    # Save to CSV for download
    outpath = os.path.join(UPLOAD_FOLDER, "mock_data.csv")
    with open(outpath, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=field_types.keys())
        writer.writeheader()
        writer.writerows(data)
    return send_file(outpath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)