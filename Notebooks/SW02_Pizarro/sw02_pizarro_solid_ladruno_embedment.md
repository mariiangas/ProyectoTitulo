# sw02_pizarro_solid_ladruno_embedment.ipynb — descripción del modelo

Espécimen **SW02** (Pizarro Pohl, Kovarbasic & Stojadinovic, ETH Zurich; JSE 2025, 151(4) 04025011): muro bajo (squat) a escala real de 3000 x 2550 x 200 mm, carga axial de 1800 kN. Construido siguiendo la metodología de `RW2_Wallace/rw2_solid_ladruno_embedment.ipynb`: **hexaedros** (`LadrunoBrick`, formulación estabilizada de un punto `ssp`) y **barras discretas** embebidas en el hormigón (`LadrunoEmbeddedRebar`, adherencia perfecta, barras `CorotTruss`), con datos del espécimen. Unidades: **N, mm, MPa**.

| ítem | en este modelo | fuente |
|---|---|---|
| muro | 3000 x 2550 x 200 mm, sin elemento de borde | JSE Fig. 1; tesis sec. 3.1.2 |
| fundación | 4000 x 500 x 200 mm, un volumen, elástico, E x (1650 / 200) = rigidez en el plano del bloque de 1650 mm de ancho | JSE Fig. 1; E de referencia |
| viga de carga | 3000 x 500 x 200 mm, elástica, E x (900 / 200); peso propio correspondiente al ancho real de 900 mm | JSE Fig. 1; E de referencia |
| hormigón | `ASDConcrete3D` 9P: fc' 28.5 MPa, Ec 32145 MPa; ft y ecp según EC2 | JSE Tabla 2 |
| barras verticales | 18 phi10 por cara @ 150 (marca 10) + 1 phi16 por cara en cada extremo (marca 12) | plano SW02.pdf |
| estribos | rectángulos cerrados de phi10 @ 150 alrededor de toda la sección (marca 11) | plano SW02.pdf |
| acero | `Hysteretic`: phi10 523.65 / 569 al 2 % / 596.19 al 5.43 %; phi16 523.52 / 578 / 612.33 al 6.86 %; pinching 0.5 / 0.8 | JSE Fig. 3, ensayos de probetas; pinching base |
| protocolo | 46 puntos de inversión medidos del ensayo, incrementos de 0.25 mm | registro del ensayo experimental |

Se ejecuta con el `OpenSeesMP` de Ladruno en **2 particiones**.

Carpeta de ejecución: `sw02_pizarro_solid_ladruno_embedment/`.

## Armadura

Centros de barra (x desde el extremo izquierdo del muro, y desde el plano medio del muro). Los recubrimientos se toman a partir de las dimensiones del estribo exterior (295 x 16 cm), situando su eje a 25 mm de las caras y de los extremos del muro.

- **phi10 vertical** (marca 10): 18 por cara @ 150 centradas en el muro, x = 225 ... 2775, y = +-65.
- **phi16 vertical** (marca 12): 1 por cara en cada extremo, x = 38 y 2962, y = +-62 (esquinas del estribo).
- **estribos** (marca 11): rectángulos cerrados de phi10, x de 25 a 2975, y = +-75, @ 150 desde z = 75.

Las barras verticales se extienden desde 50 mm sobre el fondo de la fundación hasta 50 mm por debajo de la cara superior de la viga (los extremos en L y traslapes superiores de las marcas 13-14 no se modelan). Todas las barras: `CorotTruss` en su propia malla lineal, unidas a los hexaedros mediante `LadrunoEmbeddedRebar` con adherencia perfecta.

## Parámetros

**Geometría**

| variable | valor | significado |
|---|---|---|
| `base_depth` | 500 | profundidad del bloque de fundación |
| `base_overhang` | 500 | sobreancho del bloque de fundación más allá de cada extremo del muro |
| `beam_h` | 500 | altura de la viga de carga |
| `beam_t` | 900 | ancho fuera del plano de la viga de carga |
| `hw` | 2550 | altura del muro, desde la base hasta la carga lateral |
| `lw` | 3000 | longitud del muro |
| `tw` | 200 | espesor del muro |

**Discretización**

| variable | valor | significado |
|---|---|---|
| `bar_refine` | 4 | segmento de barra = max_size / bar_refine |
| `brick` | ssp | formulación de LadrunoBrick |
| `max_size` | 200 | tamaño máximo de elemento |
| `record_all` | True | registrador en cada nodo de hormigón |

