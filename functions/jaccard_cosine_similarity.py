import re
import math
from collections import Counter
import numpy as np

text1 = 'Nicole a mangé du singe'
text2 = 'Nicole a mangé du rat'


class Similarity():
    def compute_cosine_similarity(self, string1, string2):
        # intersects the words that are common
        # in the set of the two words
        intersection = set(string1.keys()) & set(string2.keys())
        # dot matrix of vec1 and vec2
        numerator = sum([string1[x] * string2[x] for x in intersection])

        # sum of the squares of each vector
        # sum1 is the sum of text1 and same for sum2 for text2
        sum1 = sum([string1[x]**2 for x in string1.keys()])
        sum2 = sum([string2[x]**2 for x in string2.keys()])

        # product of the square root of both sum(s)
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return round(numerator / float(denominator), 4)

    def text_to_vector(self, text):
        WORD = re.compile(r'\w+')
        words = WORD.findall(text)
        return Counter(words)

    # Jaccard Similarity
    def tokenize(self, string):
        return string.lower().split(" ")

    def jaccard_similarity(self, string1, string2):
        intersection = set(string1).intersection(set(string2))
        union = set(string1).union(set(string2))
        return len(intersection) / float(len(union))


similarity = Similarity()

# vector space
vector1 = similarity.text_to_vector(text1)
vector2 = similarity.text_to_vector(text2)

# split words into tokens
token1 = similarity.tokenize(text1)
token2 = similarity.tokenize(text2)

cosine = similarity.compute_cosine_similarity(vector1, vector2)
print('Cosine Similarity:', cosine)

jaccard = similarity.jaccard_similarity(token1, token2)
print('Jaccard Similarity:', jaccard)
