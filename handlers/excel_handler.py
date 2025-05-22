import os
import pandas as pd

def export_excel(data, field_types, filename, upload_folder):
    outpath = os.path.join(upload_folder, "mock_data.xlsx")
    df = pd.DataFrame(data)
    df.to_excel(outpath, index=False)
    return outpath