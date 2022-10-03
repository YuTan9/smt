import json
import re
from tqdm import tqdm
import random

FORCE_EMPTY_FREQ = 0.05
TRANSLATE_BASED_ON_ZH = 0.01

def get_initial_translation(sentence):
    res = []
    previous = ""
    freq = 0
    for i, word in enumerate(sentence.split()):
        if(' ' in previous):
            previous = previous.split()[-1]
        if(word not in distribution):
            print("Don't know the word '{}'".format(word))
            continue
        if(previous in ["", '(', ')', '?', '.'] or word in ['(', ')', '?', '.']):
            previous = max(distribution[word], key=distribution[word].get)
            res.append(previous)
        else:
            max_freq = -1
            best_candidate = ''
            # should_pop = False
            for key in distribution[word]:
                if(key == '' and random.random() < FORCE_EMPTY_FREQ):
                    # print(f'Forced {word} translate to NULL')
                    best_candidate = ''
                    max_freq = 0
                    break
                if(random.random() < TRANSLATE_BASED_ON_ZH):
                    r = re.compile(".* {} .*".format(previous))
                    tmp = list(filter(r.match, tgt_usage))
                    if(tmp != []):
                        followed_by = {}
                        for line in tmp:
                            try:
                                next_zh_word = line.split(previous)[1].split(' ')[0]
                            except:
                                continue
                            if(next_zh_word == ''):
                                continue
                            if(next_zh_word not in followed_by):
                                followed_by[next_zh_word] = 1
                            else:
                                followed_by[next_zh_word] += 1
                        if(followed_by != {}):
                            max_freq = max(distribution[word].values())
                            best_candidate = max(followed_by, key=followed_by.get)
                            # print(f'{previous}Forced {word} translate to {best_candidate}')
                            break
                r = re.compile(".*{} {}.*".format(previous, key))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp + distribution[word][key]
                    best_candidate = key
            if(max_freq == -1):
                previous = max(distribution[word], key=distribution[word].get)
                freq += distribution[word][previous]
                res.append(previous)
            else:
                freq += max_freq
                previous = best_candidate
                res.append(previous)
    return res, freq

def lookahead(sentence, initial_translation):
    if(len(initial_translation) != len(sentence.split())):
        print('######size mismatch######')
        print(len(initial_translation))
        print(sentence.split())
    res = []
    freq = 0
    for idx, word in enumerate(sentence.split()):
        counter = 1
        while(initial_translation[min(idx+counter, len(initial_translation)-1)] == ''):
            counter += 1
            if(idx + counter == len(initial_translation)):
                break
        next_translation = initial_translation[min(idx+counter, len(initial_translation)-1)]
        if(' ' in next_translation):
            next_translation = next_translation.split()[-1]
        if(word not in distribution):
            print("Don't know the word '{}'".format(word))
            continue
        if(word in ['(', ')', '?', '.'] or next_translation in ['(', ')', '?', '.']):
            res.append(max(distribution[word], key=distribution[word].get))
        else:
            max_freq = -1
            best_candidate = ''
            for key in distribution[word]:
                if(key == '' and random.random() < FORCE_EMPTY_FREQ):
                    # print(f'Forced {word} translate to NULL')
                    best_candidate = ''
                    max_freq = 0
                    break
                if(random.random() < TRANSLATE_BASED_ON_ZH):
                    r = re.compile(".* {} .*".format(next_translation))
                    tmp = list(filter(r.match, tgt_usage))
                    if(tmp != []):
                        prior_to = {}
                        for line in tmp:
                            try:
                                previous_zh_word = line.split(next_translation)[0].split(' ')[-1]
                            except:
                                continue
                            if(previous_zh_word == ''):
                                continue
                            if(previous_zh_word not in prior_to):
                                prior_to[previous_zh_word] = 1
                            else:
                                prior_to[previous_zh_word] += 1
                        if(prior_to != {}):
                            # print(next_translation)
                            # print(prior_to)
                            max_freq = max(distribution[word].values())
                            best_candidate = max(prior_to, key=prior_to.get)
                            # print(f'{next_translation}Forced {word} translate to {best_candidate}')
                            break
                r = re.compile(".*{} {}.*".format(key, next_translation))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp + distribution[word][key]
                    best_candidate = key
            if(max_freq == -1):
                res.append(max(distribution[word], key=distribution[word].get))
            else:
                freq += max_freq
                res.append(best_candidate)
    return res, freq


def reorder(sentence, initial_translation):
    if(len(initial_translation) != len(sentence.split())):
        print('######size mismatch######')
        print(len(initial_translation))
        print(sentence.split())
    sentence = sentence.split()
    freq = 0
    for i in range(len(sentence) - 1):
        if(initial_translation[i] in ['(', ')', '?', ',', '。', ';', '、'] or\
            initial_translation[i+1] in ['(', ')', '?', ',', '。', ';', '、']):
            continue
        r = re.compile(".*{} {}.*".format(initial_translation[i], initial_translation[i+1]))
        noswap = len(list(filter(r.match, tgt_usage)))
        r = re.compile(".*{} {}.*".format(initial_translation[i+1], initial_translation[i]))
        swap = len(list(filter(r.match, tgt_usage)))
        if(swap > noswap):
            tmp = initial_translation[i+1]
            initial_translation[i+1] = initial_translation[i]
            initial_translation[i] = tmp
            tmp = sentence[i+1]
            sentence[i+1] = sentence[i]
            sentence[i] = tmp
            freq += swap
        else:
            freq += noswap
    return ' '.join(sentence), initial_translation, freq


def recover_zh_sentence(arr, space):
    if(space):
        return ' '.join(' '.join(arr).strip().split())
    else:
        return ''.join(' '.join(arr).strip().split())


with open('stat.json', 'r') as f:
    distribution = json.load(f)

with open('tw.en.txt', 'r') as f:
    src = f.readlines()

with open('tw.zh.txt', 'r') as f:
    ans = f.readlines()

with open('as_testing_gold.utf8', 'r') as f:
    tgt_usage = f.readlines()

for idx, sentence in enumerate(src):
    # print("Translating the following sentence:")
    # print(sentence)
    # print()
    previous, score = get_initial_translation(sentence)
    # print('Initialiazation:')
    # print(recover_zh_sentence(previous, True))
    # print("Optimizing...")
    res = {recover_zh_sentence(previous, False): 0}
    # for _ in tqdm(range(50)):
    for _ in range(50):
        previous, score = lookahead(sentence, previous)
        sentence, previous, ordering_score = reorder(sentence, previous)
        if(recover_zh_sentence(previous, False) in res):
            break
        res[recover_zh_sentence(previous, False)] = score + ordering_score
    # print('Result:')
    print(max(res, key=res.get))
    # print()
    # print("Correct sentence:")
    print(recover_zh_sentence(ans[idx], False))
    # print("-"* 40)
    # print()
    # input()
    


