from xml.etree import ElementTree as ET
import re

def parse_kml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    urls = []
    for placemark in root.findall('.//kml:Placemark', ns):
        url_elem = placemark.find('.//kml:description', ns)
        if url_elem is not None and url_elem.text:
            matches = re.findall(r'https?://[^\s"<]+', url_elem.text)
            urls.extend([url.strip() for url in matches])
    return urls
