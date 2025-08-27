import os
import regex
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from taxas_imi import portugal, gondomar, espinho

### extrair informação relevante da CPU ###

def get_zone_code(text):
    district = regex.findall('(?<=DISTRITO: )\d+', text)
    council = regex.findall('(?<=CONCELHO: )\d+', text)
    parish = regex.findall('(?<=FREGUESIA: )\d+', text)
    district_council = district[0] + council[0]
    district_council_parish = district_council + parish[0]
    return district_council, district_council_parish


def get_registry_year(text):
    registry_year = regex.findall('(?<=Ano de inscrição na matriz: )(.*)(?= Valor patrimonial actual)', text)
    registry_year = int(registry_year[0])
    return registry_year


def get_appraisal_date(text):
    appraisal_date = regex.findall('(?<=Avaliada em : )(.*)', text)
    appraisal_date = appraisal_date[0].split()[0]
    appraisal_date = dt.datetime.strptime(appraisal_date, '%Y/%m/%d').date()
    return appraisal_date


def get_Cv(registry_year):
    """ Get the Cv coefficient (Coeficiente de Vetustez / Age Coefficient) """

    property_age = dt.date.today().year - registry_year

    if property_age < 2:
        Cv = 1.0
    elif property_age >= 2 and property_age <= 8:
        Cv = 0.9
    elif property_age >= 9 and property_age <= 15:
        Cv = 0.85
    elif property_age >= 16 and property_age <= 25:
        Cv = 0.8
    elif property_age >= 26 and property_age <= 40:
        Cv = 0.75
    elif property_age >= 41 and property_age <= 50:
        Cv = 0.65
    elif property_age >= 51 and property_age <= 60:
        Cv = 0.55
    elif property_age > 60:
        Cv = 0.4

    return Cv


def get_params_upload(text, registry_year):
    """ Get calculation parameters for the upload registry PDF option """

    ext_vpt = regex.findall('Valor patrimonial actual \(CIMI\):\s*€([\d,.]+)', text)
    vpt_current = float(ext_vpt[0].replace('.', '').replace(',', '.'))

    ext_calc = regex.findall('(?<=Vc x A x Ca x Cl x Cq x Cv )(.*)(?= Vt = valor patrimonial tributário)', text)
    ext_calc = ext_calc[0].split()

    A = float(ext_calc[4].replace('.', '').replace(',', '.'))
    Ca = float(ext_calc[6].replace('.', '').replace(',', '.'))
    Cq = float(ext_calc[10].replace('.', '').replace(',', '.'))
    Cv = get_Cv(registry_year)

    return vpt_current, A, Ca, Cq, Cv


def get_params_input(input_dict, registry_year):

    vpt_current = float(input_dict.get("VPTCurrent").replace(",", "."))
    A = float(input_dict.get("appraisalArea").replace(",", "."))
    Ca = float(input_dict.get("Ca").replace(",", "."))
    Cq = float(input_dict.get("Cq").replace(",", "."))
    Cl = float(input_dict.get("Cl").replace(",", "."))
    Cv = get_Cv(registry_year)

    return vpt_current, A, Ca, Cl, Cq, Cv


def currency_format(value):
    return f"{int(value):,}".replace(",", "\u2024") + "\u00A0€"


def get_deduction(council_code):
    """ Create a dictionary with the deduction value per dependent for the district_council """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "deducoes_2025.csv")
    df = pd.read_csv(
        csv_path,
        encoding="utf-8",
        sep=";",
        dtype={
        "codigo_concelho": str,
        "1": int,
        "2": int,
        "3 ou mais": int
        }
    )
    df["0"] = 0
    df_filtered = df.loc[df["codigo_concelho"] == str(council_code)]

    if not df_filtered.empty:
        return df_filtered.to_dict(orient="records")[0]
    else:
        return {"codigo_concelho": None, "1": None, "2": None, "3 ou mais": None}


def apply_deduction(imi_current, imi_new, deduction_dict, too_soon_for_new_appraisal, can_save_money):
    imi_display_dict = {}
    for key, deduction in deduction_dict.items():
        if key != "codigo_concelho":
            if too_soon_for_new_appraisal:
                imi_display_dict[key] = ""
            else:
                imi_display_dict[key] = (
                    f"IMI actual: {currency_format(imi_current - deduction)}<br>"
                    f"IMI após reavaliação: {currency_format(imi_new - deduction)}<br><br>"
                )
                if can_save_money:
                    imi_display_dict[key] += f"Menos IMI, mais para si!"
    return imi_display_dict


