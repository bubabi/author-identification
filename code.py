import operator
import os
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


for filename in os.listdir( path ):
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

# for essay in data['train']['h']:
#     print("# of essay", len(data['train']['h']), end=", ")
#     print("# of sentences in essay:", len(essay))

bow = {}


def ngrams(bow, text, n):
    text = text.split()
    text.insert(0, "<s>")
    text.append("</s>")

    for i in range( len( text ) - n + 1 ):
        gram = ' '.join( text[i:i + n] )
        if bow.__contains__(gram):
            bow[gram] += 1
        else:
            bow[gram] = 1


for essay in data['train']['h']:
    for sentence in essay:
        ngrams(bow, sentence, 3)

bow = sorted(bow.items(), key=operator.itemgetter(1), reverse=True)

print(bow)
