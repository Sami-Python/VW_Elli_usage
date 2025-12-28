# VW_Elli - Projektipäiväkirja (Memo)

## 2025-12-28
- Projekti aloitettu.
- Luotu virtuaaliympäristö (`.venv`).
*source .venv/Scripts/activate*
- Luotu `requirements.txt` ja `README.md`.
- Asennettu kirjastot: `pdfplumber`, `pandas`, `openpyxl`.
- Luotu ja ajettu scripti `process_data.py`, joka muunsi PDF-latausraportit Power BI -yhteensopivaksi Excel-tiedostoksi (`Elli_Latausdata_PowerBI.xlsx`).
- Lisätty `matplotlib` ja `seaborn` kirjastot.
- Luotu visualisointiscripti `visualize_data.py`, joka tuotti kolme kuvaajaa `plots`-kansioon:
    - `consumption_over_time.png`
    - `duration_distribution.png`
    - `consumption_by_weekday.png`
- Päivitetty `process_data.py` suodattamaan pois 0 kWh lataukset. Rivien määrä putosi 72 -> 56. Excel ja kuvaajat generoitu uudelleen.
- Päivitetty `.gitignore` (lisätty `.venv`, `files/`, `*.xlsx`, `plots/`).
- Korjattu `process_data.py`: aikaleimat tallennetaan nyt tekstimuotoisina (YYYY-MM-DD HH:MM:SS), jotta Power BI ei näytä niitä Excel-sarjanumeroina.
