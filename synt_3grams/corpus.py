import os
import csv
import logging
from collections import defaultdict
from collections import Counter
import string


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


def extract_rel2(path_from, path_to, rel):  # trigrams with Heads VERB|NOUN|ADJ
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
                    if unit[t][1].lower() == rel:
                        for words in find_dep(unit, dep, t):
                            bigrams['\t'.join([str(k) for k in words])] += 1
                unit = {}
                dep = defaultdict(list)
        all_b = sum([bigrams[i] for i in bigrams])
        with open(path_to, 'w', encoding='utf-8', newline='') as f2:
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
        words = [head_words[1].lower(), head_words[2].lower(), head_words[3]]
        try:
            words += [dep_words[7], dep_words[1].lower(),
                      dep_words[2].lower(), dep_words[3]]
        except:
            continue
        try:
            words = words + [dep_dep[7], dep_dep[1].lower(),
                             dep_dep[2].lower(),  dep_dep[3]] if dep else \
                words + ['_'] * 4
        except:
            words += ['_'] * 4
            pass
        if 'punct' not in words:
            result.append(words)
    return result


def extract_rel3(path_from, path_to, rel): # negators
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
                    if unit[t][2].lower() == rel:
                        words = find_dep3(unit, dep, t)
                        trigrams['\t'.join(words)] += 1
                unit = {}
                dep = defaultdict(list)
        all_b = sum([trigrams[i] for i in trigrams])
        with open(path_to, 'w', encoding='utf-8', newline='') as f2:
            writer = csv.writer(f2, delimiter='\t')
            for br in trigrams:
                if trigrams[br] > 1:
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


def get_all_corp(path, path_to):
    files = [f for f in os.listdir(path)]
    with open(path_to, 'w', encoding='utf-8') as fw:
        for file in files:
            with open(f'{path}/{file}', 'r', encoding='utf-8') as fr:
                fw.write(fr.read())
                fw.write('\n\n')


def weight_trigrams(weights_path, trigrams_path, path_to):
    with open(weights_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        weights = {i[0].split('_')[0]: i[1] for i in reader}
    with open(trigrams_path, 'r', encoding='utf-8') as f2:
        reader2 = csv.reader(f2, delimiter='\t')
        trigrams = [i for i in reader2 if len(i) > 2]
    for t in range(len(trigrams)):
        if '_' in trigrams[t]:
            trigrams[t].remove('_')
    result = {}
    for i in trigrams:
        i = [a.rstrip(string.punctuation) for a in i if a != '_']
        t = [i[1].lower()+'_'+i[2], i[5]+'_'+i[6], i[9]+'_'+i[10]]\
            if len(i) == 13 else [i[1]+'_'+i[2], i[5]+'_'+i[6]]
        w = 0
        neg = 1 if len(t) > 5 and t[5] != 'не' else -1
        for word in t:
            try:
                w += float(weights[word.split('_')[0]])
            except KeyError:
                w = w
        result[' '.join(t)] = w * float(neg)
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    with open(path_to, 'w', encoding='utf-8', newline='') as f3:
        writer = csv.writer(f3, delimiter='\t')
        result = result[:len(result)//4] + result[-len(result)//4:]
        for item in result:
            writer.writerow([item[0], item[1]])
    return result


def get_all_deps(path_to):
    with open(path_to, 'w', encoding='utf-8', newline='') as fw:
        writer = csv.writer(fw, delimiter='\t')
        files = ['verb.csv', 'adj.csv', 'noun.csv', 'no.csv', 'not.csv']
        for file in files:
            with open(file, 'r', encoding='utf-8') as fr:
                table = [line for line in csv.reader(fr, delimiter='\t')]
                table = sorted(table, key=lambda x: x[-1], reverse=True)
                for line in table[:len(table)//10]:
                    writer.writerow(line)
    return


def get_all_lists():
    with open('synt_3grams/food_trigrams.csv', 'r', encoding='utf-8') as f1:
        food = [i for i in csv.reader(f1, delimiter='\t')]
    with open('synt_3grams/service_trigrams.csv', 'r',
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
        for line in service_l:
            writer.writerow(line)
        for line in bad_serv:
            writer.writerow([line[0], '0'])
        for line in good_serv:
            writer.writerow([line[0], '1'])
    with open('food_with_3gramms.csv', 'w', encoding='utf-8', newline='')\
            as fs:
        writer = csv.writer(fs, delimiter='\t')
        for line in food_l:
            writer.writerow(line)
        for line in bad_food:
            writer.writerow([line[0], '0'])
        for line in good_food:
            writer.writerow([line[0], '1'])


if __name__ == '__main__':
    pass
