# C:\Users\qwe\Documents\HSE\cosyco\udpipe\udpipe-1.2.0-bin\bin-win64\udpipe --output conllu --parse C:\Users\qwe\Documents\HSE\cosyco\udpipe\russian-syntagrus-ud-2.4-190531.udpipe < C:\Users\qwe\Documents\HSE\cosyco\norm_xix.conllu > C:\Users\qwe\Documents\HSE\cosyco\norm_xix_p.conllu

import os
import csv
import logging
from collections import defaultdict
from collections import Counter
from copy import deepcopy
import pandas as pd
from copy import copy


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
fh = logging.FileHandler("logs.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s - %(asctime)s')
fh.setFormatter(formatter)
LOGGER.addHandler(fh)


def extract_rel(path_from, path_to, rel, pos_or_rel):  # bigrams
    '''
    :path_from: путь к корпусу
    :path_to: путь к файлу, где будем хранить отношения
    :rel: тип отношения
    :pos_or_rel: rel если по типу отношения; pos если по типу вершины
    '''
    alpha = (3, 7)[pos_or_rel == 'rel']
    with open(path_from, 'r', encoding='utf-8') as f1:
        bigrams = Counter()
        unit = {}
        for line in f1.readlines():
            if line != '\n':
                line = line.split('\t')
                unit[int(line[0])] = line
            else:
                for t in unit:
                    if unit[t][alpha].lower() == rel and int(unit[t][6]) != 0:
                        try:
                            head_words = unit[int(unit[t][6])]
                            words = [head_words[1], head_words[2], head_words[3],
                                    rel, unit[t][1], unit[t][2], unit[t][3]]
                            bigrams['\t'.join([str(k) for k in words])] += 1
                        except:
                            print(unit)
                unit = {}
    all_b = sum([bigrams[i] for i in bigrams])
    with open(path_to, 'w', encoding='utf-8') as f2:
        writer = csv.writer(f2, delimiter='\t')
        for bigram in bigrams:
            line = bigram + '\t' + str((bigrams[bigram] / all_b) * 1000000) +\
                   '\t' + str(bigrams[bigram])
            writer.writerow(line.split('\t'))


def extract_rel2(path_from, path_to, rel): # trigrams with dependencies of VERB|NOUN|ADJ
    a = 0
    with open(path_from, 'r', encoding='utf-8') as f1:
        bigrams = Counter()
        unit = {}
        dep = defaultdict(list)
        for line in f1.readlines():
            a += 1
            if line != '\n' and line[0] != '#':
                line = line.split('\t')
                unit[int(line[0])] = line
                dep[int(line[6])].append(line)
            elif line == '\n':
                for t in unit:
                    if unit[t][3].lower() == rel:
                        for words in find_dep(unit, dep, t):
                            bigrams['\t'.join([str(k) for k in words])] += 1
                unit = {}
                dep = defaultdict(list)
        all_b = sum([bigrams[i] for i in bigrams])
        with open(path_to, 'w', encoding='utf-8') as f2:
            writer = csv.writer(f2, delimiter='\t')
            for br in bigrams:
                if bigrams[br] > 1:
                    line = br.split('\t')
                    line += [str((bigrams[br] / all_b) * 1000000), str(bigrams[br])]
                    writer.writerow(line)


def find_dep(unit, dep, t):
    result = []
    for _dep in dep[int(unit[t][0])]:
        head_words = unit[t]
        dep_words = _dep
        try:
            dep_dep = [item for item in dep[int(dep_words[0])] if item[7] ==
            'case'][0]
        except:
            dep_dep = None
        words = [head_words[1], head_words[2], head_words[3]]
        try:
            words += [dep_words[7], dep_words[1],
                      dep_words[2], dep_words[3]]
        except:
            continue
        try:
            words = words + [dep_dep[7], dep_dep[1], dep_dep[2], dep_dep[3]] \
                if dep else words + ['_'] * 4
        except:
            words += ['_'] * 4
            pass
        if 'punct' not in words:
            result.append(words)
    return result


def extract_rel3(path_from, path_to, rel): #conj
    with open(path_from, 'r', encoding='utf-8') as f1:
        trigrams = Counter()
        unit = {}
        dep = defaultdict(list)
        for line in f1.readlines():
            if line != '\n' and line[0] != '#':
                line = line.split('\t')
                unit[int(line[0])] = line
                dep[int(line[6])].append(line)
            else:
                for t in unit:
                    if unit[t][2].lower() in rel:
                        words = find_dep3(unit, dep, t)
                        trigrams['\t'.join(words)] += 1
                unit = {}
                dep = defaultdict(list)
        all_b = sum([trigrams[i] for i in trigrams])
        with open(path_to, 'w', encoding='utf-8') as f2:
            writer = csv.writer(f2, delimiter='\t')
            for br in trigrams:
                line = br.split('\t')
                line += [str((trigrams[br] / all_b) * 1000000), str(trigrams[br])]
                writer.writerow(line)


def find_dep3(unit, dep, t):
    try:
        head = unit[int(unit[t][6])]
    except:
        print(unit[t])
        return ['_'] * 11
    dep_w = unit[t]
    words = [head[1].lower(), head[2].lower(), head[3], dep_w[7],
             dep_w[1].lower(), dep_w[2].lower(), dep_w[3]]
    try:
        dep_dep = [item for item in dep[int(head[0])]]
        dep_dep = [item for item in dep_dep if item[7] != 'punct' and item[
            1].lower() != 'не']
        if len(dep_dep) > 0:
            dep_dep = dep_dep[0]
            words += [dep_dep[7], dep_dep[1].lower(), dep_dep[2].lower(),
                      dep_dep[3]]
        else:
            words += ["_"] * 4
    except Exception as e:
        words += ["_"] * 4
    return words


def intersect_lists(first_path, sec_path, path_to):
    with open(first_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        weights = {i[0].split('_')[0]: i[1] for i in reader}
    with open(sec_path, 'r', encoding='utf-8') as f2:
        reader2 = csv.reader(f2, delimiter='\t')
        trigrams = [i for i in reader2 if len(i) > 2]
    for t in range(len(trigrams)):
        if '_' in trigrams[t]:
            trigrams[t].remove('_')
    result = {}
    for i in trigrams:
        t = [i[0]+'_'+i[2], i[4]+'_'+i[6], i[8]+'_'+i[10]]\
            if len(i) == 13 else [i[0]+'_'+i[2], i[4]+'_'+i[6]]
        w = 0
        neg = 1 if len(t) > 5  and t[5] != 'не' else -1
        for word in t:
            try:
                w += float(weights[word.split('_')[0]])
            except KeyError:
                w = w
        result[' '.join(t)] = w * float(neg)
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    with open(path_to, 'w', encoding='utf-8', newline='') as f3:
        writer = csv.writer(f3, delimiter='\t')
        for item in result:
            writer.writerow([item[0], item[1]])
    return result

def get_all_lists():
    with open('synt_3grams/full_food_3grams_with_weights.csv', 'r', encoding='utf-8') as f1:
        food = [i for i in csv.reader(f1, delimiter='\t')]
    with open('synt_3grams/full_service_3grams_with_weights.csv', 'r',
              encoding='utf-8') as f1:
        service = [i for i in csv.reader(f1, delimiter='\t')]
    with open('food.csv', 'r', encoding='utf-8') as f1:
        food_l = [i for i in csv.reader(f1, delimiter='\t')]
    with open('service.csv', 'r', encoding='utf-8') as f1:
        service_l = [i for i in csv.reader(f1, delimiter='\t')]
    good_food = [i for i in food if int(float(i[-1])) > 0]
    bad_food = [i for i in food if int(float(i[-1])) < 0]
    good_serv = [i for i in service if int(float(i[-1])) > 0]
    bad_serv = [i for i in service if int(float(i[-1])) < 0]
    with open('service_with_3gramms.csv', 'w', encoding='utf-8', newline='')\
            as fs:
        writer = csv.writer(fs, delimiter='\t')
        for line in bad_serv[:int(len(bad_serv)//2)]:
            writer.writerow([line[0], '0'])
        for line in service_l:
            writer.writerow(line)
        for line in good_serv[int(len(good_serv)//2):]:
            writer.writerow([line[0], '1'])
    with open('food_with_3gramms.csv', 'w', encoding='utf-8', newline='')\
            as fs:
        writer = csv.writer(fs, delimiter='\t')
        for line in bad_food[:int(len(bad_food)//2)]:
            writer.writerow([line[0], '0'])
        for line in food_l:
            writer.writerow(line)
        for line in good_food[int(len(good_food)//2):]:
            writer.writerow([line[0], '1'])


def extract_fourgrams(path):
    with open(path, 'r', encoding='utf-8') as f1:
        fourgrams = []
        unit = {}
        dep = defaultdict(list)
        for line in f1.readlines():
            if line != '\n' and line[0] != '#':
                line = line.split('\t')
                unit[line[0]] = line
                dep[line[6]].append(line)
            else:
                grams = []
                for t in unit:
                    deps = find_dep4(dep, unit[t])
                    if deps:
                        grams.append(build_conseq(deps, unit))
                fourgrams.append(grams)
                unit = {}
                dep = defaultdict(list)
    print(fourgrams)
    return fourgrams


def find_dep4(dep, t):
    result = [t[0]]
    words = [t[0]]
    try:
        a = [i[0] for i in dep[t[0]] if i[0] in dep.keys() and dep[i[0]]]
        if len(a) > 0:
            words += a
        else:
            return None
    except:
        return None
    for idx in range(1, len(words)):
        a = words[idx]
        b = [i[0] for i in dep[a] if a in dep.keys()]
        b2 = []
        for idxb, c in enumerate(b):
            d = [i[0] for i in dep[c]]
            if len(d) > 0:
                b2.append([c, d])
        if len(b2) > 1:
            result.append([a] + b2)
    return result if len(result) > 1 else None


def build_conseq(tree, unit):
    result = []
    for t1 in tree[1:]:
        for t2 in t1[1:]:
            for t3 in t2[1:]:
                for t4 in t3:
                    line = [tree[0], t1[0], t2[0], t4]
                    result.append([unit[i][0] for i in line])
    return result


if __name__ == '__main__':
   extract_fourgrams('test.conllu')
