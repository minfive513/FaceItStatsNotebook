import json
import os
import pandas as pd
import requests

# Faceit API Key (ersetze mit deinem Key)



class FaceItApiClient:
    def __init__(self):
        with open("config.json", 'r', encoding='utf-8') as file:
                config = json.load(file)

        self.API_KEY = config["apiKey"]
        self.STEAM_ID = config["steamId"]
        self.HEADERS = {"Authorization": f"Bearer {self.API_KEY}"}
        self.CSV_MatchesFile = "faceit_match_data.csv"
        self.CSV_MatchDetailsFile = "faceit_match_details.csv"
    

    def getMatchHistory(self):
        data = self.get_player_stats(self.STEAM_ID)
        print(data)

        if data:
            df = self.parse_match_data(data)
            print(df)

            self.update_csv(df, self.CSV_MatchesFile) #Write CSV File

            csvData = pd.read_csv(self.CSV_MatchesFile) # Read CSV File
            
            print(csvData)
            
            if(df.equals(csvData)):
                print("No new Matches, do not update csv...")
            else:
                self.update_csv(df, self.CSV_MatchesFile)

            # Daten für das Modell aus CSV laden
            return df
        
    def getMatchHistoryDetails(self):
        matches = self.parse_match_data(self.get_player_stats(self.STEAM_ID))
        #matchesStats = [for matchId, playerId, createdAt, map in zip(df['Match ID'], df['Player Id'], df['Created At'], df['Map'])]
        matchesStats = [(row[0], row[1], row[2], row[3]) for row in matches[['Match ID', 'Player Id','Created At', 'Map']].to_numpy()]
        for match in matchesStats:
            data = self.get_match_stats(match[0])
            matches = self.parse_matchDetails_data(data, match[1], match[0], match[2], match[3])
            self.update_csv(matches, self.CSV_MatchDetailsFile)

    # Funktion zum Abrufen der CS2-Spielstatistiken eines Spielers
    def get_player_stats(self, steam_id, limit=100):
        url = f"https://open.faceit.com/data/v4/players/{steam_id}/games/cs2/stats?limit={limit}"
        response = requests.get(url, headers=self.HEADERS)
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
                "Player Id": stats.get("Player Id"),
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
                "ADR" : stats.get("ADR"),
                "K/R Ratio": stats.get("K/R Ratio"),
            })

        return pd.DataFrame(matches)
    

    def get_match_stats(self, match_id):
        url = f"https://open.faceit.com/data/v4/matches/{match_id}/stats"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        return response.json()
    

    def parse_matchDetails_data(self, data, playerId, matchId, created_at, map):
        matches = []
        for round in data.get('rounds', []):
            teams = round.get('teams', [])
            for team in teams:
                players = team.get('players')
                for player in players:
                    players_stats = player.get('player_stats', {})
                    player_id = player.get('player_id', {})
                    if(player_id == playerId):
                        matches.append({
                            "Match ID": matchId,
                            "Player ID": player_id,
                            "Player Name": player.get('nickname'),
                            "Created At": created_at,
                            "Map": map,

                            #Default stats
                            "Kills": players_stats.get("Kills"),
                            "Deaths": players_stats.get("Deaths"),
                            "Assists": players_stats.get("Assists"),
                            "Result": players_stats.get("Result"),
                            "Headshots": players_stats.get("Headshots"),
                            "Headshots %": players_stats.get("Headshots %"),
                            "Damage": players_stats.get("Damage"),
                            "MVPs": players_stats.get("MVPs"),

                            #Multi-kills
                            "Double Kills": players_stats.get("Double Kills"),
                            "Triple Kills": players_stats.get("Triple Kills"),
                            "Quadro Kills": players_stats.get("Quadro Kills"),
                            "Penta Kills": players_stats.get("Penta Kills"),
                            "Clutch Kills": players_stats.get("Clutch Kills"),
                            
                            #Special Weapon kills
                            "Pistol Kills": players_stats.get("Pistol Kills"),            
                            "Zeus Kills": players_stats.get("Zeus Kills"),
                            "Knife Kills": players_stats.get("Knife Kills"),
                            "Sniper Kills": players_stats.get("Sniper Kills"),
                            "Sniper Kill Rate per Match": players_stats.get("Sniper Kill Rate per Match"),
                            "Sniper Kill Rate per Round": players_stats.get("Sniper Kill Rate per Round"),

                            #Performance
                            "K/D Ratio": players_stats.get("K/D Ratio"),
                            "K/R Ratio": players_stats.get("K/R Ratio"),
                            "ADR": players_stats.get("ADR"),

                            #1v1
                            "1v1Count": players_stats.get("1v1Count"),
                            "1v1Wins": players_stats.get("1v1Wins"),
                            "Match 1v1 Win Rate": players_stats.get("Match 1v1 Win Rate"),

                            #1v2
                            "1v2Count": players_stats.get("1v2Count"),
                            "1v2Wins": players_stats.get("1v2Wins"),
                            "Match 1v2 Win Rate": players_stats.get("Match 1v2 Win Rate"),

                            #First Kills (entry kills????)
                            "First Kills": players_stats.get("First Kills"),
                            
                            #Entry Kills
                            "Entry Count": players_stats.get("Entry Count"),
                            "Entry Wins": players_stats.get("Entry Wins"),
                            "Match Entry Rate": players_stats.get("Match Entry Rate"),
                            "Match Entry Success Rate": players_stats.get("Match Entry Success Rate"),

                            #Utility
                            "Utility Count": players_stats.get("Utility Count"),
                            "Utility Damage": players_stats.get("Utility Damage"),
                            "Utility Enemies": players_stats.get("Utility Enemies"),
                            "Utility Damage Success Rate per Match": players_stats.get("Utility Damage Success Rate per Match"),
                            "Utility Success Rate per Match": players_stats.get("Utility Success Rate per Match"),
                            "Utility Usage per Round": players_stats.get("Utility Usage per Round"),
                            "Utility Damage per Round in a Match": players_stats.get("Utility Damage per Round in a Match"),
                            "Utility Successes": players_stats.get("Utility Successes"),
                            
                            #Flashes
                            "Flash Count": players_stats.get("Flash Count"),
                            "Enemies Flashed": players_stats.get("Enemies Flashed"),
                            "Flash Successes": players_stats.get("Flash Successes"),
                            "Enemies Flashed per Round in a Match": players_stats.get("Enemies Flashed per Round in a Match"),
                            "Flashes per Round in a Match": players_stats.get("Flashes per Round in a Match"),
                            "Flash Success Rate per Match": players_stats.get("Flash Success Rate per Match"),
                        })

        return pd.DataFrame(matches)
    

    # Funktion zum Speichern oder Aktualisieren der CSV-Datei
    def update_csv(self, new_data, csv_file=None):
        if os.path.exists(csv_file):
            existing_data = pd.read_csv(csv_file)
            combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=["Match ID"])
        else:
            combined_data = new_data

        combined_data.to_csv(csv_file, index=False)
        print(f"CSV-Datei aktualisiert: {len(combined_data)} Matches gespeichert.")

def main():
    faceit = FaceItApiClient()
    #faceit.getMatchHistory()
    faceit.getMatchHistoryDetails()
    

if __name__ == "__main__":
	main()
