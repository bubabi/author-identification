import os
import random
import re

path = "./data"

train_nums = {
    'h': [1, 6, 7, 8, 13, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    'm': [10, 14, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]}
test_nums = {
    'h': [9, 11, 12],
    'm': [47, 48, 58]}

data = {
    'train': {'h': [],
              'm': []},
    'test': {'h': [],
             'm': []}
}


for filename in os.listdir(path):
    num = int( filename[:-4] )
    with open( path + "/" + filename, "r" ) as f:
        f.readline()

        text_block = f.readline().split(": ", 1)[1].lower() \
            .replace(",", "").replace("(", "").replace(")", "") \
            .replace("``", "").replace(";", "").replace("\n", "")

        sentences = re.split(r"(?<!^)\s*[.\n]+\s*(?!$)", text_block)
        essay = sentences[:-1]

        if num in train_nums['h']:
            data['train']['h'].append( essay )
        elif num in train_nums['m']:
            data['train']['m'].append( essay )
        elif num in test_nums['h']:
            data['test']['h'].append( essay )
        else:
            data['test']['m'].append( essay )

################################# TASK 1 #################################

def build_ngram_model(essays, n):

    bow = {}
    for essay in essays:
        for sentence in essay:
            sentence = sentence.split()
            sentence.insert(0, "<s>")
            sentence.append("</s>")

            for i in range(len(sentence) - n + 1):
                gram = ' '.join(sentence[i:i + n])
                if bow.__contains__(gram):
                    bow[gram] += 1
                else:
                    bow[gram] = 1
    return bow


unigram = build_ngram_model(data['train']['h'], 1)
bigram = build_ngram_model(data['train']['h'], 2)
trigram = build_ngram_model(data['train']['h'], 3)


def get_unigram_probs(unigram):

    _unigram_probs = {}
    V = len(unigram.keys())
    N = sum(unigram.values())
    for k, v in unigram.items():
        numerator = v + 1
        denominator = N + V
        prob = numerator/denominator
        _unigram_probs[k] = prob

    return _unigram_probs


def get_bigram_probs(unigram, bigram):

    _bigram_probs = {}
    V = len(bigram.keys())
    for k, v in bigram.items():
        numerator = v + 1
        denominator = unigram[k.split()[0]] + V
        prob = numerator/denominator
        _bigram_probs[k] = prob

    return _bigram_probs


def get_trigram_probs(bigram, trigram):

    _trigram_probs = {}
    V = len(bigram.keys())
    for k, v in trigram.items():
        bigram_key = k.split()[0] + " " + k.split()[1]
        numerator = v + 1
        denominator = bigram[bigram_key] + V
        prob = numerator/denominator
        _trigram_probs[k] = prob

    return _trigram_probs


unigram_probs = get_unigram_probs(unigram)
bigram_probs = get_bigram_probs(unigram, bigram)
trigram_probs = get_trigram_probs(bigram, trigram)

################################# TASK 2 #################################


def generate_bigram_sentence(word, n=30):

    def weighted_random_choice(choices):

        # total = sum( bigram[w] for w in choices )
        total = sum( bigram_probs[w] for w in choices )
        r = random.uniform( 0, total )
        border = 0

        for pair in choices:
            pair_prob = bigram_probs[pair]
            if border + pair_prob > r:
                print( pair )
                return pair
            border += pair_prob

    generated_sentence = ""
    for i in range(n):
        generated_sentence += word + " "
        choices = list()
        for pair in bigram:
            if pair.split()[0] == word:
                choices.append(pair)
        if not choices: break
        word = weighted_random_choice(choices).split()[1]

    return generated_sentence


def generate_trigram_sentence(word, n=30):

    def weighted_random_choice(choices):

        total = sum( trigram_probs[w] for w in choices )
        r = random.uniform( 0, total )
        border = 0

        for pair in choices:
            pair_prob = trigram_probs[pair]
            if border + pair_prob > r:
                print(pair)
                return pair
            border += pair_prob

    generated_sentence = ""
    for i in range(n):
        generated_sentence += word.split()[1] + " "
        choices = list()
        for pair in trigram:
            key = pair.split()[0] + " " + pair.split()[1]
            if key == word:
                choices.append(pair)
        if not choices: break
        tri_word = weighted_random_choice(choices).split()
        word = tri_word[1] + " " + tri_word[2]

    return generated_sentence


print(generate_trigram_sentence('<s> it'))
