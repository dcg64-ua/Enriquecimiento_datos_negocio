# scraping.py
import re
import requests
from bs4 import BeautifulSoup
import urllib3
from procesar_kml import leer_urls_desde_kml

# Desactiva advertencias de certificados SSL inválidos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Regex para buscar teléfonos (muy básica)
telefono_regex = re.compile(
    r'(\+?\d{2,3}\s?\d{3,}[\s-]?\d{2,}[\s-]?\d{2,})|(\b\d{3}[\s-]?\d{3}[\s-]?\d{3}\b)'
)
# Regex para redes sociales (facebook, instagram, etc.)
redes_regex = re.compile(
    r'(https?://(www\.)?(facebook|instagram|twitter|tiktok|linkedin)\.com/[^\s"\'<]+)'
)

def extraer_datos(url):
    """
    Visita una URL y extrae:
      - Título de la página
      - Teléfono
      - Horarios (incluyendo el caso de i.fa-clock)
      - Dirección (heurística)
      - Redes sociales (regex)
    Devuelve un dict con los resultados.
    """
    try:
        # verify=False omite errores de SSL si el certificado no es válido
        resp = requests.get(url, timeout=10, verify=False)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accediendo a {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # 1) Título
    titulo = soup.title.get_text(strip=True) if soup.title else "Sin título"

    # 2) Teléfono
    #    A) Busca un elemento con class="telefono"
    telefono_css = soup.select_one(".telefono")
    if telefono_css:
        telefono = telefono_css.get_text(strip=True)
    else:
        #    B) Si no se encuentra, intenta regex en todo el texto
        match_tel = telefono_regex.search(soup.get_text())
        telefono = match_tel.group(0) if match_tel else None

    # 3) Horarios
    horario = None

    # 3A) Caso especial: buscar si hay un icono <i class="fa-clock"> y extraer su texto adyacente
    clock_icon = soup.select_one('i.fa-clock')  # o i.fas.fa-clock, ajusta según tu HTML real
    if clock_icon:
        next_node = clock_icon.next_sibling
        if next_node and isinstance(next_node, str):
            posible_horario = next_node.strip()
            if posible_horario:
                horario = posible_horario

    # 3B) Si no hemos encontrado nada, buscamos en un div#horario
    if not horario:
        horario_div = soup.select_one("div#horario")
        if horario_div:
            horario = horario_div.get_text(strip=True)
        else:
            # 3C) Como fallback, cualquier etiqueta que contenga la palabra "horario"
            possible_horarios = soup.find_all(
                lambda tag: tag.name in ["div", "p", "li", "span"]
                and "horario" in tag.get_text().lower()
            )
            if possible_horarios:
                # Concatenamos los textos que tengan "horario"
                horario = " | ".join(ph.get_text(strip=True) for ph in possible_horarios)

    # 4) Dirección
    #    Buscamos "calle", "c/", "avenida", etc., en div/p/span
    direccion = None
    posibles_dir = soup.find_all(
        lambda tag: tag.name in ["div", "p", "span"]
        and any(pref in tag.get_text().lower() for pref in ["calle", "c/", "avenida", "avda", "av.", "carrer"])
    )
    if posibles_dir:
        # Divides el texto en líneas y coges las que parezcan direcciones
        lineas = posibles_dir[0].get_text(strip=True, separator="\n").split("\n")
        direcciones = [linea for linea in lineas if any(p in linea.lower() for p in ["calle", "c/", "avenida", "avda", "av.", "carrer"])]
        direccion = direcciones if direcciones else posibles_dir[0].get_text(strip=True)


    # 5) Redes sociales (busca enlaces a facebook, instagram, etc.)
    # 5) Redes sociales (busca enlaces a facebook, instagram, etc.)
    redes_encontradas = []
    possible_links = soup.find_all("a", href=True)

    for link in possible_links:
        href = link['href']
        if redes_regex.search(href):
            redes_encontradas.append(href)


    # Elimina duplicados manteniendo el orden
    redes_encontradas = list(dict.fromkeys(redes_encontradas))



    return {
        'url': url,
        'titulo': titulo,
        'telefono': telefono,
        'horarios': horario,
        'direccion': direccion,
        'redes_sociales': redes_encontradas
    }

def main():
    # 1) Lee el KML y obtiene las URLs
    ruta_kml = 'map.kml'  # Cambia si tu fichero KML se llama de otra forma
    urls = leer_urls_desde_kml(ruta_kml)
    print("URLs encontradas:", urls)

    # 2) Scrapear cada URL
    resultados = []
    for url in urls:
        datos = extraer_datos(url)
        if datos:
            resultados.append(datos)

    # 3) Mostrar o guardar los resultados
    for r in resultados:
        print(r)

if __name__ == "__main__":
    main()
