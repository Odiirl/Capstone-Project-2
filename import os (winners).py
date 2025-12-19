import os
import re
import pandas as pd

def parse_logs_winner_team(folder_path):
    data = []
    
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' was not found.")
        return

    filenames = [f for f in os.listdir(folder_path) if f.endswith(".log")]
    print(f"Found {len(filenames)} log files. Starting process...")

    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract Player Names and Winner
                p1_match = re.search(r'\|player\|p1\|([^|]+)', content)
                p2_match = re.search(r'\|player\|p2\|([^|]+)', content)
                winner_match = re.search(r'\|win\|([^|]+)', content)
                
                if not (p1_match and p2_match and winner_match):
                    continue
                
                p1_name = p1_match.group(1).strip()
                p2_name = p2_match.group(1).strip()
                winner_name = winner_match.group(1).strip()
                
                # Identify if p1 or p2 won to extract the correct team
                if winner_name == p1_name:
                    winner_tag = "p1"
                    loser_name = p2_name
                else:
                    winner_tag = "p2"
                    loser_name = p1_name
                
                # Extract the 6 Pokemon for the winner
                winner_team = re.findall(rf'\|poke\|{winner_tag}\|([^,|]+)', content)
                
                # Create row data
                row = {
                    "Filename": filename,
                    "Winner": winner_name,
                    "Loser": loser_name
                }
                
                # Distribute winner's Pokemon into separate columns
                for i in range(1, 7):
                    row[f"Winner Pokemon {i}"] = winner_team[i-1] if i-1 < len(winner_team) else ""
                    
                data.append(row)
        except Exception as e:
            print(f"Could not read file {filename}: {e}")

    if data:
        df = pd.DataFrame(data)
        
        # Ensure column order is clean
        cols = ["Filename", "Winner", "Loser"]
        cols += [f"Winner Pokemon {i}" for i in range(1, 7)]
        df = df[cols]
        
        # Save to Excel
        df.to_excel("winner_teams_results.xlsx", index=False)
        print(f"Done! Processed {len(data)} matches into winner_teams_results.xlsx")
    else:
        print("No valid battle logs with winners were found.")

if __name__ == "__main__":
    
    parse_logs_winner_team("logs")