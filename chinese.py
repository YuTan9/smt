import jieba
# import nltk
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

with open('tw.zh.txt', 'w') as f:
    for sentence in tqdm(zh):
        f.write(' '.join(jieba.cut(sentence)))
        zh_tokens += jieba.lcut(sentence)
        f.write('\n')

# with open('token.zh.txt', 'w') as f:
#     f.write('\n'.join(set(zh_tokens)))
to_write = ""
for sentence in tqdm(en):
    tmp = [WordNetLemmatizer().lemmatize(word,'v') for word in word_tokenize(sentence)]
    tmp = [WordNetLemmatizer().lemmatize(word,'n').lower() for word in tmp]
    en_tokens += tmp
    to_write += " ".join(tmp)
    to_write += "\n"

with open('tw.en.txt', 'w') as f:
    f.write(to_write)


with open('token.en.txt', 'w') as f:
    f.write('\n'.join(set(en_tokens)))

# with open('data.tokenized.txt', 'w') as f:
#     for idx, sentence in enumerate(raw):
#         if(idx % 2 == 0):
#             f.write(' '.join(word_tokenize(sentence)))
#         else:
#             f.write(' '.join(jieba.cut(sentence)))
#         f.write('\n')
