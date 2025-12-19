import os
import re
import pandas as pd

def parse_detailed_logs(folder_path):
    data = []
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return

    filenames = [f for f in os.listdir(folder_path) if f.endswith(".log")]
    print(f"Processing {len(filenames)} files...")

    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                # 1. Basic Info
                p1 = re.search(r'\|player\|p1\|([^|]+)', content)
                p2 = re.search(r'\|player\|p2\|([^|]+)', content)
                win = re.search(r'\|win\|([^|]+)', content)
                if not (p1 and p2 and win): continue

                p1_name, p2_name = p1.group(1).strip(), p2.group(1).strip()
                winner = win.group(1).strip()
                loser = p2_name if winner == p1_name else p1_name

                # 2. Initialize Data Structures
                # Format: { 'p1': { 'Pikachu': {'items': set(), 'moves': set()} } }
                discovery = {'p1': {}, 'p2': {}}
                
                # Pre-fill nicknames from |poke| lines
                for p_tag in ['p1', 'p2']:
                    pokes = re.findall(rf'\|poke\|{p_tag}\|([^,|]+)', content)
                    for p in pokes:
                        discovery[p_tag][p.strip()] = {'items': set(), 'moves': set()}

                # 3. Discovery Phase (Scan lines for moves and items)
                for line in lines:
                    # Detect Moves: |move|p1a: Groudon|Precice Blades|...
                    move_match = re.search(r'\|move\|(p1|p2)[ab]: ([^|]+)\|([^|]+)', line)
                    if move_match:
                        p_tag, p_name, move = move_match.groups()
                        if p_name in discovery[p_tag]:
                            discovery[p_tag][p_name]['moves'].add(move)

                    # Detect Items: |[from] item: Leftovers
                    item_match = re.search(r'\|(p1|p2)[ab]: ([^|]+)\|.*\[from\] item: ([^|]+)', line)
                    if item_match:
                        p_tag, p_name, item = item_match.groups()
                        if p_name in discovery[p_tag]:
                            discovery[p_tag][p_name]['items'].add(item)

                # 4. Flatten Data for Excel
                row = {"Filename": filename, "Winner": winner, "Loser": loser, "Trainer 1": p1_name, "Trainer 2": p2_name}
                
                for p_idx, p_tag in enumerate(['p1', 'p2'], 1):
                    p_list = list(discovery[p_tag].keys())
                    for i in range(6):
                        p_num = i + 1
                        name = p_list[i] if i < len(p_list) else ""
                        m_str = ", ".join(discovery[p_tag][name]['moves']) if name else ""
                        i_str = ", ".join(discovery[p_tag][name]['items']) if name else ""
                        
                        row[f"T{p_idx} P{p_num} Name"] = name
                        row[f"T{p_idx} P{p_num} Item"] = i_str
                        row[f"T{p_idx} P{p_num} Moves"] = m_str

                data.append(row)
        except Exception as e:
            print(f"Error in {filename}: {e}")

    df = pd.DataFrame(data)
    df.to_excel("detailed_battle_analysis.xlsx", index=False)
    print("Done! Check detailed_battle_analysis.xlsx")

if __name__ == "__main__":
    parse_detailed_logs("logs")