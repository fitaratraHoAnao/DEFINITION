from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/recherche', methods=['GET'])
def recherche_definition():
    # Récupérer le paramètre 'definition' depuis l'URL
    mot = request.args.get('definition')
    if not mot:
        return jsonify({"erreur": "Veuillez spécifier un mot à rechercher via le paramètre 'definition'."}), 400

    # Construire l'URL de recherche
    url = f"https://cnrtl.fr/definition/{mot}"
    
    # Effectuer la requête vers le site CNRTL
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"erreur": "Impossible de récupérer les données du site CNRTL."}), 500

    # Parser le contenu HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraire le titre principal et type du mot
    titre_principal = soup.find("span", class_="tlf_cmot").get_text(strip=True)
    titre_type = soup.find("span", class_="tlf_ccode").get_text(strip=True)
    
    # Initialiser le dictionnaire des résultats
    resultats = {
        "mot": f"{titre_principal}, {titre_type}",
        "sections": []
    }
    
    # Texte final pour arrêter l'extraction
    texte_final = "Villey et V.-L. Saulnier, p. 146); 1854 « contenter ses besoins naturels » (Pommier, loc. cit.); 2. 1640 se satisfaire de (Corneille, Horace, I, 1). Empr. au lat.satisfacere"
    
    # Extraire toutes les sections et sous-sections
    for section in soup.select("div.tlf_parah"):
        section_titre = section.select_one("span.tlf_cplan b")
        section_emploi = section.select_one("span.tlf_cemploi")
        definition = section.select_one("span.tlf_cdefinition")

        # Section temporaire pour stocker les informations
        section_info = {
            "titre": section_titre.get_text(strip=True) if section_titre else "",
            "emploi": section_emploi.get_text(strip=True) if section_emploi else "",
            "definition": definition.get_text(strip=True) if definition else "",
            "exemples": []
        }

        # Ajouter les exemples associés à cette section
        for exemple in section.select("span.tlf_cexemple"):
            texte_exemple = exemple.get_text(strip=True)
            section_info["exemples"].append(texte_exemple)
            
            # Arrêter si le texte final est trouvé
            if texte_final in texte_exemple:
                resultats["sections"].append(section_info)
                return jsonify(resultats)

        # Ajouter la section complète aux résultats
        resultats["sections"].append(section_info)

    return jsonify(resultats)

# Lancer l'application sur l'hôte 0.0.0.0 et le port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
