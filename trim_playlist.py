import requests
import re

# Use your DrewLive URL
URL = "http://drewlive2423.duckdns.org:8081/DrewLive/MergedCleanPlaylist.m3u8"

def main():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        lines = response.text.splitlines()

        # Groups you want to explicitly BLOCK (Group-Title only)
        exclude_groups = [
            "ANIME", "VOD", "ADULT", "MOVIES", "SERIES", "DREW", "MUSIC", 
            "AU", "CA", "EPL", "EU", "NZ", "UK", "JAPANTV", "AUSTRALIA", 
            "CANADA", "FRANCE", "MEXICO", "NEW ZEALAND", "SPAIN", 
            "UNITED KINGDOM", "ARGENTINA", "BRAZIL", "CHILE", "DENMARK", 
            "ITALY", "NORWAY", "SWEDEN", "INDIA", "SOUTH KOREA", 
            "SWITZERLAND", "TVPASS"
        ]
        
        filtered = [lines[0]] # Keep the #EXTM3U header
        
        # We loop through lines in steps of 2 (Metadata line + URL line)
        for i in range(1, len(lines) - 1, 2):
            metadata = lines[i]
            link = lines[i+1]
            
            # Use regex to find the content inside group-title="..."
            group_match = re.search(r'group-title="([^"]+)"', metadata)
            group_name = group_match.group(1).upper() if group_match else ""
            
            # Logical check: Only exclude if the keyword is found specifically in the GROUP NAME
            if not any(word in group_name for word in exclude_groups):
                filtered.append(metadata)
                filtered.append(link)

        with open("trimmed.m3u", "w") as f:
            f.write("\n".join(filtered))
        
        print(f"Success! Processed {len(lines)//2} channels down to {len(filtered)//2}.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
