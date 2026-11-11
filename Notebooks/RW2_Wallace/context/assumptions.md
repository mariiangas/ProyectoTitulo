# Supuestos y puntos abiertos

## `rw2_solid_ladruno_embedment.ipynb`

| # | supuesto | justificación | efecto / cómo modificar |
|---|---|---|---|
| 1 | El bloque de base tiene el espesor del muro (102 mm) y E = 28198 x 500 / 102 | La base proporciona la rigidez equivalente de la fundación en el plano; el muro superior no se modifica | `base_e`, `base_overhang`, `base_depth` |
| 2 | El muro se divide en z = 1220 mm en una zona de borde confinado | sec. 7.1.1: elementos de borde detallados en los 1.22 m inferiores | `h_conf` |
| 3 | Los valores de hormigón 9P fc0 10, fcr 10, Gt 0.1, Gc 36, pscale 0.3 se toman del preajuste de STKO | El reporte original no incluye energías de fractura ni resistencias residuales | celda de entradas |
| 4 | El hormigón confinado utiliza los mismos valores fc0 / fcr / Gc que el no confinado | Simplificación directa; únicamente varían fcp y ecp (Tabla 7.2) | celda de entradas |
| 5 | Valores de acero de barra desnuda (434 / 448 MPa), no los valores reducidos en tracción (395 / 336 MPa) | Barras discretas; el efecto de rigidización por tracción (tension stiffening) se incluye en la rama de ablandamiento del hormigón | `fy3`, `fy2` |
| 6 | Endurecimiento del alambre b = 0.005 | El artículo indica: "relativamente plano"; sin valor numérico explícito | `bw` |
| 7 | Barras del alma horizontales y verticales en el mismo plano (y = +-32) | Idealización de reticulado; las barras no interactúan cinemáticamente entre sí | - |
| 8 | Barras del alma en 3 @ 191 centradas (separación de 151.5 mm en lugar de 153 mm) | Las cotas del plano suman 1223 mm frente a los 1219 mm reales | `web_x` |
| 9 | Las barras horizontales inician en z = 191 y van desde x = 19 hasta 1201 mm | Espaciamiento de Fig. 7.3a; la posición vertical de la primera barra no está especificada | celda de armaduras |
| 10 | Estribos únicamente bajo 1220 mm, @ 76 desde z = 38 mm; trabas internas con gancho no modeladas | El reporte solo detalla armadura de confinamiento en los 1.22 m inferiores | celda de armaduras |
| 11 | Barras verticales rectas, embebidas 450 mm en la base, sin ganchos | Los ganchos del pedestal sirven para anclaje; con adherencia perfecta la barra recta queda fijada | `anchor_depth` |
| 12 | Adherencia perfecta: `k_perfect = 1e8` | Modelo inicial continuo; la adherencia con deslizamiento (`LadrunoBondSlip`) puede añadirse posteriormente | `k_perfect` |
| 13 | 2 particiones MPI | apeGmsh `f8eae4cc` asigna cada restricción al rango de su hexaedro anfitrión y declara el nodo fantasma de la barra | `nparts` |
| 14 | `max_size = 100`, 2 elementos a través del espesor (51 mm) | Mantiene la relación de aspecto de los hexaedros en 2 o menos | `max_size` |
| 14b | Barras discretizadas en `max_size / bar_refine` (25 mm), aprox. 4 nodos de barra por hexaedro atravesado | Regla de modelación: discretización de barras 4 veces más fina que el hormigón | `bar_refine` |
| 15 | Carga axial 0.07 Ag f'c como tracción uniforme sobre la cara superior | Mismo total que la carga axial especificada en el ensayo | `p_axial` |
| 16 | `max_size = 500` para las primeras corridas de prueba (1 elemento en el espesor, 38 hexaedros) | Verificación rápida de convergencia; la malla operativa es `max_size = 100` o `max_size = 200` | `max_size` |

Puntos abiertos: los parámetros de tracción del hormigón (Gt con ft = 2.03) y la energía de fractura del hormigón confinado pueden contrastarse con la Fig. 7.4; las losas de piso cada 0.915 m (sec. 7.1.1) no están modeladas en el cuaderno.
