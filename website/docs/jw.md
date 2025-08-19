# JW Crawler

El sitio web de los Testigos de Jehová es uno de los recursos más valiosos con los que cuenta la comunidad de lenguas de escasos recursos ([Agić & Vulić 2019](https://aclanthology.org/P19-1310.pdf)).

La labor más importante del mes fue el desarrollo y ejecución de [`jw_crawler`](https://github.com/transducens/jw_crawler), un *crawler* del sitio de los Testigos de Jehová capaz de extraer textos paralelos de cualquier número de lenguas presentes en este a partir de los diferentes mapas de sitio disponibles.

<!-- Inicialmente utilicé el mapa en español, con lo que obtuve una cantidad de texto en paralelo comparable al del llorado JW300. -->

| Lengua | no. de párrafos | no. de párrafos  <br>no repetidos |
| --- | --- | --- |
| cak | 51 089 | 48 764 |
| ctu | 95 104 | 91 591 |
| kek | 81 969 | 81 000 |
| mam | 110 310 | 104 241 |
| poh | 10 136 | 10 130 |
| quc | 76 961 | 76 045 |
| tzh | 100 865 | 99 673 |
| tzo | 167 345 | 161 322 |
| yua | 192 726 | 186 111 |

<!-- No he pasado ningún tokenizador de oraciones, por lo que el número de estas es mayor para cada lengua. -->

Los textos, como cabe esperarse, no están perfectamente alineados entre sí; optamos por utilizar el alineador [`hunalign`](https://github.com/danielvarga/hunalign).

| Lengua | no. de URLs |
| --- | --- |
| en  | 33 245 |
| es  | 27 344 |
| fr  | 22 673 |
| de  | 27 097 |
| it  | 22 638 |

Realizamos una *crawl* completa para inglés y español, y no hay una diferencia significativa entre ambos en cuanto al número de documentos con textos paralelos en lenguas mayas (6 525 para español, 6 544, para inglés).