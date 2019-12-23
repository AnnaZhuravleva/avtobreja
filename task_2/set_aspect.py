# C:\Users\qwe\Documents\HSE\cosyco\udpipe\udpipe-1.2.0-bin\bin-win64\udpipe --output conllu --parse C:\Users\qwe\Documents\HSE\cosyco\udpipe\russian-syntagrus-ud-2.4-190531.udpipe < C:\Users\qwe\Documents\HSE\cosyco\norm_xix.conllu > C:\Users\qwe\Documents\HSE\cosyco\norm_xix_p.conllu

import os
import csv
import logging
from collections import defaultdict
from collections import Counter
from copy import deepcopy
import pandas as pd
from copy import copy
import string


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
fh = logging.FileHandler("logs.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s - %(asctime)s')
fh.setFormatter(formatter)
LOGGER.addHandler(fh)


def extract_fourgrams(path):
    with open(path, 'r', encoding='utf-8') as f1:
        fourgrams = {}
        coder = {}
        unit = {}
        dep = defaultdict(list)
        idx = 0
        for line in f1.readlines():
            if line != '\n' and line[0] != '#':
                line = line.split('\t')
                unit[line[0]] = line
                dep[line[6]].append(line)
            else:
                if unit:
                    idx += 1
                    fourgrams[idx] = []
                    coder[idx] = []
                for t in unit:
                    deps = find_dep4(dep, unit[t])
                    if deps:
                        grams, encoder = build_conseq(deps, unit)
                        fourgrams[idx] += grams
                        coder[idx] += encoder
                unit = {}
                dep = defaultdict(list)
    return fourgrams, coder


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
        if len(b2) > 0:
            result.append([a] + b2)
    return result if len(result) > 1 else None


def build_conseq(tree, unit):
    result = []
    coder = []
    for t1 in tree[1:]:
        for t2 in t1[1:]:
            for t3 in t2[1:]:
                for t4 in t3:
                    line = [tree[0], t1[0], t2[0], t4]
                    result.append([unit[i][2]+'_'+unit[i][3] for i in line])
                    coder.append([unit[i][0]for i in line])
    return result, coder


def extract_words(unit):
    try:
        return [[t[0], t[2].lower() + '_' + t[3]] for t in unit.values()]
    except:
        return


def extract_bigrams(unit, dep):
    bigrams = []
    for row in unit.values():
        head = [row[0], row[2].lower() + '_' + row[3]]
        nb = row[0]
        if nb in dep.keys():
            bigrams += [[head, [i[0], i[2].lower() + '_' + i[3]]]
                        for i in dep[nb]]
    return bigrams


def extract_trigrams(unit, dep):
    trigrams = []
    for row in unit.values():
        head = [row[0], row[2] + '_' + row[3]]
        nb = row[0]
        if nb in dep.keys():
            deps = [[i[0], dep[i[0]]] for i in dep[nb] if i[0] in dep.keys()]
            for i in deps:
                line1 = unit[i[0]]
                dep1 = [line1[0], line1[2].lower() + '_' + line1[3]]
                for item in i[1]:
                    line2 = unit[item[0]]
                    gram = [head, dep1,
                            [line2[0], line2[2].lower() + '_' +  line2[3]]]
                    trigrams.append(gram)
    return trigrams


def find_ngrams(filepath):
    '''
    :param filepath: path to conllu file
    :return: dictionary with all 1-, 2-, 3-gramms
    '''
    with open(filepath, 'r', encoding='utf-8') as f1:
        onegrams = {}
        bigrams = {}
        trigrams = {}
        fourgrams = {}
        unit = {}
        dep = defaultdict(list)
        idx = 0
        for line in f1.readlines():
            if line != '\n' and line[0] != '#':
                line = line.split('\t')
                unit[line[0]] = line
                dep[line[6]].append(line)
            else:
                if unit != {}:
                    idx += 1
                    onegrams[idx] = extract_words(unit)
                    bigrams[idx] = extract_bigrams(unit, dep)
                    trigrams[idx] = extract_trigrams(unit, dep)
                    fourgrams[idx] = []
                for t in unit:
                    deps = find_dep4(dep, unit[t])
                    if deps:
                        grams, encoder = build_conseq(deps, unit)
                        fourgrams[idx] += grams
                unit = {}
                dep = defaultdict(list)
    return onegrams, bigrams, trigrams, fourgrams


def set_score(food, service, food_b, service_b, ngram):
    result = []
    if isinstance(ngram[1], str):
        result = [str(ngram[0])]
        ngram = ngram[1].lower()
        if ngram in food.keys():
            result.append(f'food\t{food[ngram]}')
        if ngram in service.keys():
            result.append(f'service\t{service[ngram]}')
    elif isinstance(ngram[1], list):
        nb = '-'.join([str(i[0]) for i in ngram])
        result = [nb]
        ngram = tuple(set([i[1].lower() for i in ngram]))
        if ngram in service_b.keys():
            result.append(f'service\t{service_b[ngram]}')
        if ngram in food_b.keys():
            result.append(f'food\t{food_b[ngram]}')
    return result


def find_aspect(filepath, food_path, serv_path):
    '''
    :param filepath: path to conllu file (file should end with one single line)
    :param food_path: path to file with weights of food words
    :param serv_path: path to file with weights of service words
    :return: None, result in ./file score.txt
    '''
    with open(food_path, 'r', encoding='utf-8') as ff:
        reader = csv.reader(ff, delimiter='\t')
        food = {i[0].lower(): i[1] for i in reader}
        food_b = {tuple(set(i[0].split(' '))): i[1] for i in food.items() if
                  len( i[0].split(' ')) > 1}
    with open(serv_path, 'r', encoding='utf-8') as fs:
        reader = csv.reader(fs, delimiter='\t')
        service = {i[0].lower(): i[1] for i in reader}
        service_b = {tuple(set(i[0].split(' '))): i[1] for i in service.items()
                     if len(i[0].split(' ')) > 1}
    one, two, three, four = find_ngrams(filepath)
    for idx in one:
        grams = [i for i in one[idx]] + \
                [i for i in two[idx]] + \
                [i for i in three[idx]]
        for i in grams:
            score = set_score(food, service, food_b, service_b, i)
            if len(score) > 1:
                with open('score.txt', 'a', encoding='utf-8') as fo:
                    res = str(idx) + '\t' + score[0] + '\t' + score[1]
                    if len(score) == 3:
                        res += '\t' + score[2]
                    fo.write(res)
                    fo.write('\n')


if __name__ == '__main__':
    find_aspect('test.conllu', 'food_with_3gramms.csv',
                'service_with_3gramms.csv')