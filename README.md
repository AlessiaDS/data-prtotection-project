## How to run the main
The command that needs to be used has the following format:
+ `-pt` *"path of the table to anonymize"* 
+ `-qi` *"quasi_identifier_1" "qi_2" ... "qi_n"* 
+ `-dgh` *"generalization_table_of_qi_1" "gen_table_qi_2" ... "gen_table_qi_n"*
+ `-k` *"k (int) to use as anonymization criteria"*
+ `-o` *"path+name of the file where to save the anonymized table"*

Example:
`-pt "C:\Users\giamp\PycharmProjects\pythonProject\DP-Project3\tables\db_20.csv" -qi "age" "sex" "zip_code" -dgh "C:\Users\giamp\PycharmProjects\pythonProject\DP-Project3\tables\age_generalization.csv" "C:\Users\giamp\PycharmProjects\pythonProject\DP-Project3\tables\sex_generalization.csv" "C:\Users\giamp\PycharmProjects\pythonProject\DP-Project3\tables\zip_code_generalization.csv" -k 5 -o "db_20_5_incognito.csv"`

## Changelog
+ Changelog 3
    + Merged `combination` and `recursiveComb`, now `combination` will use the function `product` from `itertools`
    + ~~Added `get_tree_height` to `Node` in order to get the heights of the trees of generalization of the ___QIs___, development needed to make it work~~
        + `get_tree_height` changed to `getTreeHeight`, moved from `Node` to `CsvDGH` and now is working as intended
        + ~~Forgot to delete `get_tree_height` from `Node`, will update it as soon as i can~~ Done
+ Changelog 2
    + Added function `combination` to get a list of touples that will specify the generalization level of the ___QIs___ during the generation of generalized tables
    + Added function `recursiveComb` to make `combination` work for any number of ___QIs___
    + Added variable `combinations` to the function `anonymize`
+ Changelog 1
    + Corrected concatenation tuple on recursion previous to 0
    + Removed `domains` (was used for cardinality calc)
    + Added variable `qi_frequency_candidates` to save the K-Anon tables generated
    + Added variable `qi_frequency_states` for the many table SaveStates
    + Added function `resetState` to reset the table to a specific state (needed for Anon)
    + Added function `recResetState` to make `resetState` work for any number of ___QIs___
    + Added variable `saveState` to the function `anonymize`
