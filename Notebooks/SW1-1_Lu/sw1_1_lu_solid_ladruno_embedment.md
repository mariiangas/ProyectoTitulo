# sw1_1_lu_solid_ladruno_embedment.ipynb — descripción del modelo

Espécimen **SW1-1** (Lu, Xie, Guan, Huang & Lu 2015; ensayo por Zhang, Tongji 2007): muro esbelto de 1000 x 2000 x 125 mm con elementos de borde confinados, carga axial de 246 kN. Construido según la formulación de `RW2_Wallace/rw2_solid_ladruno_embedment.ipynb`: **hexaedros** (`LadrunoBrick`, formulación estabilizada de un punto `ssp`) y **barras discretas** embebidas en el hormigón (`LadrunoEmbeddedRebar`, adherencia perfecta, barras `CorotTruss`), con datos del espécimen. Unidades: **N, mm, MPa**.

| ítem | en este modelo | fuente |
|---|---|---|
| muro | 1000 x 2000 x 125 mm, elementos de borde de 200 mm | Lu 2015 Fig. 7a |
| bloque de base | 1600 x 550 x 125 mm, un volumen, elástico, E x (390 / 125) = rigidez en el plano del bloque de 390 mm de ancho | Fig. 7a; E de referencia |
| hormigón | `ASDConcrete3D` 9P: alma 20.7 MPa a 0.002; núcleo de elemento de borde 25 MPa a 0.005 | THU Tabla 2; núcleo base (Mander) |
| barras de borde | 6 phi10 por extremo (3 columnas x 2 caras) | Fig. 7a sección 2-2 |
| barras del alma | 5 phi6 verticales por cara, phi6 @ 125 horizontal | Fig. 7a |
| estribos | phi6 @ 80 alrededor de cada grupo de 6 phi10, en toda la altura | Fig. 7a, THU Tabla 1 |
| acero | `Hysteretic`: phi6 392 / al 2 % / 479 al 10 %; phi10 379 / al 2 % / 554 al 10 %; b 0.01; pinching 0.5 / 0.8 | Fig. 7a; b del deck THU; eu y pinching base |
| protocolo | 24 puntos de inversión del archivo de ensayo, incrementos de 0.25 mm | `sw1-1_Test.txt` |

Se ejecuta con el `OpenSeesMP` de Ladruno en **2 particiones**.

Carpeta de ejecución: `sw1_1_lu_solid_ladruno_embedment/`.

## Armadura

Centros de barra (x desde el extremo izquierdo del muro, y desde el plano medio del muro). Las posiciones no están acotadas en detalle en Lu 2015; se adopta un recubrimiento de 15 mm al eje del estribo.

- **borde**: 6 phi10 por extremo, x = 23, 100, 177 (y simétrico), y = +-39.5.
- **alma vertical**: 5 phi6 por cara @ 125 centradas en el muro, x = 250 ... 750, y = +-39.5.
- **alma horizontal**: phi6 @ 125 en la altura, x desde 23 hasta 977, y = +-39.5 (mismo plano que las barras verticales, idealización reticulada; los extremos en U no se modelan).
- **estribos**: rectángulos cerrados de phi6 rodeando cada grupo de 6 phi10, @ 80 desde z = 40 hasta la parte superior; la traba interior de la Fig. 7a no se modela.

Las barras verticales se extienden desde `anchor_depth` dentro de la base hasta 23 mm bajo la cara superior. Todas las barras: `CorotTruss` en su propia malla lineal, unidas a los hexaedros mediante `LadrunoEmbeddedRebar` con adherencia perfecta.

## Parámetros

**Geometría**

| variable | valor | significado |
|---|---|---|
| `base_depth` | 550 | profundidad del bloque de fundación |
| `base_overhang` | 300 | sobreancho del bloque de fundación más allá de cada extremo del muro |
| `hw` | 2000 | altura del muro, desde la base hasta la carga lateral |
| `lbe` | 200 | ancho del elemento de borde / franja extrema |
| `lw` | 1000 | longitud del muro |
| `tw` | 125 | espesor del muro |

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
| `anchor_depth` | 500 | longitud de anclaje de barras verticales en la base |
| `be_cols` | 3 | columnas de barras de borde por elemento |
| `db10` | 10 | diámetro de barra phi10 |
| `db6` | 6 | diámetro de barra phi6 |
| `edge` | 23 | distancia del centro de la barra a la cara y al extremo del muro |
| `h_step` | 125 | espaciamiento de barras horizontales |
| `hoop_step` | 80 | espaciamiento de estribos / trabas |
| `k_perfect` | 1e+08 | penalización axial de adherencia perfecta (LadrunoEmbeddedRebar) |
| `web_n` | 5 | barras verticales del alma por cara |
| `web_step` | 125 | espaciamiento de barras del alma |

