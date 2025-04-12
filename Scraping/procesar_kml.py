# procesar_kml.py

import xml.etree.ElementTree as ET
import re

def leer_urls_desde_kml(ruta_kml):
    tree = ET.parse(ruta_kml)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    patron_url = re.compile(r'https?://[^\s]+')

    urls = []
    for placemark in root.findall('.//kml:Placemark', ns):
        description_elem = placemark.find('kml:description', ns)
        if description_elem is not None and description_elem.text:
            texto_desc = description_elem.text.strip()
            match = patron_url.search(texto_desc)
            if match:
                url = match.group(0)
                urls.append(url)
    return urls
