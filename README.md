# Репозиторий проекта по АвтОбрЕе
## Участники:
- [Аня Журавлёва](https://github.com/AnnaZhuravleva)
- [Лера Морозова](https://github.com/leramorozova)
- [Галя Рязанская](https://github.com/flying-bear/)
- [Ася Сидорова](https://github.com/SerasLain)
## Полезные статьи
- [sentence-level classifier](https://www.aclweb.org/anthology/C14-1018.pdf)
- [use more seeds for PMI](https://www.aclweb.org/anthology/C16-1147.pdf) - SO(w) = pmi(w, pos) − pmi(w, neg)
- [graph measures of co-occurence](http://www.dialog-21.ru/media/3388/dubatovkaaetal.pdf)

## Полезные ссылки
- [UDPipe parsed](https://drive.google.com/open?id=181szxLRYHorRrzGTcA1XwwA23MVy7F90)
- [UDPipe lemmatized and POS-tagged dataset](https://drive.google.com/open?id=1oqzArfz05A7Wecfs95FXPy1VyjU2tnkx)
- [ruscorpora_upos_cbow_300_20_2019](http://vectors.nlpl.eu/repository/11/180.zip)

## TODO:

### manual labor
- (done) _реферат_ Ася (и все остальные)
- (done) _manually tag part of test set_ Галя
- (done) _extract domain keywords_ Галя

### preprocessing
- (done) _xml parsing (train)_ Галя
- (done) _UDPipe_ Ася
  - (done) _fix lemmatization_ (* and «» didgits)

### methods of extracting sentiment words
- (done) _apply vector method_ Лера
- (done) _apply method from sem7_ Галя
- apply graph method Ася

### expanding sentiment words (Аня)
- (done) _w2v_
- (done) _expand via thesaurus_
  - (done) _RuTez_
  - (done) _wikiwordnet_
- (done) _adagram_
- add bigrams

### expanding key words
- (done) _same as expanding sentiment words_ Аня (Возможно, для ключей стоит расширять только существительные и глаголы и только по гипонимам)
- (done) _by CNN_ Галя
- by clustring w2v on domain specific words
  - extract  domain specific words
  - cluster around centroids of manually extracted keys

### filter sentiment words
- (done) _methods intersection_ Аня
- check by scores Аня??? (Если в тексте в целом стоит очень низкая оценка сервиса, то слова, которые мы отнесли к аспекту сервиса из этого текста автоматически можно взвесить в отрицательную сторону пропорционально оценке)

### aspect separation
- слово по трейну сочетается больше со словами из одного списка ключей, чем из другого (сильно больше, потому что если 45/55% то надо и туда и туда)
- слово ворд-ту веком больше похоже на уже проверенные слова одного аспекта, а не другого
     
### detect sentiment words using created vocabulary
#### extracting sentiment words with our ready vocabulary
- ??
#### aspect separation
- если тональное слово по юдипайпу сочетается со словом из ключа аспекта - оно относится к этому аспекту (может быть разом несколько аспектов, тк "и кухня и обслуживание очень плохие")
