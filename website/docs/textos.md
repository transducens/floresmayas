# Textos paralelos

Un __texto paralelo__ se refiere al conjunto de dos o más textos multilingües, alineados a nivel de frase, donde cada una de las frases alineadas corresponde a la traducción de las demás, en cada uno de los idiomas involucrados. El siguiente es un ejemplo de un texto paralelo en español, mam, tzotzil, y maya yucateco:

![Texto paralelo entre español, mam, tzotzil, y maya yucateco](assets/texto_paralelo.png)

Los textos paralelos son necesarios para los sistemas modernos de TAN porque, para entrenarse, estos necesitan “ver” tanto texto como sea posible en todos los idiomas involucrados para aprender a traducir entre estos.

## Los vocabularios

Publicados por la Academia de Lenguas Mayas de Guatemala (ALMG), con la excepción del tzeltal, cada uno de los __vocabularios__ consiste en un listado de voces en una lengua maya, oraciones que ejemplifican sus usos, y sus correspondientes traducciones al español. El siguiente es un ejemplo de una entrada en el vocabulario mam:

![Ejemplo de entrada en el vocabulario mam](assets/vocab_qeqchi.png)

Los vocabularios son un recurso invaluable pues, además de tratarse de una colección de varios miles de frases en paralelo en diversas lenguas mayas, el registro lingüístico que utilizan corresponde al del uso más frecuente de los hablantes de cada comunidad lingüística. 

