import numpy as np

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from langdetect import detect
import nltk
nltk.download('wordnet')
import spacy
from custom_logger import logger

set_stop_words_french = set(stopwords.words('french'))
set_stop_words_english = set(stopwords.words('english'))
def _stop_words_filtering(liste_mots, set_stop_words) :
    tokens = [mot for mot in liste_mots if mot not in set_stop_words]
    return tokens

#------------------------------------------------------------------------
nlp_fr = spacy.load('fr_core_news_sm')
nlp_en = spacy.load('en_core_web_sm')


def _tokenisation_et_lemmatisation(mots, nlp_for_language) :
    """
    Perform tokenization and lemmatization on a given string of text, removing stop words and 
    preserving specific words based on custom rules (like words starting with 'zz').

    Args:
        mots (str): The input string of words to be tokenized and lemmatized.
        nlp_for_language (spacy.Language): The SpaCy language model used for tokenization and lemmatization.

    Returns:
        List[str]: A list of lemmatized words, excluding stop words and ensuring certain words are repeated as needed.
    """

    sortie = []
    #print("liste de mots", mots)
    phrase_nlp = nlp_for_language(mots)
    for mot in phrase_nlp :
        #print('______________')
        #print("mot:", mot)
        #print(" ", mot.text, mot.lemma_, mot.pos_, mot.tag_, mot.dep_,mot.shape_, mot.is_alpha, mot.is_stop)
        if mot.lemma_.startswith('zz') : # pour garder la répétition des mots
            sortie.append(mot.lemma_)
        else:
            if (mot.is_stop == False ) : # pour ne pas prendre les stop-words  
                # and (mot.pos_ != 'PROPN') # n'a pas donné de bons résultats
                lemma = mot.lemma_ # on ne rajoute que les lemmes
                #print("   lemma:", lemma)
                if (lemma not in sortie) : sortie.append(lemma)
    return sortie

#------------------------------------------------------------------------
def token_lemmatization_and_remove_stop_words(text: str) -> str:
    """
    Perform tokenization, lemmatization, and stop word removal on the input text.
    Depending on the detected language (English or French), it applies language-specific 
    preprocessing. If the language is neither English nor French, it removes stop words for both.

    Args:
        text (str): The input text string to transform.

    Returns:
        Optional[str]: The text after stop words are removed and tokens are lemmatized.
        Returns None if the text could not be processed.
    """
    token_word_tokenize = lambda row: word_tokenize(row)
    token_remove_stop_words_en = lambda row: _stop_words_filtering(row, set_stop_words_english)
    token_remove_stop_words_fr = lambda row: _stop_words_filtering(row, set_stop_words_french)

    token_spacy_en = lambda row: _tokenisation_et_lemmatisation(row, nlp_en)
    token_spacy_fr = lambda row: _tokenisation_et_lemmatisation(row, nlp_fr)
    token_rebuild_text = lambda row: ' '.join(row)

    def _text_remove_stop_words(row):
        if detect(row) == 'en':
            return token_rebuild_text(token_spacy_en(row))
        elif detect(row) == 'fr':
            return token_rebuild_text(token_spacy_fr(row))
        else:
            return token_rebuild_text(token_remove_stop_words_fr(token_remove_stop_words_en(token_word_tokenize(row))))
    
    return _text_remove_stop_words(text)
    

#------------------------------------------------------------------------
def clean_transform_ocerised_text(text: str) -> str:
    """
    Clean and transform the input text by applying various preprocessing steps such as:
    - Lowercasing the text.
    - Tokenizing the text into words.
    - Removing short words and strings with insufficient content.

    Args:
        text (str): The text string to clean and transform.

    Returns:
        Optional[str]: The cleaned and transformed text. Returns None if the resulting text has fewer than 5 characters.
    """

    # transform the string in lower cases
    x = (lambda row: str(row).lower()) (text)

    # split as tokens
    x = (lambda row: word_tokenize(row)) (x)

    # remove word when too small
    minletters = 2
    x = (lambda row: [word for word in row if len(word) >= minletters])  (x)

    # remove word when too few
    minwords = 2
    x = (lambda row: row if len(row) > minwords else [])  (x)

    # collapse the token back in one string
    x = (lambda row: ' '.join(row))  (x)
    
    # remove if final string less than 5 characters
    x = (lambda text: np.nan if (len(text) < 5) else text) (x)
    fct_clean = x

    return fct_clean 

def tokenize_data(data: str) -> str:
    STAGE_NAME = "Stage: clean_text"    
    try:        
        #logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        cleaned_data = clean_transform_ocerised_text(data)
        tokenized_data = token_lemmatization_and_remove_stop_words(cleaned_data)
        #logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
        return tokenized_data
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

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

if __name__ == "__main__":
    tokenize_data(txt_test) 