def compute_savings(calc_type, text, input_dict, validated_zone_coef):
    """ Compute possible savings based on uploaded file and manual input """

    if calc_type == "upload":

        district_council, district_council_parish = get_zone_code(text)
        registry_year = get_registry_year(text)
        appraisal_date = get_appraisal_date(text)
        vpt_current, A, Ca, Cq, Cv = get_params_upload(text, registry_year)
        Cl = float(validated_zone_coef.replace(",", "."))
        successful_calculation = True

    elif calc_type == "input":

        input_dict = input_dict.to_dict()
        district_council = input_dict.get("propertyDistrict") + input_dict.get("propertyCouncil")
        district_council_parish = district_council + input_dict.get("propertyParish")
        registry_year = int(input_dict.get("registryYear"))
        appraisal_date = input_dict.get("appraisalDate")
        appraisal_date = dt.datetime.strptime(appraisal_date, '%Y-%m-%d').date()
        vpt_current, A, Ca, Cl, Cq, Cv = get_params_input(input_dict, registry_year)
        successful_calculation = True

    # valor de construção em 26-07-2024 (última actualização deste código)
    Vc = 665.00 # Valor em 2022: 640; actualizado em 2023, mantido em 2024

    if district_council == '1304':
        council_rate = gondomar[district_council_parish]
    elif district_council == '0107':
        council_rate = espinho[district_council_parish]
    else:
        council_rate = portugal[district_council]

    vpt_new = round(Vc * A * Ca * Cl * Cq * Cv, 2)
    imi_current = round(vpt_current * council_rate, 0)
    imi_new = round(vpt_new * council_rate, 0)
    imi_savings = imi_current - imi_new

    too_soon_for_new_appraisal = False
    can_save_money = False

    if appraisal_date + relativedelta(years=3) > dt.date.today():

        too_soon_for_new_appraisal = True

        output_message = (
            f"Ainda não é possível pedir uma reavaliação.<br><br>A última "
            f"reavaliação deste imóvel foi feita em {str(appraisal_date)}. A "
            f"Autoridade Tributária impõe um período mínimo de 3 anos entre "
            f"reavaliações.<br><br>Para saber se pode poupar no IMI, volte a esta "
            f"ferramenta no fim desse prazo, uma vez que vários parâmetros de "
            f"cálculo podem ser alterados pela Autoridade Tributária até lá."
        )

    elif vpt_new > vpt_current:

        output_message = (
            f"Não é aconselhável pedir já uma reavaliação.<br><br>Uma "
            f"reavaliação pedida neste momento irá fazer subir o Valor Patrimonial "
            f"do imóvel. Esta situação poderá dever-se à subida de alguns dos"
            f"parâmetros de cálculo pela Autoridade Tributária.<br><br>"
            f"Valor Patrimonial actual: {currency_format(vpt_current)}<br>"
            f"Valor Patrimonial após reavaliação: {currency_format(vpt_new)}<br><br>"
            f"Aumento do IMI: {currency_format(abs(imi_savings))}<br><br>"
        )

    elif vpt_new <= vpt_current:
        # em 2024, Gondomar e Espinho são os únicos concelhos com taxas diferentes em algumas freguesias

        if imi_savings >= 10:

            can_save_money = True

            output_message = (
                f"Você pode passar a pagar menos IMI!<br><br>Poderá poupar "
                f"{currency_format(imi_savings)} por ano se pedir uma "
                f"reavaliação à Autoridade Tributária. O Valor Patrimonial do "
                f"imóvel irá reduzir e, com ele, o valor do IMI anual a pagar "
                f"(à taxa de {str(dt.date.today().year)}).<br><br>"
                f"Valor Patrimonial actual: {currency_format(vpt_current)}<br>"
                f"Valor Patrimonial após reavaliação: {currency_format(vpt_new)}<br><br>"
                f"Redução do IMI: {currency_format(imi_savings)}<br><br>"
            )

        # não há poupança ou esta é inferior a 10 €.
        else:

            imi_savings_low = "{:.2f}".format(round(vpt_current \
                * council_rate, 2) - round(vpt_new * council_rate, 2)) + "\u00A0€"

            output_message = (
                f"Pode pagar menos IMI, mas pode não compensar.<br><br>Uma "
                f"reavaliação irá resultar numa poupança anual no IMI do imóvel "
                f"de {imi_savings_low}.<br><br>Recordamos que as reavaliações "
                f"só podem ser pedidas de 3 em 3 anos, pelo que deve analisar "
                f"se esta é a melhor opção para si. Recomendamos que "
                f"consulte o seu Serviço de Finanças.<br><br>"
                f"Valor Patrimonial actual: {currency_format(vpt_current)}<br>"
                f"Valor Patrimonial após reavaliação: {currency_format(vpt_new)}<br><br>"
                f"Redução do IMI: {imi_savings_low}<br><br>"
            )

    deduction_dict = get_deduction(district_council)
    imi_display_dict = apply_deduction(
        imi_current,
        imi_new,
        deduction_dict,
        too_soon_for_new_appraisal,
        can_save_money
        )

    return successful_calculation, output_message, imi_display_dict
