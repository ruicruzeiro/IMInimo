import os
import io
import sys
import regex
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from logic import compute_savings
from taxas_imi import portugal, gondomar, espinho


app = Flask(__name__)


@app.route("/")
def index():
    """ Homepage/Short app presentation to the user """
    return render_template("index.html", current_page="index")


@app.route("/validate-pdf", methods=["POST"])
def validate_pdf():
    """ Route for PDF validation """
    file = request.files.get('pdf')
    if file and file.filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file.read()))
        text = " ".join([page.extract_text() for page in reader.pages]).replace("\n", " ")
        text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
        text = " ".join(text).replace("\n", "")

        if 'CADERNETA PREDIAL URBANA' and 'SERVIÇO DE FINANÇAS' and 'DADOS DE AVALIAÇÃO' in text:
            return jsonify({"valid": True}), 200
        else:
            return jsonify({"valid": False, "message": "Caderneta Predial Urbana inválida."}), 400
    else:
        return jsonify({"valid": False, "message": "Ficheiro inválido. O IMInimo só aceita PDF."}), 400


@app.route("/zone-confirm", methods=["POST"])
def zone_confirm():
    """ Confirmation of zone coefficient """

    file = request.files.get('pdf')
    reader = PdfReader(io.BytesIO(file.read()))
    text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
    text = " ".join(text).replace("\n", "")
    ext_calc = regex.findall('(?<=Vc x A x Ca x Cl x Cq x Cv )(.*)(?= Vt = valor patrimonial tributário)', text)
    ext_calc = ext_calc[0].split()
    Cl = float(ext_calc[8].replace('.', '').replace(',', '.'))
    Cl = f"{Cl:.2f}"

    return jsonify({"Cl": Cl, "text": text})


@app.route("/upload", methods=["POST"])
def upload():
    """ Page for the results of the calculation via PDF input """

    validated_zone_coef = request.form.get("zoneCoef")
    were_terms_accepted = request.form.get("zoneCheckbox")
    if were_terms_accepted != 'true':
        sys.exit("Invalid acceptance of terms & conditions and policies.")
    text = request.form.get("textInput")
    (
        successful_calculation,
        output_message,
        imi_display_dict
    ) = compute_savings("upload", text, {}, validated_zone_coef)

    return render_template(
        "upload.html",
        successful_calculation=successful_calculation,
        output_message=output_message,
        imi_display_dict=imi_display_dict
        ), 400


@app.route("/input", methods=["GET", "POST"])
def input():
    """ Page for manual input of CPU data """

    validated_zone_coef = False
    (
        successful_calculation,
        output_message,
        imi_display_dict
    ) = compute_savings("input", "", request.form, validated_zone_coef)

    return render_template(
        "input.html",
        successful_calculation=successful_calculation,
        output_message=output_message,
        imi_display_dict=imi_display_dict
        ), 400


@app.route("/invalid-pdf")
def invalid_pdf():
    """ Error page for invalid file types """
    return render_template("invalid_pdf.html")


zone_codes = {**portugal, **gondomar, **espinho}
@app.route("/zone-codes")
def get_zone_codes():
    return jsonify(list(zone_codes.keys()))


@app.route("/about")
def about():
    return render_template("about.html", current_page="about")


@app.route("/terms-conditions")
def terms_conditions():
    return render_template("terms_conditions.html")


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")


@app.route("/cookie-policy")
def cookie_policy():
    return render_template("cookie_policy.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
