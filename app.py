import io
from flask import Flask, render_template, redirect, request, url_for
from PyPDF2 import PdfReader
from logic import compute_savings


app = Flask(__name__)


@app.route("/")
def index():
    """Homepage/Short app presentation to the user"""
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """ Page for loading of CPU document (PDF file) """

    if "pdf" not in request.files:
        output_message = "Error: invalid file type, expected PDF."
        return render_template("upload.html", output_message=output_message), 400


    file = request.files["pdf"]

    if file.filename == "":
        output_message = "Error: no selected file."
        return render_template("upload.html", output_message=output_message), 400


    if file and file.filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file.read()))
        text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
        text = " ".join(text).replace("\n", "")
        output_message = compute_savings(text)
        return render_template("upload.html", output_message=output_message), 400





@app.route("/input")
def input():
    """Page for manual input of CPU data"""
    return render_template("input.html")


if __name__ == "__main__":
    app.run(debug=True)
