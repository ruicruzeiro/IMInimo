import io
import regex
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from logic import compute_savings
from taxas_imi import portugal, gondomar, espinho


app = Flask(__name__)


@app.route("/")
def index():
    """Homepage/Short app presentation to the user"""
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """ Page for loading of CPU document (PDF file) """

    if "pdf" not in request.files:
        output_message = "Tipo de ficheiro inválido. O IMInimo só aceita PDF."
        successful_calculation = False
        return render_template("upload.html", output_message=output_message), 400

    file = request.files["pdf"]

    if file.filename == "":
        output_message = "Ficheiro não seleccionado."
        successful_calculation = False
        return render_template("upload.html", output_message=output_message), 400

    if file and file.filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file.read()))
        text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
        text = " ".join(text).replace("\n", "")
        if 'CADERNETA PREDIAL URBANA' and 'SERVIÇO DE FINANÇAS' and 'DADOS DE AVALIAÇÃO' in text:
            successful_calculation, output_message = compute_savings("upload", text, {})
        else:
            return render_template(
                "upload.html",
                successful_calculation=False,
                output_message="Caderneta Predial Urbana inválida."), 400

        ext_calc = regex.findall('(?<=Vc x A x Ca x Cl x Cq x Cv )(.*)(?= Vt = valor patrimonial tributário)', text)
        ext_calc = ext_calc[0].split()
        Cl = float(ext_calc[8].replace('.', '').replace(',', '.'))
        Cl = f"{Cl:.2f}"
        return jsonify({"Cl": Cl})

        return render_template(
            "upload.html",
            successful_calculation=successful_calculation,
            output_message=output_message), 400


@app.route("/input", methods=["GET", "POST"])
def input():
    """Page for manual input of CPU data"""

    successful_calculation, output_message = compute_savings("input", "", request.form)

    return render_template(
        "input.html",
        successful_calculation=successful_calculation,
        output_message=output_message), 400


zone_codes = {**portugal, **gondomar, **espinho}
@app.route('/zone-codes')
def get_zone_codes():
    return jsonify(list(zone_codes.keys()))


if __name__ == "__main__":
    app.run(debug=True)
