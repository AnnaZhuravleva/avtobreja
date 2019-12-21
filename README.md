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

## TODO:

### manual labor
- (done) _реферат_ Ася (и все остальные)
- (done) _manually tag part of test set_ Галя
- (done) _extract domain keywords_ Галя

### preprocessing
- (done) _xml parsing (train)_ Галя
- (done) _UDPipe_ Ася
  - fix lemmatization (* and «»)

### methods of extracting sentiment words
- (done) _apply vector method_ Лера
- apply graph method ?Ася??
  - find negators and adversaries ?Ася??
- apply pmi method Аня
- (done) _apply method from sem7_ Галя

### expanding sentiment words (Аня)
- (done) _w2v_
- (done) _expand via thesaurus_ (Возможно, для ключей стоит расширять только существительные и глаголы и только по гипонимам. Зато их, наверное, можно как-то расширять по словарю сочетаемости)
  - (done) _RuTez_
  - (done) _wikiwordnet_
- (done) _adagram_

### filter sentiment words
- methods intersection
- on co-occurence (если по словарю сочетаемости / по нашему корпусу тональное слово никогда не сочетается со словами из списка, мы его выбрасываем) Лера
- check by scores: Если в тексте в целом стоит очень низкая оценка сервиса, то слова, которые мы отнесли к аспекту сервиса из этого текста автоматически можно взвесить в отрицательную сторону пропорционально оценке.

### aspect separation
- слово по трейну сочетается больше со словами из одного списка ключей, чем из другого (сильно больше, потому что если 45/55% то надо и туда и туда)
- слово ворд-ту веком больше похоже на уже проверенные слова одного аспекта, а не другого
     
### detect sentiment words using created vocabulary
#### extracting sentiment words with our ready vocabulary
- ??
#### aspect separation
- если тональное слово по юдипайпу сочетается со словом из ключа аспекта - оно относится к этому аспекту (может быть разом несколько аспектов, тк "и кухня и обслуживание очень плохие")
