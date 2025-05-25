import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from routes.preview import preview_bp
from handlers.upload_handler import allowed_file

app = Flask(__name__)
app.secret_key = "mockdatakey"
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.register_blueprint(preview_bp)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files.get("datafile")
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            return redirect(url_for('preview.preview', filename=filename))
        else:
            flash("Invalid file type.")
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)