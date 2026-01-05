# VW_Elli

Tämä projekti käsittelee ja visualisoi Volkswagen Elli -latausaseman dataa.

## Toiminnallisuus

1. **Datan luku ja käsittely (`process_data.py`)**:
   - Lukee latausraportit PDF-tiedostoista (`files/` -kansiosta).
   - Puhdistaa datan ja muuntaa aikaleimat ja numerot oikeaan muotoon.
   - Tallentaa käsitellyn datan `Elli_Latausdata_PowerBI.xlsx` -tiedostoon.

2. **Visualisointi (`analysis.ipynb` & `visualize_data.py`)**:
   - `analysis.ipynb`: Jupyter Notebook, joka sisältää interaktiiviset kuvaajat latausdatasta (kulutus ajan yli, kestojen jakauma, viikonpäiväkohtainen kulutus).
   - `visualize_data.py`: Skripti, joka generoi ja tallentaa samat kuvaajat suoraan `.png` -tiedostoiksi `plots/` -kansioon.

## Käyttöohje

1. Lisää PDF-raportit `files/` -kansioon.
2. Aja datan käsittely: `python process_data.py`
3. Tutki dataa avaamalla `analysis.ipynb` Jupyter Notebookissa tai aja `python visualize_data.py` generoidaksesi kuvat.
4. Muokkaa lopulliseen esitettävään **Power BI** -muotoon Excel-tiedosto `Elli_Latausdata_PowerBI.xlsx`


