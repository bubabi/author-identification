import math
import os
import random
import re


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


def read_and_tokenize(path, num_list):

    essays = []

    for filename in os.listdir(path):
        num = int( filename[:-4] )

        if num in num_list:
            with open( path + "/" + filename, "r" ) as f:
                f.readline()

                text_block = f.readline().split( ": ", 1 )[1].lower() \
                    .replace( ",", " <comma> " ).replace( "(", "" ).replace( ")", "" ) \
                    .replace( "``", "" ).replace( ";", "" ).replace( "\n", "" ).replace( ":", "" ) \
                    .replace( ".", " <dot> . " ).replace( "?", " <q> ? " ).replace( "!", " <ex> ! " ).replace( "''", "" )

                sentences = re.split( r"(?<!^)\s*[.\n]+\s*(?!$)", text_block )
                essay = sentences[:-1]

            essays.append( essay )

    return essays

################################# TASK 1 #################################


def build_ngram_model(essays):

    models = list()
    for n in range(1, 4):
        bow = {}
        for essay in essays:
            for sentence in essay:
                sentence = sentence.split()
                if n == 3:
                    sentence.insert( 0, "<s>" )
                sentence.insert( 0, "<s>" )
                sentence.append( "</s>" )

                for i in range( len( sentence ) - n + 1 ):
                    gram = ' '.join( sentence[i:i + n] )
                    if bow.__contains__( gram ):
                        bow[gram] += 1
                    else:
                        bow[gram] = 1
        models.append(bow)

    return models[0], models[1], models[2]


def get_ngram_probs(sentence_count, unigram, bigram, trigram):
    models_probs = list()
    for n in range(1, 4):
        probs = {}
        if n == 1:
            target_items = unigram.items()
            V = len( unigram.keys() )
            N = sum( unigram.values() )
            for k, v in target_items:
                numerator = v + 1
                denominator = N + V
                prob = numerator / denominator
                probs[k] = prob
        elif n == 2:
            target_items = bigram.items()
            V = len( bigram.keys() )
            for k, v in target_items:
                numerator = v + 1
                denominator = unigram[k.split()[0]] + V
                prob = numerator / denominator
                probs[k] = prob
        else:
            target_items = trigram.items()
            V = len( trigram.keys() )
            for k, v in target_items:
                bigram_key = k.split()[0] + " " + k.split()[1]
                numerator = v + 1
                if bigram_key == "<s> <s>":
                    denominator = sentence_count
                else:
                    denominator = bigram[bigram_key] + V
                prob = numerator / denominator
                probs[k] = prob

        models_probs.append( probs )

    return models_probs[0], models_probs[1], models_probs[2]


################################# TASK 2 #################################


def generate_unigram_sentence(word, ngram, probs, n=30):

    def weighted_random_choice(words):
        total = sum( probs[w] for w in words )
        r = random.uniform( 0, total )
        border = 0

        for w in choices:
            word_prob = probs[w]
            if border + word_prob > r:
                #print( w, word_prob)
                return w, word_prob
            border += word_prob

    generated_sentence = ""
    sentence_prob = 0
    choices = ngram.keys()
    for i in range(n):
        generated_sentence += word + " "
        word, prob = weighted_random_choice(choices)

        sentence_prob += math.log10( prob )

    #print(sentence_prob)
    return generated_sentence


def generate_bigram_sentence(word, ngram, probs, n=30):

    def weighted_random_choice(choices):
        total = sum( probs[w] for w in choices )
        r = random.uniform( 0, total )
        border = 0

        for pair in choices:
            pair_prob = probs[pair]
            if border + pair_prob > r:
                #print( pair, pair_prob)
                return pair, pair_prob
            border += pair_prob

    generated_sentence = ""
    sentence_prob = 0
    for i in range(n):
        generated_sentence += word + " "
        choices = list()
        for pair in ngram:
            if pair.split()[0] == word:
                choices.append(pair)
        if not choices: break
        word, prob = weighted_random_choice(choices)
        word = word.split()[1]

        sentence_prob += math.log10( prob )

    #print(sentence_prob)
    return generated_sentence


def generate_trigram_sentence(word, ngram, probs, n=30):

    def weighted_random_choice(choices):
        total = sum( probs[w] for w in choices )
        r = random.uniform( 0, total )
        border = 0

        for pair in choices:
            pair_prob = probs[pair]
            if border + pair_prob > r:
                #print(pair, pair_prob)
                return pair, pair_prob
            border += pair_prob

    generated_sentence = ""
    sentence_prob = 0
    for i in range(n):
        generated_sentence += word.split()[1] + " "
        choices = list()
        for pair in ngram:
            key = pair.split()[0] + " " + pair.split()[1]
            if key == word:
                choices.append(pair)
        if not choices: break
        tri_word, prob = weighted_random_choice(choices)
        tri_word = tri_word.split()

        sentence_prob += math.log10(prob)

        word = tri_word[1] + " " + tri_word[2]

    #print(sentence_prob)
    return generated_sentence


#################### H ####################

data['train']['h'] = read_and_tokenize("./data", train_nums['h'])
unigram_h, bigram_h, trigram_h = build_ngram_model(data['train']['h'])

h_sentence_count = 0
for essay in data['train']['h']: h_sentence_count += len(essay)

unigram_h_probs, bigram_h_probs, trigram_h_probs = get_ngram_probs(h_sentence_count, unigram_h, bigram_h, trigram_h)

print("UNIGRAM: \n", generate_unigram_sentence('', unigram_h, unigram_h_probs))
print("BIGRAM: \n", generate_bigram_sentence('<s>', bigram_h, bigram_h_probs))
print("TRIGRAM: \n", generate_trigram_sentence('<s> <s>', trigram_h, trigram_h_probs))

#################### M ####################

data['train']['m'] = read_and_tokenize("./data", train_nums['m'])
unigram_m, bigram_m, trigram_m = build_ngram_model(data['train']['m'])

m_sentence_count = 0
for essay in data['train']['m']: m_sentence_count += len(essay)

unigram_m_probs, bigram_m_probs, trigram_m_probs = get_ngram_probs(m_sentence_count, unigram_m, bigram_m, trigram_m)

print("\nUNIGRAM: \n", generate_unigram_sentence('', unigram_h, unigram_h_probs))
print("BIGRAM: \n", generate_bigram_sentence('<s>', bigram_h, bigram_h_probs))
print("TRIGRAM: \n", generate_trigram_sentence('<s> <s>', trigram_h, trigram_h_probs))