La extracción original de los vocabularios mayas, publicados por la ALMG en formato pdf de texto, fue llevada a cabo utilizando [`pdfplumber`](https://github.com/jsvine/pdfplumber). 

La ALMG ha publicado muchos más textos mono y bilingües que con los que contamos actualmente. A continuación un listado de los documentos de los que podríamos extraer textos paralelos:

#### Achi

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/09/VOCABULARIO.pdf)
- [Sinónimos](https://www.almg.org.gt/wp-content/uploads/2020/09/SINONIMOS.pdf)
- [Compendio de leyes](https://www.almg.org.gt/wp-content/uploads/2020/09/COMPENDIO-DE-LEYES.pdf)\*
- [Constitución de la república](https://www.almg.org.gt/wp-content/uploads/2020/09/CONSTITUCI%C3%93N-POL%C3%8DTICA-DE-LA-REP%C3%9ABLICA-DE-G..pdf)\*

#### Akateko

- [Expresiones](https://www.almg.org.gt/wp-content/uploads/2020/09/EXPRESIONES.pdf?__cf_chl_tk=xurSsxfHtKKkupKqUp7TMbnHzzu7x7LjeBKHDDcIWJI-1693406204-0-gaNycGzNDPs)\*
- [Popol Wu](https://www.almg.org.gt/wp-content/uploads/2023/05/Popol-Wu-Akateko.pdf)\*
- [Compendio de literatura](https://www.almg.org.gt/wp-content/uploads/2020/09/COMPENDIO-DE-LITERATURA-KUKUY-AKATEKA.pdf)\*

#### Awakateko

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/09/VOCABULARIO-1.pdf)
- [Vocabulario ilustrado](https://www.almg.org.gt/wp-content/uploads/2020/09/VOCABULARIO-ILUSTRADO-PEDAG%C3%93GICO.pdf).\*
- [Plantas Medicinales](https://www.almg.org.gt/wp-content/uploads/2020/09/PLANTAS-MEDICIONALES.pdf)\*
- [Lectura infantil](https://www.almg.org.gt/wp-content/uploads/2020/09/LITERATURA-INFANTIL.pdf)
- [Lectura infantil 2](https://www.almg.org.gt/wp-content/uploads/2020/09/LITERATURA-INFANTIL-VOLUMEN-No.-2.pdf)
- [Numeración](https://www.almg.org.gt/wp-content/uploads/2020/09/NUMERACI%C3%93N.pdf)

#### Ch'orti'

- [Vocabulario pedagógico](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-PEDAG%C3%93GICO-DEL-IDIOMA-CH_ORTI_.pdf)
- [Ley de idiomas mayas y su reglamento](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-DE-IDIOMAS-NACIONALES-Y-SU-REGLAMENTO.pdf)
- [Ley de catastro](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-DE-CATASTRO.pdf)
- [Ley de información pública](https://www.almg.org.gt/wp-content/uploads/2020/10/INFORMACION-PUBLICA.pdf)
- [Literatura](https://www.almg.org.gt/wp-content/uploads/2020/09/LITERATURA-BILINGUE-FINAL.pdf)

#### Chuj

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO.pdf)

#### Itza'

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-ITZA_.pdf)
- [Vocabulario pedagógico](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-PEDAG%C3%93GICO-ITZA_-FINAL.pdf)
- [Neologismos](https://www.almg.org.gt/wp-content/uploads/2020/10/NEOLOGISMOS.pdf)
- [Ley de idiomas mayas y su reglamento](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADUCCI%C3%93N-19-2003.pdf)\*
- [Ley contra la violencia sexual, explotación y trata de personas](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-CONTRA-LA-VIOLENCIA-SEXUAL-EXPLOTACI%C3%93N-Y-TRATA-DE-PERSONAS.pdf)\*
- [Ley contra el femicidio y otras formas de violencia contra la mujer](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADUCCI%C3%93N-DEL-DECRETO-22-2008.pdf)\*
- [Acuerdo de identidad de los pueblos indígenas](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADUCCI%C3%93N-ACUERDO-SOBRE-IDENTIDAD-Y-DD-DE-LOS-PUEBLOS-IND%C3%8DGENAS.pdf)\*

#### Ixil

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-1.pdf)
- [Textos literarios](https://www.almg.org.gt/wp-content/uploads/2020/10/LITERATURA.pdf)\*

#### Jakalteco/Popti

- [Vocabulario pedagógico](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-PEDAG%C3%93GICO.pdf)
- [Ley contra el femicidio y otras formas de la violencia contra la mujer](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-CONTRA-EL-FEMICIDIO.pdf)
- [Ley de simplificación de requisitos y trámites administrativos](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-DE-ACCESO.pdf)
- [Diccionario\*](https://www.almg.org.gt/wp-content/uploads/2020/10/ENTRADAS-DICCIONARIO-ESTANDAR.pdf)
- [Album infantil](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADICI%C3%93N-ORAL-ALBUM-INFANTIL.pdf)\*

#### Kaqchikel

- [Ley de idiomas mayas y su reglamento](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-DE-IDIOMAS-NACIONALES.pdf)
- [Ley de simplificación de requisito y trámites administrativos](https://www.almg.org.gt/wp-content/uploads/2023/05/LEY-PARA-LA-SIMPLIFICACION-DE-REQUISITOS-Y-TRAMITES-ADMINISTRATIVOS-1.pdf)
- [Popol Wuj](https://www.almg.org.gt/wp-content/uploads/2023/05/Popol-Wuj-Kaqchikel.pdf)\*(pdf de imágenes)

#### K'iche'

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-2.pdf)
- [Vocabulario de sinónimos](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-DE-SIN%C3%93NIMOS.pdf)\*
- [Ley de simplificación de requisito y trámites administrativos](https://www.almg.org.gt/wp-content/uploads/2023/05/LEY-PARA-LA-SIMPLIFICACION-DE-REQUISITOS-Y-TRAMITES-ADMINISTRATIVOS-1.pdf)

#### Mam

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-3.pdf)
- [Diccionario de sinónimos](https://www.almg.org.gt/wp-content/uploads/2020/10/DICCIONARIO-DE-SIN%C3%93NIMOS-1.pdf)\*
- [Ley de simplificación de requisito y trámites administrativos](https://www.almg.org.gt/wp-content/uploads/2023/05/LEY-PARA-LA-SIMPLIFICACION-DE-REQUISITOS-Y-TRAMITES-ADMINISTRATIVOS-1.pdf)
- [Diccionario bilingüe](https://www.almg.org.gt/wp-content/uploads/2020/10/DICCIONARIO-MAM-COLIMAM.pdf)
- [Popol U'j](https://www.almg.org.gt/wp-content/uploads/2023/05/Pop-Uj-Mam-_-ALMG.pdf)\*(pdf de imágenes)
- [Numeración maya](https://www.almg.org.gt/wp-content/uploads/2020/10/NUMERACI%C3%93N-MAYA.pdf)

#### Mopan

- [Ley mopan](https://www.almg.org.gt/wp-content/uploads/2020/10/22-2008-Ley-Mopan.pdf)\*
- [Código municipal](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADUCCION-CODIGO-MUNICIPAL.pdf)\*
- [Ley de consejos de desarrollo urbano y rural](https://www.almg.org.gt/wp-content/uploads/2020/10/TRADUCCION-LEY-DE-CONSEJOS-DE-DESARROLLO-URBANO-Y-RURAL.pdf)\*

#### Poqomam

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/DICCIONARIO-POQOM-ESPA%C3%91OL-2019.pdf)

#### Poqomchi

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-4.pdf)
- [Ley de idiomas mayas y su reglamento](https://www.almg.org.gt/wp-content/uploads/2020/10/LEY-DE-IDIOMAS-NACIONALES-1.pdf)
- [Diccionario bilingüe](https://www.almg.org.gt/wp-content/uploads/2020/10/DICCIONARIO-2003.pdf)
- [Lectura](https://www.almg.org.gt/wp-content/uploads/2020/10/ILHUJB_AL-POQOMCHI_-TEXTO-LECTURA.pdf)\*

#### Q'anjob'al

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-5.pdf)

#### Q'eqchi'

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-6.pdf)
- [Ley de simplificación de requisito y trámites administrativos](https://www.almg.org.gt/wp-content/uploads/2023/05/LEY-PARA-LA-SIMPLIFICACION-DE-REQUISITOS-Y-TRAMITES-ADMINISTRATIVOS-1.pdf)
- [Poopol Hu](https://www.almg.org.gt/wp-content/uploads/2023/05/Popol-Wj-Infantil-Qeqchi.pdf)\*

#### Sakapulteko

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-7.pdf) (pdf de imágenes)

#### Sipakapense

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-8.pdf)

#### Tektiteko

- [Diccionario bilingüe](https://www.almg.org.gt/wp-content/uploads/2020/10/DICCIONARIO-BILINGUE-TEKTITEKO.pdf)

#### Tz'utujil

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-9.pdf)

#### Uspanteko

- [Vocabulario](https://www.almg.org.gt/wp-content/uploads/2020/10/VOCABULARIO-10.pdf)
- [Popol Wuuj](https://www.almg.org.gt/wp-content/uploads/2023/05/Popol-Wuj-Uspanteka.pdf)\*

\*<small>denota texto mayormente monolingüe.</small>