**Armadura**

| variable | valor | significado |
|---|---|---|
| `anchor` | 50 | distancia de retranqueo de barras verticales respecto al fondo de base / tope de viga |
| `db10` | 10 | diámetro de barra phi10 |
| `db16` | 16 | diámetro de barra phi16 |
| `edge10` | 35 | distancia del eje vertical de phi10 a la cara |
| `edge16` | 38 | distancia del eje de phi16 a la cara y al extremo del muro |
| `hoop_edge` | 25 | distancia del eje del estribo a la cara y al extremo del muro |
| `hoop_step` | 150 | espaciamiento de estribos / trabas |
| `k_perfect` | 1e+08 | penalización axial de adherencia perfecta (LadrunoEmbeddedRebar) |
| `v_step` | 150 | espaciamiento de barras verticales phi10 |

**Hormigón**

| variable | valor | significado |
|---|---|---|
| `ec` | 32145 | módulo de elasticidad E |
| `ecp` | 0.00197742 | deformación unitaria en el pico e_cp |
| `fc0` | 5 | fin de la rama lineal f_c0 |
| `fcp` | 28.5 | resistencia máxima a compresión f_cp |
| `fcr` | 1 | resistencia residual f_cr |
| `ft` | 2.7991 | resistencia a la tracción f_t |
| `gc` | 33 | energía de fractura en compresión G_c |
| `gt` | 0.133412 | energía de fractura en tracción G_t |
| `nu` | 0.2 | coeficiente de Poisson |
| `pscale_c` | 0.3 | escala de deformación plástica en compresión |
| `pscale_t` | 0.3 | escala de deformación plástica en tracción |

**Acero**

| variable | valor | significado |
|---|---|---|
| `es10` | 198970 | módulo de elasticidad phi10 |
| `es16` | 196490 | módulo de elasticidad phi16 |
| `eu10` | 0.0543 | deformación unitaria de phi10 en f_u |
| `eu16` | 0.0686 | deformación unitaria de phi16 en f_u |
| `fu10` | 596.19 | tensión última de phi10 |
| `fu16` | 612.33 | tensión última de phi16 |
| `fy10` | 523.65 | tensión de fluencia de phi10 |
| `fy16` | 523.52 | tensión de fluencia de phi16 |
| `pinch_x` | 0.5 | estrangulamiento (pinching) Hysteretic, deformación |
| `pinch_y` | 0.8 | estrangulamiento (pinching) Hysteretic, fuerza |
| `s2_10` | 569 | tensión de phi10 al 2 % |
| `s2_16` | 578 | tensión de phi16 al 2 % |

**Partes elásticas**

| variable | valor | significado |
|---|---|---|
| `base_e` | 272250 | módulo elástico del bloque de fundación (sólido: escalado por ancho fuera del plano / t_w) |
| `beam_e` | 148500 | módulo elástico de la viga de carga (sólido: escalado por ancho fuera del plano / t_w) |

**Cargas**

| variable | valor | significado |
|---|---|---|
| `gamma_c` | 2.3544e-05 | peso unitario del hormigón (peso propio) |
| `p_axial` | 1.8e+06 | carga axial |

**Protocolo**

| variable | valor | significado |
|---|---|---|
| `peaks` | 46 puntos de inversión, -25.98 a 25.32 mm | desplazamiento superior impuesto (registro del ensayo) |
| `d_step` | 0.25 | incremento de desplazamiento |
| `n_cyclic` | 3566 | incrementos cíclicos |

## Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (10079 elementos, 5596 nodos) |
| secciones | - |
| materiales nD | `ASDConcrete3D`, `ElasticIsotropic` |
| materiales uniaxiales | `Hysteretic` |
| transformación geométrica | - |
| integración de viga | - |
| procesos | 2 rangos MPI (`OpenSeesMP`) |
| constraints / numberer / system | `Transformation` / `ParallelRCM` / `Mumps -ICNTL14 200 -matrixType 0` |
| algoritmo | `KrylovNewton -maxDim 10` |
| escala de alternativas (cíclico) | `KrylovNewton -maxDim 10`, `ModifiedNewton -initial`, `KrylovNewton`, `NewtonLineSearch -type Bisection` |
| etapa de gravedad | `LoadControl 0.1` x 10, `test EnergyIncr 0.0001 10 0 2` |
| etapa cíclica | `LoadControl 0.00028042624789680314` x 3566, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
