import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Définir les répertoires
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

# Créer les répertoires s'ils n'existent pas
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def extract_jorf_content(url, raw_path, processed_path):
    """
    Extrait et sauvegarde la structure de la page du Journal Officiel.
    :param url: URL de la page du Journal Officiel
    :param raw_path: Chemin où sauvegarder la page brute
    :param processed_path: Chemin où sauvegarder les données structurées
    """
    try:
        print(f"Accès à l'URL : {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Page récupérée avec succès.")
            # Sauvegarder la page brute dans le répertoire raw
            with open(raw_path, "wb") as file:
                file.write(response.content)
            print(f"Page brute sauvegardée dans {raw_path}")

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraire les données
            data = []
            sections = soup.find_all('div', {'data-noeud-jorf': '2'})
            for section in sections:
                section_title = section.find('h2').get_text(strip=True)
                subsections = section.find_all('div', {'data-noeud-jorf': '3'})
                for subsection in subsections:
                    subsection_title = subsection.find('h3').get_text(strip=True)
                    ministries = subsection.find_all('div', {'data-noeud-jorf': '4'})
                    for ministry in ministries:
                        ministry_title = ministry.find('h4').get_text(strip=True)
                        items = ministry.find_all('li')
                        for item in items:
                            title = item.find('a').get_text(strip=True)
                            link = "https://www.legifrance.gouv.fr" + item.find('a')['href']
                            nature = item.get('data-nature', 'N/A')
                            emetteur = item.get('data-emetteur', 'N/A')
                            data.append({
                                "section": section_title,
                                "subsection": subsection_title,
                                "ministry": ministry_title,
                                "title": title,
                                "nature": nature,
                                "emetteur": emetteur,
                                "link": link
                            })
            
            # Sauvegarder les données structurées dans le répertoire processed
            with open(processed_path, "w", encoding="utf-8") as file:
                import json
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Données structurées sauvegardées dans {processed_path}")

        else:
            print(f"Erreur HTTP lors de l'accès à la page : {response.status_code}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def generate_jo_url(base_number=278):
    """
    Génère l'URL pour le Journal Officiel en fonction de la date actuelle et d'un numéro de base.
    :param base_number: Numéro de base à partir duquel chercher.
    """
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    # Base du numéro pour aujourd'hui
    number = base_number
    url = f"https://www.legifrance.gouv.fr/jorf/jo/{year}/{month}/{day}/{number:04d}"
    return url

if __name__ == "__main__":
    # Générer l'URL pour le Journal Officiel
    jo_url = generate_jo_url()
    
    # Définir les chemins des fichiers
    today_str = datetime.now().strftime("%Y-%m-%d")
    raw_path = os.path.join(RAW_DIR, f"jo_{today_str}.html")
    processed_path = os.path.join(PROCESSED_DIR, f"jo_{today_str}.json")
    
    # Extraire et sauvegarder les données
    extract_jorf_content(jo_url, raw_path, processed_path)
