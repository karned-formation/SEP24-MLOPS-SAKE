from src.data.clean_text import tokenize_data

txt_test = """
FACTURE

 

 

 

Joanna Binet
48 Coubertin
31400 Paris
FACTURE A ENVOVE A FACTURE N° FR.001
Cendrilon Ayot Cendrilon Ayot DATE 2901/2019
69 rue Nations 46 Rue St Fertéol .
22000 Paris 92360 Ile-de-France COMMANDE N ‘esoa0t9
ECHEANCE 24/08/2019
ae DESIGNATION PRIX UNIT. HT MONTANT HT
1 Grand brun escargot pour manger 4100.00 100.00
2 Petit mariniére uniforme en bleu 15.00 30.00
3 Facile a jouer accordéon 5.00 15.00
Total HT 145.00
VA 20.0% 29.00
TOTAL 174.006

CONDITIONS ET MODALITES DE PAIEMENT

Le paiement est d0 dans 15 jours

Caisse d'Epargne
IBAN: FR12 1234 5678
‘SWIFTIBIC: ABCDFRP1XXX
Joanna Binet

48 Coubertin
31400 Paris
Facturé a Envoyé a
Cendrilon Ayot Cendritlon Ayot
69 rue Nations 46 Rue St Ferréol
22000 Paris 92360 lle-de-France
are DESIGNATION

1. Grand brun escargot pour manger

2 Petit mariniére uniforme en bleu

3 Facile & jouer accordéon

Conditions et modalités de paiement
Le paiement est dd dans 15 jours

Caisse d'Epargne
IBAN: FR12 1234 5678
SWIFT/BIC: ABCDFRP1XxX
"""


result_test = "factur joanna binet 48 coubertin 31400 pari envov numéro fr.001 cendrilon ayot date 2901/2019 69 rue natier 46 st fertéol 22000 92360 ile-de-france command esoa0t9 echeance 24/08/2019 ae designation prix unir ht montant grand brun escargot manger 4100.00 100.00 petit mariniére uniforme bleu 15.00 30.00 facile jouer accordéon 5.00 total 145.00 20.0 29.00 174.006 condition modalite paiement d0 15 jour caisse epargne iban fr12 1234 5678 swiftibic abcdfrp1xx facturer envoyer cendritlon ferréol lle-de-france are 1 . modalité dd swift / bic abcdfrp1xxx"

clean_url = "http://localhost:8903/clean" # url de l'OCR

def main():
    assert tokenize_data(txt_test) == result_test

    

