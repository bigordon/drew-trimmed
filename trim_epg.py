import requests
import gzip
import re
from lxml import etree

EPG_URL = "http://drewlive2423.duckdns.org:8081/DrewLive/DrewLive.xml.gz"
M3U_FILE = "trimmed.m3u"

def get_kept_ids():
    """Extracts all tvg-id values from your trimmed M3U."""
    with open(M3U_FILE, 'r') as f:
        content = f.read()
    # Matches tvg-id="ID_HERE"
    return set(re.findall(r'tvg-id="([^"]+)"', content))

def main():
    kept_ids = get_kept_ids()
    print(f"Filtering EPG for {len(kept_ids)} channels...")

    response = requests.get(EPG_URL)
    xml_content = gzip.decompress(response.content)
    
    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring(xml_content, parser=parser)

    # 1. Remove <channel> tags not in our list
    for channel in tree.xpath('//channel'):
        if channel.get('id') not in kept_ids:
            channel.getparent().remove(channel)

    # 2. Remove <programme> tags for channels we don't have
    for programme in tree.xpath('//programme'):
        if programme.get('channel') not in kept_ids:
            programme.getparent().remove(programme)

    # Save the trimmed EPG
    with open("trimmed_epg.xml", "wb") as f:
        f.write(etree.tostring(tree, encoding='utf-8', xml_declaration=True))

if __name__ == "__main__":
    main()
