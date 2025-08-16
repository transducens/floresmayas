# FLORES-Mayas

## Qué es un FLORES

Los datasets [FLORES-101](https://arxiv.org/abs/2106.03193) y [FLORES-200](https://arxiv.org/pdf/2207.04672.pdf), (probablemente un acrónimo de *Focus on Low Resources*; en ningún lugar se aclara de manera explícita) son una iniciativa llevada a cabo por el equipo de Inteligencia Artificial de Meta que busca enfocarse en la evaluación de sistemas de TAN multilingüe de lenguas de infrarrepresentadas o de escasos recursos.

<!-- > In this work, we introduce the Flores-101 evaluation benchmark, consisting of 3001 sentences extracted from English Wikipedia and covering a variety of different topics and domains. These sentences have been translated in 101 languages by professional translators through a carefully controlled process. The resulting dataset enables better assessment of model quality on the long tail of low-resource languages, including the evaluation of many-to-many multilingual translation systems, as all translations are fully aligned. -->

Nuestros objetivo es construir un dataset para la evaluación de sistemas de TAN de lenguas mayas siguiendo los mismos métodos que se utilizaron para construir los FLORES. A este dataset los llamaremos FLORES-Mayas.

## En qué consiste un FLORES

Los FLORES consisten en una selección de aproximadamente 3 000 oraciones tomadas de Wikipedia en inglés, abarcando varias temáticas, las cuales son traducidas a las distintas lenguas objetivo, con el propósito de crear un corpus paralelo entre estas. El artículo de FLORES-101 entra en más detalle pero, en resumen, el dataset se divide en tres fracciones de aproximadamente 1 000 oraciones cada una, denominadas `dev`, `devtest`, `test`, de las cuales las primeras dos han sido publicadas ([aquí](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#flores-101) para FLORES‑101 y [aquí](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#download) para FLORES‑200)[^1].

[^1]: Del artículo: “The primary motivation for keeping the test set available only through an evaluation server is to guarantee equivalent assessment of models and reduce overfitting to the test set. Further, as the dataset is many-to-many, if the source sentences are released, the target sentences would also be released”.

## Cómo se construye un FLORES

La construcción de un FLORES conlleva una serie de pasos con el propósito de asegurar su calidad como recurso de procesamiento de lenguaje natural (PLN). En nuestro caso, este control de calidad (QA) es de especial importancia debido a la escasez de recursos en el campo; FLORES se convertirá en una cota de referencia (una _benchmark_) que podrá utilizarse para cualquier futuro esfuerzo de TAN de las lenguas mayas por parte de cualquier otro equipo de investigación.

### Traducción desde el español
Puesto que es improbable que los traductores de lenguas mayas tengan un dominio fluido del inglés (o por lo menos comparable al que tuvieran del español), y para mantenerse en paralelo con los corpora de los FLORES, nuestras tareas de traducción se darán no desde las oraciones en inglés de Wikipedia sino desde sus respectivas traducciones al español. A pesar de estar al tanto del fenómeno del *translationese*[^2], creemos que los efectos de este son menos importantes que la posibilidad de trabajar con las lenguas mayas en paralelo con otras lenguas de escasos recursos del mundo. Si eligiéramos trabajar desde los textos originales en inglés, nos expondríamos a tiempos de procesamiento mucho más prolongados y a traducciones de inferior calidad.

[^2]: [es decir](https://aclanthology.org/W19-5208.pdf): “[C]ompared to original texts, translations tend to be simpler, more standardised, and more explicit and they retain some characteristics that pertain to the source language”. 

### Selección de proveedores de servicios lingüísticos
Tanto FLORES-101 como FLORES-200 hablan de los llamados *Language Service Providers* (LSP) como las entidades encargadas de las traducciones y sus correspondientes controles de calidad. Tomando en cuenta nuestro escenario, es probable que nuestros LSP sean a traductores individuales para cada una de las lenguas en las que nos enfoquemos. Necesitamos un mínimo de dos traductores por lengua, uno para traducir y el otro para QA, aunque idealmente querríamos tres, con tal de seguir más de cerca el método de los FLORES, el cual estipula que dos LSP se encarguen de la traducción y uno del control de calidad.

### Las lenguas de la tarea
A pesar que nuestro objetivo sería la inclusión de todas las lenguas mayas reconocidas, como primera fase, comenzaríamos con las cinco lenguas mayas más habladas del páis: qʼeqchiʼ, kʼicheʼ, mam, kaqchikel, y chʼol. Como proyecto piloto, comenzaríamos con kʼicheʼ o qʼeqchiʼ, dependiendo del personal que lográramos contactar.

<!-- #### Nota sobre la ortografía
Es muy importante notar que el carácter que denota consonantes implosivas en las lenguas mayas, `ʼ`, es el MODIFIER LETTER APOSTROPHE ([pag 2](https://www.unicode.org/charts/PDF/U02B0.pdf)), cuyo código es `U+02BC`, y no el APOSTROPHE, `'`, ni el RIGHT SINGLE QUOTATION MARK, `’`, cuyos códigos son respectivamente `U+0027` y `U+2019`. A pesar de ser tipográficamente muy similares y hasta indistinguibles, la distinción es vital cuando se trata de segmentación a nivel de carácter; en las lenguas mayas, el apóstrofo unido a una consonante es un dígrafo que denota una fonema distinguible, y no una contracción, como ocurre en el caso del inglés (eg *don't*) o una elisión, como ocurre en el francés (eg *l'île*). -->