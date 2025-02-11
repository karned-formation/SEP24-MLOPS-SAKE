import requests

endpoint_url = 'http://localhost:9095/predict'
data_dict = [
    {
        "ref": "707b5d9f-1632-408f-ac53-f3ac87395b54/ocerized_raw/img_0000080.jpg",
        "data": "français république carte national r'identité aliin3gi/ card bueuns sur von martin pec men prénoms/ given name maëlis gaëll marie sexe /sex nationalit nationaity date naiss1 ofbirth fra 13 07 1990 lieu naissance place of birth nom usage iallemate .n documenti documentno 5380z9ae9 pari dexpir / expiry ll 02 2030 804465 jignatur"
    },
    {
        "ref": "707b5d9f-1632-408f-ac53-f3ac87395b54/ocerized_raw/img_0000060.jpg",
        "data": "factur no f-2021 - 0002 Monsieur jean dupont 223 av general leclerc 54000 france siret 84549341300187 date document exigibilité paiement 18/06/2021 désianation description ref tvb ther vert biologique mt miel thym délai 30 jour pénalité retard fois taux légal 40 escompte aucun commercy bazar zone commercialf canaire rue fuville 55200 52341768100013 19/05/2021 quantité prix ht 12,00 20,00 total remise général final tver ttc montant 36,00 40,00 76.00 5,00 71,00 0,00 indemnité forfaitaire frais recouvrement non applicable art 293 cgi abby 1/1"
    }
]
headers = {'Content-Type': 'application/json'}
response = requests.post(
    url=endpoint_url,
    json=data_dict,
    headers=headers
)

print(response.json())