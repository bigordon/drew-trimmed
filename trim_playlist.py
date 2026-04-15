import requests

# Use your DrewLive URL
URL = "http://drewlive2423.duckdns.org:8081/DrewLive/MergedCleanPlaylist.m3u8"

def main():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        lines = response.text.splitlines()

        # Keywords to exclude
        exclude = ["ANIME", "VOD", "ADULT", "MOVIES", "SERIES", "DREW", "MUSIC"]
        
        filtered = [lines[0]] # Keep #EXTM3U
        
        for i in range(1, len(lines) - 1, 2):
            metadata = lines[i]
            link = lines[i+1]
            
            # If the metadata doesn't contain excluded keywords, keep it
            if not any(word.upper() in metadata.upper() for word in exclude):
                filtered.append(metadata)
                filtered.append(link)

        with open("trimmed.m3u", "w") as f:
            f.write("\n".join(filtered))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
