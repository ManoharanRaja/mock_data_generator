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

    # Function to prettify XML
    # for better readability
    # This function is used to format the XML string for better readability
    def prettify_xml(elem):
        import xml.dom.minidom
        rough_string = ET.tostring(elem, encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string.decode("utf-8"))
        # Return only the pretty XML string, without the XML declaration
        pretty_xml = reparsed.toprettyxml(indent="  ")
        # Remove the XML declaration if present
        pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if not line.strip().startswith('<?xml'))
        return pretty_xml.encode("utf-8")
    
    if separate_files:
        # Export each record as a separate file (example: JSON, CSV, XML, Excel)
        from zipfile import ZipFile
        import io
        zip_path = os.path.join(UPLOAD_FOLDER, "mock_data_records.zip")
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
                    # Default root tag and attributes
                    root_tag = "root"
                    root_attrib = {}
                    ext = filename.rsplit('.', 1)[1].lower()
                    if ext == "xml":
                        uploaded_tree = ET.parse(os.path.join(UPLOAD_FOLDER, filename))
                        uploaded_root = uploaded_tree.getroot()
                        root_tag = uploaded_root.tag
                        root_attrib = uploaded_root.attrib
                    # Create root node as in uploaded file
                    root = ET.Element(root_tag, root_attrib)
                    rec_elem = ET.SubElement(root, "Record")
                    for k, v in record.items():
                        elem = ET.SubElement(rec_elem, k)
                        elem.text = str(v)
                    xml_str = prettify_xml(root)
                    # Write XML declaration manually
                    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
                    zipf.writestr(record_path, xml_bytes)
                elif export_type in ["xlsx", "xls", "excel"]:
                    record_path = f"record_{record_num}.xlsx"
                    df = pd.DataFrame([record])
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False)
                    zipf.writestr(record_path, output.getvalue())
        return send_file(zip_path, as_attachment=True)
    else:
        # Export as a single file (JSON, CSV, XML, Excel)
        if export_type == "json":
            outpath = os.path.join(UPLOAD_FOLDER, "mock_data.json")
            with open(outpath, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif export_type == "csv":
            outpath = os.path.join(UPLOAD_FOLDER, "mock_data.csv")
            with open(outpath, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=field_types.keys())
                writer.writeheader()
                writer.writerows(data)
        elif export_type == "xml":
            outpath = os.path.join(UPLOAD_FOLDER, "mock_data.xml")
            # Default root tag and attributes
            root_tag = "Records"
            root_attrib = {}
            # If the uploaded file is XML, try to preserve root tag and attributes
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == "xml":
                tree = ET.parse(os.path.join(UPLOAD_FOLDER, filename))
                uploaded_root = tree.getroot()
                root_tag = uploaded_root.tag
                root_attrib = uploaded_root.attrib
            root = ET.Element(root_tag, root_attrib)
            for record in data:
                rec_elem = ET.SubElement(root, "Record")
                for k, v in record.items():
                    elem = ET.SubElement(rec_elem, k)
                    elem.text = str(v)
            xml_str = prettify_xml(root)
            # Write XML declaration manually
            with open(outpath, "wb") as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(xml_str)
        elif export_type in ["xlsx", "xls", "excel"]:
            outpath = os.path.join(UPLOAD_FOLDER, "mock_data.xlsx")
            df = pd.DataFrame(data)
            df.to_excel(outpath, index=False)
        else:
            flash("Unsupported export type.")
            return redirect(url_for("home"))
        return send_file(outpath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)