**Hormigón**

| variable | valor | significado |
|---|---|---|
| `ec` | 21400 | módulo de elasticidad E |
| `ecp` | 0.002 | deformación unitaria en el pico e_cp |
| `ecp_core` | 0.005 | e_cp del núcleo confinado |
| `fc0` | 5 | fin de la rama lineal f_c0 |
| `fc0_core` | 10 | f_c0 del núcleo confinado |
| `fcp` | 20.7 | resistencia máxima a compresión f_cp |
| `fcp_core` | 25 | f_cp del núcleo confinado |
| `fcr` | 4.14 | resistencia residual f_cr |
| `fcr_core` | 20 | f_cr del núcleo confinado |
| `ft` | 2.07 | resistencia a la tracción f_t |
| `gc` | 30 | energía de fractura en compresión G_c |
| `gc_core` | 60 | G_c del núcleo confinado |
| `gt` | 0.12595 | energía de fractura en tracción G_t |
| `nu` | 0.2 | coeficiente de Poisson |
| `pscale_c` | 0.3 | escala de deformación plástica en compresión |
| `pscale_t` | 0.3 | escala de deformación plástica en tracción |

**Acero**

| variable | valor | significado |
|---|---|---|
| `b_h` | 0.01 | razón de endurecimiento utilizada para la tensión al 2 % |
| `es10` | 202700 | módulo de elasticidad phi10 |
| `es6` | 200600 | módulo de elasticidad phi6 |
| `eu` | 0.12 | deformación unitaria en f_u |
| `fu10` | 554 | tensión última de phi10 |
| `fu6` | 479 | tensión última de phi6 |
| `fy10` | 379 | tensión de fluencia de phi10 |
| `fy6` | 392 | tensión de fluencia de phi6 |
| `k2` | 0.914634 | tensión al 2 % = f_y + k2 (f_u - f_y) |
| `pinch_x` | 0.5 | estrangulamiento (pinching) Hysteretic, deformación |
| `pinch_y` | 0.8 | estrangulamiento (pinching) Hysteretic, fuerza |
| `s2_10` | 539.061 | tensión de phi10 al 2 % |
| `s2_6` | 471.573 | tensión de phi6 al 2 % |

**Partes elásticas**

| variable | valor | significado |
|---|---|---|
| `base_e` | 71760 | módulo elástico del bloque de fundación (sólido: escalado por ancho fuera del plano / t_w) |

**Cargas**

| variable | valor | significado |
|---|---|---|
| `gamma_c` | 2.3544e-05 | peso unitario del hormigón (peso propio) |
| `p_axial` | 246000 | carga axial |

**Protocolo**

| variable | valor | significado |
|---|---|---|
| `peaks` | 24 puntos de inversión, -21.3 a 20.2 mm | desplazamiento superior impuesto (registro del ensayo) |
| `d_step` | 0.25 | incremento de desplazamiento |
| `n_cyclic` | 2378 | incrementos cíclicos |

## Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (4729 elementos, 2552 nodos) |
| secciones | - |
| materiales nD | `ASDConcrete3D`, `ElasticIsotropic` |
| materiales uniaxiales | `Hysteretic` |
| transformación geométrica | - |
| integración de viga | - |
| procesos | 2 rangos MPI (`OpenSeesMP`) |
| constraints / numberer / system | `Transformation` / `ParallelRCM` / `Mumps -ICNTL14 200 -matrixType 0` |
| algoritmo | `KrylovNewton -maxDim 10` |
| escala de alternativas (cíclico) | `KrylovNewton -maxDim 10`, `ModifiedNewton -initial`, `KrylovNewton`, `NewtonLineSearch -type Bisection` |
| etapa de gravedad | `LoadControl 0.1` x 10, `test NormDispIncr 0.0001 50 0 2` |
| etapa cíclica | `LoadControl 0.00042052144659377626` x 2378, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
