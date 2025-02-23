import os
import pandas as pd
import requests

# Faceit API Key (ersetze mit deinem Key)
API_KEY = "xxxxx"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
CSV_FILE = "faceit_match_data.csv"
player_id = "xxxx"  # Ersetze mit Faceit Player-ID

class FaceItApiClient:
    def __init__(self):
        pass

    def calculateWinProbability(self):
        data = pd.read_csv(CSV_FILE)
        pass
    

    def getMatchHistory(self):
        data = self.get_player_stats(player_id)
        print(data)

        if data:
            df = self.parse_match_data(data)
            print(df)

            self.update_csv(df) #Write CSV File

            csvData = pd.read_csv(CSV_FILE) # Read CSV File
            
            print(csvData)
            
            if(df.equals(csvData)):
                print("No new Matches, do not update csv...")
            else:
                self.update_csv(df)

            # Daten für das Modell aus CSV laden
            return df

    # Funktion zum Abrufen der CS2-Spielstatistiken eines Spielers
    def get_player_stats(self, player_id, limit=100):
        url = f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats?limit={limit}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        return response.json()
    
    # Funktion zum Extrahieren relevanter Match-Daten
    def parse_match_data(self, data):
        matches = []
        for match in data.get('items', []):
            stats = match.get('stats', {})

            matches.append({
                "Match ID": stats.get("Match Id"),
                "Created At": stats.get("Created At"),
                "Result": stats.get("Result"),
                "Map": stats.get("Map"),
                "Kills": stats.get("Kills"),
                "Assists": stats.get("Assists"),
                "Deaths": stats.get("Deaths"),
                "Headshots": stats.get("Headshots"),
                "Double Kills": stats.get("Double Kills"),
                "Triple Kills": stats.get("Triple Kills"),
                "Quadro Kills": stats.get("Quadro Kills"),
                "Penta Kills": stats.get("Penta Kills"),
                "K/D Ratio": stats.get("K/D Ratio"),
            })

        return pd.DataFrame(matches)
    
    # Funktion zum Speichern oder Aktualisieren der CSV-Datei
    def update_csv(self, new_data):
        if os.path.exists(CSV_FILE):
            existing_data = pd.read_csv(CSV_FILE)
            combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=["Match ID"])
        else:
            combined_data = new_data

        combined_data.to_csv(CSV_FILE, index=False)
        print(f"CSV-Datei aktualisiert: {len(combined_data)} Matches gespeichert.")

def main():
    faceit = FaceItApiClient()
    faceit.getMatchHistory()

if __name__ == "__main__":
	main()
