import os
import csv
import json
import xml.etree.ElementTree as ET
import pandas as pd

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