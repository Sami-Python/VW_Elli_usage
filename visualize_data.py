import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def visualize_data():
    input_file = "Elli_Latausdata_PowerBI.xlsx"
    
    if not os.path.exists(input_file):
        print(f"Virhe: Tiedostoa {input_file} ei löydy. Aja ensin process_data.py.")
        return

    print(f"Luetaan data tiedostosta: {input_file}")
    df = pd.read_excel(input_file)

    # Varmistetaan aikaleimojen tyyppi
    df["Start_Timestamp"] = pd.to_datetime(df["Start_Timestamp"])
    
    # Luodaan kuvaajille kansio
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)

    # Asetetaan tyyli
    sns.set_theme(style="whitegrid")

    # 1. Kulutus ajan yli (Viivakuvaaja)
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x="Start_Timestamp", y="Consumption_kWh", alpha=0.6)
    plt.title("Latauskulutus ajan yli")
    plt.xlabel("Päivämäärä")
    plt.ylabel("Kulutus (kWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/consumption_over_time.png")
    print(f"Tallennettu: {output_dir}/consumption_over_time.png")
    plt.close()

    # 2. Latauksien keston jakauma (Histogrammi)
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="Duration_Minutes", bins=20, kde=True)
    plt.title("Latauskestojen jakauma")
    plt.xlabel("Kesto (min)")
    plt.ylabel("Lukumäärä")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/duration_distribution.png")
    print(f"Tallennettu: {output_dir}/duration_distribution.png")
    plt.close()

    # 3. Kulutus viikonpäivittäin (Pylväskuvaaja)
    # Luodaan viikonpäivä-sarake (0=Maanantai, 6=Sunnuntai)
    df["Weekday"] = df["Start_Timestamp"].dt.day_name()
    # Järjestetään viikonpäivät oikeaan järjestykseen
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="Weekday", y="Consumption_kWh", estimator="sum", order=order, errorbar=None)
    plt.title("Kokonaiskulutus viikonpäivittäin")
    plt.xlabel("Viikonpäivä")
    plt.ylabel("Kokonaiskulutus (kWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/consumption_by_weekday.png")
    print(f"Tallennettu: {output_dir}/consumption_by_weekday.png")
    plt.close()

if __name__ == "__main__":
    visualize_data()
