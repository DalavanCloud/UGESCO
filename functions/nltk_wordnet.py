from nltk.corpus import wordnet as wn

print(sorted(wn.langs()))

print(wn.synsets(u'vache', lang='fra')) #dog.n.01


print(wn.synset('dog.n.01').lemma_names('fra'))

dog = wn.synset('dog.n.01')

carnivore = wn.synset('carnivore.n.01')

cat = wn.synset('cat.n.01')

salope = wn.synset('bitch.n.01')

vache = wn.synset('cow.n.01')

maison = wn.synset('house.n.07')

print(dog.path_similarity(carnivore))
print(dog.path_similarity(cat))
print(dog.path_similarity(vache))
print(dog.path_similarity(maison))