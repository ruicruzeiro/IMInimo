import os
import time
import random
import requests
import pandas as pd
from deducoes_fixas import deducoes  # em 2026, muda a origem das keys/council_codes do deducoes_fixas.py para o csv de 2025 porque já lá estão todas :)
from bs4 import BeautifulSoup as bs

ano = "2025"
errors = 0
df_deductions = pd.DataFrame(columns=["codigo_concelho", "1", "2", "3 ou mais"])

for council_code in deducoes.keys():
    print(f"A extrair concelho {council_code}... ", end="")
    url = f"https://www.portaldasfinancas.gov.pt/pt/external/matrizes/imi/consultaDeducao.action?anoConsulta=2024&codigoMunicipio={council_code}"
    results = requests.get(url)
    soup = bs(results.text, features="html.parser")
    td_elements = soup.find_all("td", align="center")
    td_elements = [td_element.text for td_element in td_elements]

    if len(td_elements) != 9:
        errors += 1
        print("Error!")
        continue

    new_row = {}
    new_row["codigo_concelho"] = council_code

    for i in range(0, len(td_elements), 3):
        num_dependents = td_elements[i]
        deduction_value = int(td_elements[i + 1]) if td_elements[i + 2].lower() == "sim" else 0
        new_row[num_dependents] = deduction_value

    df_deductions = pd.concat([df_deductions, pd.DataFrame([new_row])], ignore_index=True)

    print("Ok!")
    # Mantendo o Portal das Finanças feliz
    request_delay = random.uniform(0.5, 1.5)
    time.sleep(request_delay)

df_deductions.to_csv(f"deducoes_{ano}.csv", encoding="utf-8", sep=";", index=False)
os.system(f"say 'Deduction parsing finished with {errors} errors!'")