## TODO
+ Complete review (and possible improvements) of `anonymize`
+ Improvement of `getTreeHeight` (the function can still be used like the current version, only it's implementation will change)
+ Selection of the ___K-Anon Minimum table___ between the candidates
+ Start process of testing and work on fixes if needed
+ Update the `README.md` documentation after the needed changes are applied, or if needed to be able to get a grasp of certain variables/functions/synergies

## Anon-Comb

Visto che si andrà a riutilizzare la maggior parte del codice del laboratorio presente su Aula Web ho optato per riutilizzare parte di tale codice e modificarlo a seconda delle esigenze di Incognito.

Partendo dal metodo `anonymize`, tra gli attributi inizializzati ho aggiunto semplicemente `qi_frequency_candidates`, il quale sarà una lista di Dizionari e avrà il compito di salvare tutte le istanze della tabella generalizzata (salvata sotto forma di dizionario) mentre viene generalizzata combinazione dopo combinazione.
Il resto delle variabili inizializzate, compresi `qi_frequency` e `domains`, sono rimasti invariati.

### Generalization
A questo punto viene creata una lista di combinazioni (tuple) tramite il metodo `combination()`, queste saranno le combinazioni che verranno usate per generalizzare la tabella.
```python
combinations = combination(qi_names,dghs)
```
Le tuple in se specificheranno solo il livello di generalizzazione che ogni attributo dovrà seguire per ogni combinazione, ma avendo inserito i livelli ordinatamente basterà iterare i valori della tupla ed eseguire le generalizzazioni in modo ordinato per andare in confusione.

Al posto di un `while True`, dal quale si dovrà poi uscire con un break, ho usato gli elementi in `combinations` come criterio per chiudere il ciclo For. _(una volta lette tutte le tuple `data` esco dal For)_

Qui al posto di usare `attribute_idx` per decidere che attributo generalizzare userò la tupla `data`, la quale contiene in ordine che livello di generalizzazione ogni QI deve avere.

Il processo di generalizazione (in locale) è rimasto quasi invariato, ho aggiunto giusto un _For_ per eseguire tale procedimento su tutti gli attributi necessari, e reso `generalized_value` un dizionario, per poter lavorare allo stesso modo nei multipli cicli di generalizzazione.

```python
new_qi_sequence = list(qi_sequence)
for id, gen_val in generalized_value.items():
    new_qi_sequence[id] = gen_val
new_qi_sequence = tuple(new_qi_sequence)
```
Poi si passa a salvare i valori generalizzati nei corrispettivi campi, appartenenti alla tupla presa in esame. (passaggio Tupla -> Lista -> Tupla necessario per poter modificare i valori, visto che i valori nelle tuple non si sono modificabili)

Gli aggiornamenti di `qi_frequency` e `domains` sono rimasti prevalentemente invariati.

```python
qi_frequency_candidates.append(qi_frequency)
```
E aggiungo lo stato della tabella attuale alla lista dei candidati `qi_frequency_candidates`.

### K-Anon Minimum
> Ancora da implementare

### Output file
Questa parte ha subito pressochè zero cambiamenti.
Tra le sequenze di attributi salvati, vengono tolti (o "soppressi") solo quelli che hanno una ripetizione inferiore a K
```python
if data[0] < k:
    qi_frequency.pop(qi_sequence)
```
E in fine si inizia a scrivere la tabella generalizzata nel file di output (formattando la riga da scrivere con `_set_values`).

## Combinations
Questi metodi si possono scrivere tranquillamente nello stesso file di `anonymize`, ma richiederanno l'implementazione di un metodo `tree.length` per poter funzionare.

`combination` farà una breve preparazione per iniziare a lanciare ricorsivamente `recursiveComb`, dandogli la lunghezza della ricorsione `rec_length` (che servirà da indice per specificare il massimo livello di generalizazione che ciascun attributo avrà), i nomi dei vari attributi (`qi_names`), i vari alberi di generalizzazione (`dghs`) e la lista `comb` che conterrà tutte le combinazioni.

`recursiveComb` (se `rec_length` è diverso da zero) entrerà in un ciclo di ricorsione che si ripeterà tante volte quanto siano i livelli di generalizzazione dell'attributo preso in esame nella ricorsione corrente (che come specificato precedentemente verrà specificato da `rec_length`).
```python
for i in range(dghs.length(qi_names[rec_length])):
    recursiveComb(rec_length - 1, qi_names, dghs, comb, base+(i,))
```
Alla chiamata ricorsiva si daranno in input le stesse variabili specificate prima, con un paio di modifiche:
`rec_length` verrà ridotto di 1 e in aggiunta si darà una tupla contenente i livelli di generalizzazione delle ricorsioni precedenti (`base`) concatenata con la tupla composta dal livello di generalizzazione dell'attributo preso in esame nella ricorsione corrente (`(i,)`).
_P.S.: Questo non conta come "modificare" una tupla, si manda semplicemente una tupla composta da due tuple concatenate._
```python
for i in range(dghs.length(qi_names[rec_length])):
    comb.append(base + (i,))
```
Arrivati all'ultimo attributo dei QI (`rec_length == 0`) si entrerà in un altro ciclo _For_ che inizierà a inserire in `comb` varie concatenazioni, incrementando di 1 il livello di generalizzazione dell'ultimo attributo per ogni inserimento (`append`).
Una volta uscito dal ciclo _For_ si tornerà alla ricorsione precedente, la quale incrementerà il suo livello di generalizzazione e chiamerà nuovamente (ricorsivamente) la funzione sul seguente attributo.
