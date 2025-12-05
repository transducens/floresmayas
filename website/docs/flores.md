# Qué es FLORES+

[FLORES+](https://huggingface.co/datasets/openlanguagedata/flores_plus)[^1] es un **corpus paralelo** en más de 200 idiomas del mundo. Consiste en una selección de aproximadamente 2 000 oraciones tomadas del repositorio de [Wikimedia](https://www.wikimedia.org/) en inglés, abarcando diversas temáticas como deportes, ciencia, política, historia, etc; cada una de las frases se traduce a cada una de las lenguas incluídas con el propósito de crear un corpus paralelo entre estas. 

El conjunto de datos FLORES+ pertenece a una iniciativa llevada a cabo inicialmente por el equipo de Inteligencia Artificial de Meta, y seguidamente por la iniciativa [OLDI](https://oldi.org/), que busca enfocarse en la evaluación de sistemas de traducción automática  multilingüe de lenguas infrarrepresentadas o de escasos recursos.

<!--
## Cómo se construye un FLORES

La construcción de un FLORES conlleva una serie de pasos con el propósito de asegurar su calidad como recurso de procesamiento de lenguaje natural. En nuestro caso, este control de calidad es de especial importancia debido a la escasez de recursos en el campo; las frases den lenguas mayas incluidas en FLORES+ se convertirán en una cota de referencia (una _benchmark_) que podrá utilizarse para cualquier futuro esfuerzo en el desarrollo de tecnologías de lenguaje de las lenguas mayas por parte de cualquier otro equipo de investigación.

### Traducción desde el español
Puesto que es improbable que los traductores de lenguas mayas tengan un dominio fluido del inglés (o por lo menos comparable al que tuvieran del español), y para mantenerse en paralelo con los corpora de los FLORES, nuestras tareas de traducción se darán no desde las oraciones en inglés de Wikipedia sino desde sus respectivas traducciones al español. A pesar de estar al tanto del fenómeno del *translationese*[^2], creemos que los efectos de este son menos importantes que la posibilidad de trabajar con las lenguas mayas en paralelo con otras lenguas de escasos recursos del mundo. Si eligiéramos trabajar desde los textos originales en inglés, nos expondríamos a tiempos de procesamiento mucho más prolongados y a traducciones de inferior calidad.


### Selección de proveedores de servicios lingüísticos
Tanto FLORES-101 como FLORES-200 hablan de los llamados *Language Service Providers* (LSP) como las entidades encargadas de las traducciones y sus correspondientes controles de calidad. Tomando en cuenta nuestro escenario, es probable que nuestros LSP sean a traductores individuales para cada una de las lenguas en las que nos enfoquemos. Necesitamos un mínimo de dos traductores por lengua, uno para traducir y el otro para QA, aunque idealmente querríamos tres, con tal de seguir más de cerca el método de los FLORES, el cual estipula que dos LSP se encarguen de la traducción y uno del control de calidad.

### Las lenguas de la tarea
A pesar que nuestro objetivo sería la inclusión de todas las lenguas mayas reconocidas, como primera fase, comenzaríamos con las cinco lenguas mayas más habladas del páis: qʼeqchiʼ, kʼicheʼ, mam, kaqchikel, y chʼol. Como proyecto piloto, comenzaríamos con kʼicheʼ o qʼeqchiʼ, dependiendo del personal que lográramos contactar.
--->
[^1]: El nombre se trata probablemente de un acrónimo: *Focus on Low Resources*. En ningún lugar se aclara de manera explícita.

<!-- #### Nota sobre la ortografía
Es muy importante notar que el carácter que denota consonantes implosivas en las lenguas mayas, `ʼ`, es el MODIFIER LETTER APOSTROPHE ([pag 2](https://www.unicode.org/charts/PDF/U02B0.pdf)), cuyo código es `U+02BC`, y no el APOSTROPHE, `'`, ni el RIGHT SINGLE QUOTATION MARK, `’`, cuyos códigos son respectivamente `U+0027` y `U+2019`. A pesar de ser tipográficamente muy similares y hasta indistinguibles, la distinción es vital cuando se trata de segmentación a nivel de carácter; en las lenguas mayas, el apóstrofo unido a una consonante es un dígrafo que denota una fonema distinguible, y no una contracción, como ocurre en el caso del inglés (eg *don't*) o una elisión, como ocurre en el francés (eg *l'île*). -->
