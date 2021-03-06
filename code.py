import math, os, random, re

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

unknown_nums = [49, 50, 51, 52, 53, 54, 55, 56, 57, 62, 63]


def read_and_tokenize(path, num_list):

    essays = []

    for filename in os.listdir(path):
        num = int( filename[:-4] )

        if num in num_list:
            with open( path + "/" + filename, "r" ) as f:
                f.readline()

                text_block = f.readline().split( ": ", 1 )[1].lower() \
                    .replace( ",", "" ).replace( "(", "" ).replace( ")", "" ) \
                    .replace( "``", "" ).replace( ";", "" ).replace( "\n", "" ).replace( ":", "" ) \
                    .replace( ".", " <dot> . " ).replace( "?", " <q> " ).replace( "!", " <ex> " ).replace( "''", "" )

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
                denominator = unigram.get(k.split()[0], 0) + V
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
                    denominator = bigram.get(bigram_key, 0) + V
                prob = numerator / denominator
                probs[k] = prob

        models_probs.append( probs )

    return models_probs[0], models_probs[1], models_probs[2]


################################# TASK 2 #################################

def weighted_random_choice(words, probs):

    total = sum( probs[w] for w in words )
    r = random.uniform( 0, total )
    border = 0

    for w in words:
        word_prob = probs[w]
        if border + word_prob > r:
            if w not in ["<s>", "</s>", "<dot>"]:
                return w, word_prob
        border += word_prob


def generate_unigram_sentence(word, ngram, probs, n=30):

    generated_sentence = ""
    sentence_prob = 0
    choices = ngram.keys()
    for i in range(n):
        generated_sentence += word + " "
        word, prob = weighted_random_choice(choices, probs)

        sentence_prob += math.log10( prob )

    return generated_sentence


def generate_bigram_sentence(word, ngram, probs, n=30):

    generated_sentence = ""
    sentence_prob = 0
    for i in range(n):
        generated_sentence += word + " "
        choices = list()
        for pair in ngram:
            if pair.split()[0] == word:
                choices.append(pair)
        if not choices: break
        word, prob = weighted_random_choice(choices, probs)
        word = word.split()[1]

        sentence_prob += math.log10( prob )

    return generated_sentence


def generate_trigram_sentence(word, ngram, probs, n=30):
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
        tri_word, prob = weighted_random_choice(choices, probs)
        tri_word = tri_word.split()

        sentence_prob += math.log10(prob)

        word = tri_word[1] + " " + tri_word[2]

    return generated_sentence


def task1_and_task2_handler(author):

    data['train'][author] = read_and_tokenize("./data", train_nums[author])
    unigram, bigram, trigram = build_ngram_model(data['train'][author])

    sentence_count = 0
    for essay in data['train'][author]: sentence_count += len(essay)

    unigram_probs, bigram_probs, trigram_probs = get_ngram_probs(sentence_count, unigram, bigram, trigram)


    # print("UNIGRAM: \n", generate_unigram_sentence('', unigram, unigram_probs))
    # print("BIGRAM: \n", generate_bigram_sentence('<s>', bigram, bigram_probs))
    # print("TRIGRAM: \n", generate_trigram_sentence('<s> <s>', trigram, trigram_probs))

    return unigram, bigram, trigram, sentence_count, bigram_probs, trigram_probs


################################ TASK 3 ##################################


def get_essay_perplexity(n, count, author, unigram, bigram, trigram, essays):

    if n == 3: V = len( trigram.keys() )
    else: V = len( bigram.keys() )
    perps = list()

    for essay in essays:
        pair_count = 0
        essay_perplexity = 0
        essay_prob = 0
        for sentence in essay:
            sentence = sentence.split()
            if (len( sentence ) - n + 1 ) == 0: continue
            sentence_prob = 0
            for i in range( len( sentence ) - n + 1 ):
                pair_count += 1
                gram = ' '.join(sentence[i:i + n])
                if n == 3:
                    key = gram.split()[0] + " " + gram.split()[1]
                    numerator = trigram.get( gram, 0 ) + 1
                    if key == "<s> <s>":
                        denominator = count + V
                    else:
                        denominator = bigram.get( key, 0 ) + V
                else:
                    key = gram.split()[0]
                    numerator = bigram.get( gram, 0 ) + 1
                    denominator = unigram.get( key, 0 ) + V
                prob = numerator / denominator
                sentence_prob += math.log2(prob)
            essay_prob += sentence_prob
            essay_perplexity = math.pow(2, essay_prob*(-1/pair_count))

        print("Author:", author, "Perplexity:", essay_perplexity)
        perps.append(essay_perplexity)

    return perps


def test_and_classify_essays(nums):

    for num in nums:
        for i in range( 2, 4 ):
            print("n-gram:", i)
            h_perp = 0
            m_perp = 0
            for author in ['h', 'm']:
                unigram, bigram, trigram, count, \
                bigram_prob, trigram_prob = task1_and_task2_handler(author)

                essays = read_and_tokenize("./data", [num])
                perps = get_essay_perplexity( i, count, author, unigram, bigram, trigram, essays )
                if author == 'h': h_perp = perps[0]
                else: m_perp = perps[0]
            #print("h:", h_perp, "m", m_perp)
            if h_perp <= m_perp: print(str(num) + ".txt", "HAMILTON")
            else: print(str(num) + ".txt", "MADISON")


##########################################################################


# task1_and_task2_handler('h')

# task1_and_task2_handler('m')

# test_and_classify_essays(unknown_nums)

test_and_classify_essays(test_nums['h'] + test_nums['m'])
