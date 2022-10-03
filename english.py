import jieba
# import nltk
# nltk.download('wordnet')
# nltk.download('omw-1.4')
# nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm

zh = []
en = []
zh_tokens = []
en_tokens = []
raw = ''
with open('tw.txt', 'r') as f:
    raw = f.readlines()

for idx, sentence in enumerate(raw):
    if(idx % 2 == 0):
        en.append(sentence.strip())
    else:
        zh.append(sentence.strip())

for sentence in tqdm(en):
    tmp = [WordNetLemmatizer().lemmatize(word,'v') for word in word_tokenize(sentence)]
    en_tokens += [WordNetLemmatizer().lemmatize(word,'n').lower() for word in tmp]
with open('tw.en.txt', 'w') as f:
    for word in set(en_tokens):
        f.write("\t\"")
        f.write(word)
        f.write("\": {\"\": },\n")

