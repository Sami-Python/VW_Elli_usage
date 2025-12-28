import pdfplumber
import pandas as pd
import re
import glob
import os

# Funktio aikaleimojen erottamiseen (Start & End)
def split_timestamps(timestamp_str):
    if not isinstance(timestamp_str, str):
        return None, None
    # Regex etsii muotoa: DD.MM.YYYY HH:MM
    pattern = r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})"
    matches = re.findall(pattern, timestamp_str)
    
    if len(matches) >= 2:
        return matches[0], matches[1]
    elif len(matches) == 1:
        return matches[0], None
    return None, None

def process_pdfs():
    # Haetaan kaikki PDF-tiedostot files-kansiosta
    pdf_files = glob.glob(os.path.join("files", "*.pdf"))
    
    if not pdf_files:
        print("Ei PDF-tiedostoja löytynyt 'files'-kansiosta.")
        return

    print(f"Löydettiin {len(pdf_files)} PDF-tiedostoa. Aloitetaan käsittely...")
    
    all_data = []

    # 1. Luetaan PDF:t ja siivotaan solut
    for file_path in pdf_files:
        print(f"Käsitellään: {os.path.basename(file_path)}")
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            # Puhdistetaan solut: korvataan rivinvaihdot välilyönneillä
                            cleaned_row = [str(cell).replace('\n', ' ').strip() if cell is not None else '' for cell in row]
                            
                            # Suodatus: Varmistetaan että rivillä on dataa, se ei ole sivunumero eikä otsikkorivi sivun vaihtuessa
                            # Tarkistetaan, että rivi ei ole tyhjä ja ei sisällä sanaa "Page" ensimmäisessä solussa
                            if any(cleaned_row) and "Page" not in cleaned_row[0]:
                                # Lisätään vain jos ei ole otsikkorivi (tarkistetaan myöhemmin dataframessa, mutta voidaan skipata tässäkin jos halutaan)
                                all_data.append(cleaned_row)
        except Exception as e:
            print(f"Virhe tiedoston {file_path} käsittelyssä: {e}")

    if not all_data:
        print("Ei dataa löydetty.")
        return

    # 2. Luodaan DataFrame
    # Oletetaan, että sarakkeet ovat nämä (tarkista PDF:stä jos otsikot vaihtelee)
    columns = ["Record date", "Consumption", "Home charger", "Authentication", "Raw_Time"]
    
    # Koska taulukoissa voi olla vaihteleva määrä sarakkeita tai roskadataa, varmistetaan että otetaan vain 5 saraketta
    # Jos rivillä on enemmän tai vähemmän, pitää käsitellä. Tässä oletetaan, että rakenne on vakio.
    # Suodatetaan rivit, joilla on oikea määrä sarakkeita (5)
    valid_data = [row for row in all_data if len(row) == 5]
    
    if len(valid_data) < len(all_data):
        print(f"Varoitus: {len(all_data) - len(valid_data)} riviä hylättiin väärän sarakemäärän vuoksi.")

    df = pd.DataFrame(valid_data, columns=columns)

    # 3. Poistetaan otsikkorivit ja tyhjät rivit
    # Otsikkorivit tunnistetaan siitä, että "Record date" on sarakkeen arvona
    df = df[df["Record date"] != "Record date"]
    df = df[df["Consumption"] != ""]
    
    # Poistetaan mahdolliset duplikaatit, jos sama faili luettu vahingossa kahdesti (ei tässä logiikassa, mutta hyvä varotoimi)
    df.drop_duplicates(inplace=True)

    # 4. Aikaleimojen käsittely
    print("Käsitellään aikaleimoja...")
    df[["Start_Timestamp", "End_Timestamp"]] = df["Raw_Time"].apply(
        lambda x: pd.Series(split_timestamps(x))
    )

    # Muunnetaan oikeiksi datetime-objekteiksi.
    df["Start_Timestamp"] = pd.to_datetime(df["Start_Timestamp"], dayfirst=True, errors='coerce')
    df["End_Timestamp"] = pd.to_datetime(df["End_Timestamp"], dayfirst=True, errors='coerce')

    # 5. Lasketaan kesto (Duration)
    df["Duration_Minutes"] = (df["End_Timestamp"] - df["Start_Timestamp"]).dt.total_seconds() / 60

    # 6. Numeroiden puhdistus
    # "Consumption" kenttä: "12,5 kWh" -> 12.5 (muutetaan pilkku pisteeksi jos tarve, tässä str.replace hoitaa yksikön)
    # Huom: Jos luvussa on pilkku desimaalierottimena, se pitää vaihtaa pisteeksi Pythonia varten
    df["Consumption_kWh"] = df["Consumption"].str.replace(" kWh", "").str.replace(",", ".").astype(float)
    
    # SUODATUS: Poistetaan rivit, joissa kulutus on 0
    df = df[df["Consumption_kWh"] > 0]
    
    # 7. Siistitään sarakkeet Power BI -ystävälliseen järjestykseen
    # Valitaan sarakkeet lopulliseen tiedostoon
    final_df = df[[
        "Duration_Minutes", 
        "Consumption_kWh", 
        "Home charger", 
        "Authentication",
        "Start_Timestamp", 
        "End_Timestamp"
    ]].copy() # Käytetään .copy() jotta vältetään slice-ongelmat
    
    # Lajitellaan aikajärjestykseen
    final_df = final_df.sort_values(by="Start_Timestamp")
    
    # Formatoidaan Timestamp-sarakkeet stringeiksi (kuten aiemmin sovittiin)
    # Varmistetaan että tyyppi on datetime ennen .dt-kutsua
    final_df["Start_Timestamp"] = pd.to_datetime(final_df["Start_Timestamp"])
    final_df["End_Timestamp"] = pd.to_datetime(final_df["End_Timestamp"])

    final_df["Start_Timestamp"] = final_df["Start_Timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
    final_df["End_Timestamp"] = final_df["End_Timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # 8. Tallennus Exceliin
    output_filename = "Elli_Latausdata_PowerBI.xlsx"
    
    # Power BI fix: Muunnetaan aikaleimat merkkijonoiksi (String), jotta Power BI ei näytä niitä Excel-sarjanumeroina (esim. 45761.46)
    # Tämä pakottaa Power BI:n tunnistamaan ne päivämäärinä tai tekstinä, jonka se osaa parsia.
    # HUOM: Tämä tehtiin jo yllä, joten tässä ei tarvitse tehdä mitään uutta muunnosta.
    # Varmistetaan vain tallennus.

    try:
        final_df.to_excel(output_filename, index=False)
        print(f"Valmis! Tiedosto tallennettu: {output_filename}")
        print(f"Rivien määrä: {len(final_df)}")
        print(final_df.head())
    except Exception as e:
        print(f"Virhe tallennuksessa: {e}")

if __name__ == "__main__":
    process_pdfs()
