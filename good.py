import json
import re
from tqdm import tqdm
def get_initial_translation(sentence):
    res = []
    previous = ""
    for word in sentence.split():
        if(' ' in previous):
            previous = previous.split()[-1]
        if(word not in distribution):
            print("Don't know the word '{}'".format(word))
            continue
        if(previous in ["", '(', ')', '?'] or word in ['(', ')', '?']):
            previous = max(distribution[word], key=distribution[word].get)
            res.append(previous)
        else:
            max_freq = -1
            best_candidate = ''
            # should_pop = False
            for key in distribution[word]:
                r = re.compile(".*{} {}.*".format(previous, key))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp
                    best_candidate = key
                #     should_pop = False
                # r = re.compile(".*{} {}.*".format(key, previous))
                # tmp = len(list(filter(r.match, tgt_usage)))
                # if(tmp > max_freq):
                #     max_freq = tmp
                #     best_candidate = key
                #     should_pop = True
            if(max_freq == -1):
                previous = max(distribution[word], key=distribution[word].get)
                res.append(previous)
                continue
            # if(should_pop):
            #     tmp = res.pop(-1)
            #     res.append(best_candidate)
            #     res.append(tmp)
            else:
                previous = best_candidate
                res.append(previous)
    return res
def lookahead(sentence, initial_translation):
    if(len(initial_translation) != len(sentence.split())):
        print('######size mismatch######')
        print(len(initial_translation))
        print(sentence.split())
    res = []
    previous = ""
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
        if(word in ['(', ')', '?'] or next_translation in ['(', ')', '?']):
            res.append(max(distribution[word], key=distribution[word].get))
        else:
            max_freq = -1
            best_candidate = ''
            for key in distribution[word]:
                r = re.compile(".*{} {}.*".format(key, next_translation))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp
                    best_candidate = key
            if(max_freq == -1):
                res.append(max(distribution[word], key=distribution[word].get))
            else:
                res.append(best_candidate)
    return res


def optimzie_according_to_initial_translation(sentence, initial_translation):
    if(len(initial_translation) != len(sentence.split())):
        print('######size mismatch######')
        print(len(initial_translation))
        print(sentence.split())
    res = []
    previous = ""
    for idx, word in enumerate(sentence.split()):
        counter = 1
        while(initial_translation[min(idx+counter, len(initial_translation)-1)] == ''):
            counter += 1
            if(idx + counter == len(initial_translation)):
                break
        next_translation = initial_translation[min(idx+counter, len(initial_translation)-1)]
        if(' ' in previous):
            previous = previous.split()[-1]
        if(' ' in next_translation):
            next_translation = next_translation.split()[-1]
        if(word not in distribution):
            print("Don't know the word '{}'".format(word))
            continue
        if(previous in ["", '(', ')', '?'] or word in ['(', ')', '?']\
            or next_translation in ['(', ')', '?']):
            previous = max(distribution[word], key=distribution[word].get)
            res.append(previous)
        else:
            max_freq = -1
            best_candidate = ''
            should_pop = False
            for key in distribution[word]:
                r = re.compile(".*{} {} {}.*".format(previous, key, next_translation))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp
                    best_candidate = key
                    should_pop = False
                r = re.compile(".*{} {}.*".format(key, previous, next_translation))
                tmp = len(list(filter(r.match, tgt_usage)))
                if(tmp > max_freq):
                    max_freq = tmp
                    best_candidate = key
                    should_pop = True
            if(max_freq == -1):
                previous = max(distribution[word], key=distribution[word].get)
                res.append(previous)
                continue
            if(should_pop):
                tmp = res.pop(-1)
                res.append(best_candidate)
                res.append(tmp)
            else:
                previous = best_candidate
                res.append(previous)
    return res

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
    print("Translating the following sentence:")
    print(sentence)
    print()
    previous = get_initial_translation(sentence)
    print('Initialiazation:')
    print(recover_zh_sentence(previous, True))
    print("Optimizing...")
    res = [recover_zh_sentence(previous, False)]
    for _ in tqdm(range(50)):
        previous = lookahead(sentence, previous)
        if(recover_zh_sentence(previous, False) in res):
            break
        res.append(recover_zh_sentence(previous, False))
    print('Result:')
    print(recover_zh_sentence(res[-1], False))
    print()
    print("Correct sentence:")
    print(ans[idx])
    print("-"* 40)
    print()
    input()
    


