import requests
import re
import gzip
from lxml import etree

# URLs
M3U_URL = "http://drewlive2423.duckdns.org:8081/DrewLive/MergedCleanPlaylist.m3u8"
EPG_URL = "http://drewlive2423.duckdns.org:8081/DrewLive/DrewLive.xml.gz"

# Configuration
EXCLUDE_GROUPS = [
    "ANIME", "VOD", "ADULT", "MOVIES", "SERIES", "DREW", "MUSIC", 
    "AU", "CA", "EPL", "EU", "NZ", "UK", "JAPANTV", "AUSTRALIA", 
    "CANADA", "FRANCE", "MEXICO", "NEW ZEALAND", "SPAIN", 
    "UNITED KINGDOM", "ARGENTINA", "BRAZIL", "CHILE", "DENMARK", 
    "ITALY", "NORWAY", "SWEDEN", "INDIA", "SOUTH KOREA", 
    "SWITZERLAND", "TVPASS"
]

def main():
    # --- PART 1: TRIM M3U ---
    print("Fetching and trimming M3U...")
    try:
        r_m3u = requests.get(M3U_URL, timeout=30)
        r_m3u.raise_for_status()
        m3u_lines = r_m3u.text.splitlines()

        filtered_m3u = [m3u_lines[0]] # Keep #EXTM3U
        kept_ids = set()

        for i in range(1, len(m3u_lines) - 1, 2):
            metadata = m3u_lines[i]
            link = m3u_lines[i+1]
            
            group_match = re.search(r'group-title="([^"]+)"', metadata)
            group_name = group_match.group(1).upper() if group_match else ""
            
            # Check if group is allowed
            if not any(word in group_name for word in EXCLUDE_GROUPS):
                filtered_m3u.append(metadata)
                filtered_m3u.append(link)
                
                # Extract tvg-id for the EPG filter
                id_match = re.search(r'tvg-id="([^"]+)"', metadata)
                if id_match:
                    kept_ids.add(id_match.group(1))

        with open("trimmed.m3u", "w") as f:
            f.write("\n".join(filtered_m3u))
        print(f"M3U Done: Kept {len(filtered_m3u)//2} channels.")

        # --- PART 2: TRIM EPG ---
        print(f"Fetching and trimming EPG for {len(kept_ids)} IDs...")
        r_epg = requests.get(EPG_URL, timeout=60)
        r_epg.raise_for_status()
        
        xml_content = gzip.decompress(r_epg.content)
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(xml_content, parser=parser)

        # Remove channel tags not in our kept list
        for channel in tree.xpath('//channel'):
            if channel.get('id') not in kept_ids:
                channel.getparent().remove(channel)

        # Remove programme tags for removed channels
        for programme in tree.xpath('//programme'):
            if programme.get('channel') not in kept_ids:
                programme.getparent().remove(programme)

        # Save as compressed GZIP
        with gzip.open("trimmed_epg.xml.gz", "wb") as f:
            f.write(etree.tostring(tree, encoding='utf-8', xml_declaration=True))
        
        print("EPG Done: Created trimmed_epg.xml.gz")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()    with open("trimmed_epg.xml", "wb") as f:
        f.write(etree.tostring(tree, encoding='utf-8', xml_declaration=True))

if __name__ == "__main__":
    main()
