# Datos experimentales de RW2

Fuente: Orakcal, Massone y Wallace (2006), *Analytical Modeling of Reinforced
Concrete Walls for Predicting Flexural and Coupled Shear-Flexural Responses*,
PEER 2006/07, `Bibliografia/Wallace/Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf`.

La carpeta reúne la curva global y las referencias locales del ensayo RW2.

`ExperimentalData.csv` contiene los 674 pares de desplazamiento superior y fuerza
lateral del antiguo `ExperimentalData.txt`, en su orden original. La conversión
conserva todos los valores y sus unidades. Sus columnas son `displacement_m`
(desplazamiento en m) y `force_tonf` (fuerza en tonf). Para comparar con el modelo
se multiplica el desplazamiento por 1000 y la fuerza por 9.80665 para obtener
mm y kN, respectivamente. El origen documental del registro global se describe
en `../context/experimental_data.md` y `../context/sources.md`.

Los CSV `fig_*.csv` son **digitalizaciones gráficas de los trazos experimentales Test**,
no archivos originales de adquisición. `provenance.json` identifica el PDF por
SHA256, método y precisión gráfica aproximada. El script reproducible es
[`digitize_rw2_local.py`](digitize_rw2_local.py), ubicado en esta carpeta.

| Archivo | Contenido | Página impresa / PDF | Unidades |
|---|---|---|---|
| ExperimentalData.csv | Curva global de desplazamiento superior y fuerza lateral, 674 puntos | Registro preexistente; ver `../context/experimental_data.md` | m; tonf |
| fig_7_30_concrete_strain.csv | Perfiles de hormigón, positivos, 0.5/1/2 % nominal | 145 / 156 | x: mm; strain: mm/mm |
| fig_7_31_steel_strain.csv | Barras verticales, base y primer nivel; incluye 2.5 % en primer nivel | 145 / 156 | x: mm; strain: mm/mm |
| fig_7_32_concrete_history.csv | Sensor embebido y LVDT interpolado del borde sur | 146 / 157 | registro adimensional; strain: mm/mm |
| fig_7_29_first_story.csv | Rotación y desplazamiento de flexión del primer nivel | 144 / 155 | rad; mm |
| fig_7_28_displacement_profiles.csv | Perfiles Test en niveles 1 a 4 para siete derivas y ambos sentidos; origen geométrico en nivel 0 | 143 / 154 | mm; nivel adimensional |
| fig_8_3_story_components.csv | Componentes por nivel; curvas identificables, sin referencia elástica | 160 / 171 | Uf/Ufy para flexión; mm para corte; kN |
| fig_9_3_first_story.csv | Trazos experimentales cíclicos de flexión y corte | 186 / 196 | mm; kN |

`source_figures/` conserva recortes del informe para revisar los perfiles completos
de 7.28, la separación de 8.3 y las curvas de corte de 7.23(a)/7.24(a).
El PDF original permanece intacto. Los recortes de 7.28 y 8.3 contienen también
las curvas analíticas del informe, identificadas por sus leyendas; los CSV
experimentales no incorporan esas curvas.

## Convenciones y límites

- Deformación positiva: tracción. `nominal_drift_pct` es la etiqueta del ensayo,
  no el desplazamiento del protocolo dividido por 3660 mm.
- El informe no identifica el número de ciclo de cada perfil local: se conserva
  `cycle=not_reported`. `profile_cycle` selecciona explícitamente el ciclo numérico
  que se superpone; su valor queda guardado con la corrida/postproceso.
- Secuencia nominal de los diez bloques de dos ciclos:
  0.1, 0.25, 0.5, 0.75, 1, 1.5, 1, 1.5, 2 y 2.5 % (sección 7.1.5).
- Los picos del protocolo actual coinciden con la columna **(b)** de la Tabla 7.3:
  movimiento del pedestal descontado, corte incluido. Las figuras de flexión del
  capítulo 7 descuentan además el corte. No se cambia el protocolo al postprocesar.
- Fig. 7.30: siete LVDT, longitud 229 mm. El inicio z=0 mm del sensor virtual es
  un supuesto configurable; se interpola el desplazamiento de sus extremos.
- Fig. 7.31: alturas aproximadas 25 y 950 mm; perfiles numéricos promediados entre
  las dos caras. Son deformaciones axiales de las barras, no del hormigón vecino.
- Fig. 7.32: longitud 83 mm, centro z≈92 mm. Se utiliza x=25 mm como supuesto del
  borde sur. El sensor embebido falla en el registro 330 (≈0.75 % nominal) y su
  tracción no es confiable. El LVDT interpolado se limita al registro 515.
- Las historias se alinean por reversiones solo si se reconoce la secuencia
  completa; esa alineación es aproximada y no admite métricas punto a punto sin
  sincronización original. Un registro del informe no es pseudo-tiempo ni segundos.
- Fig. 7.28 utiliza los trazos discontinuos Test del PDF vectorial, muestreados
  en los niveles 1, 2, 3 y 4 para derivas de 0.25, 0.5, 0.75, 1, 1.5, 2 y 2.5 %,
  en ambos sentidos. La interpolación lineal cubre los espacios entre guiones del
  trazo publicado. Los puntos en nivel 0 representan el origen geométrico.
  Se corrigió la asociación del perfil positivo de 0.25 %, que antes tomaba un
  segmento de la leyenda. L6 superpone ensayo discontinuo con marcadores y modelo
  continuo, utilizando el mismo color para cada deriva. La procedencia queda
  registrada en `provenance.json`.
- Fig. 8.3(a): la flexión está normalizada por la primera fluencia del ensayo.
  Se muestra como referencia; no se inventa un desplazamiento de fluencia dimensional.
- En el segundo nivel no había instrumentos verticales para la corrección X del
  ensayo (sección 8.1.5). La estimación corregida numérica se identifica separadamente.
- Los rótulos de unidades en 7.23/7.24 presentan inconsistencias aparentes entre
  distorsión, desplazamiento y carga. Se conservan como imágenes de referencia;
  la comparación dimensional de corte usa la Fig. 9.3, con ejes verificables.
- Las curvas analíticas de la Fig. 9.3 provienen de análisis monotónicos del
  informe. Los trazos Test digitalizados son cíclicos.

La precisión gráfica declarada describe el trazado publicado, no la incertidumbre
de los instrumentos. El acuerdo con estas curvas no valida automáticamente daño,
anchos de fisura, adherencia, pandeo o fractura de barras.
