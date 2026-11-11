# Fuentes

Todos los archivos fuente se consultan únicamente en modo de lectura.

| archivo | contenido | unidades | utilizado por |
|---|---|---|---|
| `../../../Bibliografia/Wallace/Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf` | Orakcal, Massone & Wallace (2006), *Analytical Modeling of RC Walls for Predicting Flexural and Coupled Shear-Flexural Responses*, PEER 2006/07, 228 páginas. El Capítulo 7 describe RW2 (Thomsen & Wallace 1995) | SI | `rw2_solid_ladruno_embedment` (geometría, armaduras, materiales), carga axial |
| `../ExperimentalData.txt` | Ensayo RW2, 674 filas, 2 columnas: desplazamiento superior, fuerza lateral | **m, tonf** | `rw2_solid_ladruno_embedment` (comparación con ensayo experimental) |

## Mapa de páginas de PEER 2006/07

El número de página impresa corresponde al índice de página del PDF menos 11.

| pág. pdf | impresa | contenido | imagen de evidencia |
|---|---|---|---|
| 100 | 89 | sec. 6.1: RW2 "altura de 3.66 m, espesor de 102 mm, longitud de 1.22 m, y carga axial aplicada de aprox. 0.07 Ag f'c" | - |
| 125 | 114 | sec. 7.1.1, Fig. 7.1 (especímenes), Fig. 7.2 (perfil de RW2, pedestal 1.93 x 0.69 m, armaduras) | [figs/peer607_pdf125-125.png](figs/peer607_pdf125-125.png) |
| 126 | 115 | sec. 7.1.1 texto (8 #3, mallas #2, alambre 4.76 mm, zona confinada en 1.22 m, ganchos a 90° en pedestal) y sec. 7.1.2 materiales (42.8 MPa, eps 0.002, Grado 60) | [figs/peer607_pdf126-126.png](figs/peer607_pdf126-126.png) |
| 127 | 116 | sec. 7.1.2 (#2 448 MPa sin meseta, alambre recocido 552 -> 448 MPa, endurecimiento plano), **Fig. 7.3a** sección transversal de RW2 con dimensiones | [figs/peer607_pdf127-127.png](figs/peer607_pdf127-127.png) |
| 128 | 117 | Fig. 7.4 curvas tensión-deformación del hormigón, Fig. 7.5 curvas tensión-deformación del acero | [figs/peer607_pdf128-128.png](figs/peer607_pdf128-128.png) |
| 141 | 130 | sec. 7.2.2.1: R0 = 20, a1 = 18.5, a2 = 0.0015 (Elmorsi et al. 1998) | - |
| 142 | 131 | **Tabla 7.1** (hormigón en tracción, acero en compresión) y **Tabla 7.2** (hormigón en compresión, acero en tracción) | [figs/peer607_pdf142-142.png](figs/peer607_pdf142-142.png) |

Figuras generadas con `pdftoppm -r 110 -f N -l N -png <pdf> figs/peer607_pdfN`.

## Scripts (`scripts/`)

| script | función | salida guardada |
|---|---|---|
| `audit_stko.py <deck dir>` | lista nodos, grupos de elementos, condiciones de borde, desplazamientos impuestos, etapas de carga y monitores | `audit_stko_output.txt` |
| `recover_9p.py <materials.tcl>` | recupera los parámetros de diálogo STKO `Concrete (9P)` a partir de las ramas `-Te/-Ts/-Td/-Ce/-Cs/-Cd` y los valida regenerando las curvas con `ASDConcrete3D.from_stko` | `recover_9p_output.txt` (diferencia máxima 4.4e-16) |
