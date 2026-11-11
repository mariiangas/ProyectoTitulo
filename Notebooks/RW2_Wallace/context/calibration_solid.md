# Calibración de `rw2_solid_ladruno_embedment.ipynb` (max_size 200, 2 particiones)

Criterio: valores del espécimen reportados en los documentos de ensayo, completados con la línea base calibrada de STKO para parámetros no reportados; `ASDConcrete3D` (preajuste 9P) + acero `Hysteretic`; barras embebidas Ladruno (adherencia perfecta). Protocolo: 40 puntos de inversión del registro experimental (incrementos de 0.5 mm, 5209 pasos).

Métricas (calculadas frente a los datos del ensayo experimental):
error de pico (+ / -); **envolvente (backbone)**: en cada nueva amplitud máxima, fuerza máxima \|F\| alcanzada por el modelo vs ensayo, error medio \|error\| sobre todos los niveles; **razón de energía**: energía disipada (área del ciclo) modelo / ensayo experimental.

| corrida | modificación | pico + / - vs ensayo | error medio envolvente | razón energía | resultado |
|---|---|---|---|---|---|
| it0 | espécimen + línea base, `stdBrick` | +10.3 % / +9.8 % | 24.4 % | 0.82 | 30-40 % más resistente en derivas bajas |
| it1 | `LadrunoBrick eas` | - | - | - | sin convergencia en paso 1032 (modos EAS + tangente IMPL-EX) |
| it1b | `LadrunoBrick ssp` | - | - | - | sin convergencia en paso 2435 (tolerancia 1e-5, sin alternativas) |
| **it1c** | `ssp` + escala `penalty-stiff` + tol cíclica 1e-4 | **+2.0 % / +0.6 %** | **16.0 %** | 0.73 | **seleccionada** |
| it2 | it1c + ft 1.0, pinching 0.8 / 0.9 | +2.7 % / +2.4 % | 15.9 % | 0.71 | sin mejora; se revirtió a ft 2.03 documentado y pinching base |

Conclusiones:

1. Los hexaedros lineales estándar de 8 nodos (`stdBrick`) presentan bloqueo por flexión con 1 elemento en el espesor: la respuesta resulta 30-40 % más resistente a 2-13 mm. `LadrunoBrick` con la formulación estabilizada de un punto (`ssp`) elimina este bloqueo, logrando un ajuste de pico de +2.0 % / +0.6 % frente al ensayo.
2. `ssp` requiere la escala de convergencia `penalty-stiff` (ModifiedNewton inicial -> KrylovNewton -> NewtonLineSearch en incrementos con falla) y una tolerancia cíclica de 1e-4 para completar todo el historial.
3. La diferencia observada en derivas bajas (+20-30 % a 2-14 mm frente al ensayo experimental) se asocia a la flexibilidad de la base (deslizamiento de armaduras y penetración de deformaciones en el pedestal) que no está incorporada en la fijación perfecta. Reducir ft o modificar los parámetros de pinching no cierra esta diferencia.

Configuración seleccionada: it1c (`brick = 'ssp'`, valores documentados del espécimen, preajuste 9P / pinching de referencia).

## Corrida final (configuración it1c, registro en cada nodo de hormigón)

Corte de pico -0.7 % / +2.2 % vs ensayo experimental, error medio de envolvente 16.1 %, razón de energía disipada 0.68. Carpeta de ejecución: `rw2_solid_ladruno_embedment/`.
