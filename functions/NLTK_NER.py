# -*- coding: utf-8 -*-
""" 
Test du Stanford NER tagger avec les modèles CRF d'Europeana
entrainés sur des journaux :
http://lab.kbresearch.nl/static/html/eunews.html
La fonction est lente --> songer au multiprocessing
"""

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings("ignore")

MODEL = r'D:\stanford-ner-2017-06-09\classifiers\eunews.fr.crf.gz'
STANFORD_JAR = r'D:\stanford-ner-2017-06-09\stanford-ner.jar'


def classify(text):
    """
    Test du Stanford NER tagger avec NLTK et les modèles CRF d'Europeana
    entrainés sur des journaux :
    http://lab.kbresearch.nl/static/html/eunews.html
    Récrire cette partie en utilisant pathlib pour éviter les chemins absolus
    """
    st = StanfordNERTagger(MODEL,
                           STANFORD_JAR,
                           encoding='utf-8')

    tokenized_text = word_tokenize(text)
    ner_output = st.tag(tokenized_text)

    return ner_output


def rechunk(ner_output):
    """regroupe les entités par type si elles sont consécutives.
    [('Jean', 'I-PERS'), ('Duvieusart', 'I-PERS')] devient ainsi
    [('Jean Duvieusart', 'I-PERS')]"""
    chunked, pos, prev_tag = [], "", None
    for i, word_pos in enumerate(ner_output):
        word, pos = word_pos
        if pos in ['I-PERS', 'I-LIEU', 'I-ORG'] and pos == prev_tag:
            chunked[-1] += word_pos
        else:
            chunked.append(word_pos)
        prev_tag = pos

    clean_chunked = [tuple([" ".join(wordpos[::2]), wordpos[-1]])
                     if len(wordpos) != 2 else wordpos for wordpos in chunked]

    return clean_chunked


def get_ner_lieux(clean_chunks):
    """récupération des lieux dans la liste de tuples"""
    list_loc = []
    for i, j in clean_chunks:
        if j == "I-LIEU":
            list_loc.append(i)
    list_loc = list(set(list_loc))
    return list_loc


def get_ner(text):
    """Récupération des lieux à l'aide de stanford NER"""
    ner_output = classify(text)
    clean_chunks = rechunk(ner_output)
    lieux = get_ner_lieux(clean_chunks)

    return lieux


if __name__ == '__main__':

    text = """Char américain dans la rue de France, le 3 septembre 1944 (Philippeville)."""

    print(get_ner(text))
