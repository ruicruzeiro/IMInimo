import regex
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
    Cl = float(ext_calc[8].replace('.', '').replace(',', '.'))
    Cq = float(ext_calc[10].replace('.', '').replace(',', '.'))
    Cv = get_Cv(registry_year)

    return vpt_current, A, Ca, Cl, Cq, Cv


def get_params_input(input_dict, registry_year):

    vpt_current = float(input_dict.get("VPTCurrent").replace(",", "."))
    A = float(input_dict.get("appraisalArea").replace(",", "."))
    Ca = float(input_dict.get("Ca").replace(",", "."))
    Cq = float(input_dict.get("Cq").replace(",", "."))
    Cl = float(input_dict.get("Cl").replace(",", "."))
    Cv = get_Cv(registry_year)

    return vpt_current, A, Ca, Cl, Cq, Cv


def compute_savings(calc_type, text, input_dict):
    """ Compute possible savings based on uploaded file and manual input """

    if calc_type == "upload":

        district_council, district_council_parish = get_zone_code(text)
        registry_year = get_registry_year(text)
        appraisal_date = get_appraisal_date(text)
        vpt_current, A, Ca, Cl, Cq, Cv = get_params_upload(text, registry_year)
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

    vpt_new = round(Vc * A * Ca * Cl * Cq * Cv, 2)

    if appraisal_date + relativedelta(years=3) > dt.date.today():
        output_message = (
            f"Ainda não é possível pedir uma reavaliação. A última "
            f"reavaliação deste imóvel foi feita em {str(appraisal_date)}. A "
            f"Autoridade Tributária impõe um período mínimo de 3 anos entre "
            f"reavaliações. Para saber se pode poupar no IMI, volte a esta "
            f"ferramenta no fim desse prazo, uma vez que vários parâmetros de "
            f"cálculo podem ser alterados pela Autoridade Tributária até lá."
        )

    elif vpt_new > vpt_current:
        output_message = (
            f"Não é aconselhável pedir já uma reavaliação. Uma "
            f"reavaliação pedida neste momento irá fazer subir o Valor Patrimonial "
            f"do imóvel para {str(int(vpt_new))} €. Esta situação poderá dever-se "
            f"à subida de alguns dos parâmetros de cálculo pela Autoridade Tributária."
        )

    elif vpt_new <= vpt_current:

        # em 2024, Gondomar e Espinho são os únicos concelhos com taxas diferentes em algumas freguesias

        if district_council == '1304':
            council_rate = gondomar[district_council_parish]
        elif district_council == '0107':
            council_rate = espinho[district_council_parish]
        else:
            council_rate = portugal[district_council]

        imi_current = int(round(vpt_current * council_rate, 0))
        imi_new = int(round(vpt_new * council_rate, 0))
        imi_savings = imi_current - imi_new

        if imi_savings >= 10:

            output_message = (
                f"Você pode passar a pagar menos IMI! Se pedir uma "
                f"reavaliação à Autoridade Tributária, o Valor Patrimonial do "
                f"imóvel passará a ser de {str(int(vpt_new))} € e o valor do IMI "
                f"anual a pagar de {str(imi_new)} €. Com a taxa de "
                f"{str(dt.date.today().year)}, a poupança anual de IMI neste "
                f"imóvel é de {str(int(round(imi_savings, 0)))} €!"
            )

        # não há poupança ou esta é inferior a 10 €.

        else:

            imi_savings_low = "{:.2f}".format(round(vpt_current \
                * council_rate, 2) - round(vpt_new * council_rate, 2))

            output_message = (
                f"Pode pagar menos, mas pode não compensar. Uma "
                f"reavaliação irá resultar numa poupança anual no IMI do imóvel "
                f"de {imi_savings_low} €. Recordamos que as reavaliações só podem "
                f"ser pedidas de 3 em 3 anos, pelo que deve analisar se esta é a "
                f"melhor opção para si. Consulte o seu Serviço de Finanças."
            )

    return successful_calculation, output_message
