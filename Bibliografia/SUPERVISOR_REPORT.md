# Informe de supervisión: estado de modelos sólidos y bibliografía

## 1. Alcance y estructura del proyecto

- La carpeta de trabajo se encuentra acotada exclusivamente a los modelos tipo **sólido** (`solids`) implementados en apeGmsh / apeSees y ejecutados con el fork Ladruno de OpenSees en `Notebooks/`:
  - `RW2_Wallace/`: modelo sólido `rw2_solid_ladruno_embedment.ipynb` (muro rectangular esbelto, h_w/l_w = 3.0).
  - `SW1-1_Lu/`: modelo sólido `sw1_1_lu_solid_ladruno_embedment.ipynb` (muro rectangular esbelto, h_w/l_w = 2.0).
  - `SW02_Pizarro/`: modelo sólido `sw02_pizarro_solid_ladruno_embedment.ipynb` (muro bajo a escala real, h_w/l_w = 0.85).
- La carpeta de bibliografía (`Bibliografia/`) contiene la documentación de respaldo de los especímenes del proyecto:
  - `Wallace/`: Reporte PEER 2006/07 en PDF (`Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf`).
  - `Lu/`: Referencias del muro SW1-1 (Zhang 2007; Lu et al. 2015).
  - `Pizarro/`: Referencias del muro SW02 (Pizarro Pohl et al. 2025).

## 2. Estado del modelo sólido RW2 (`rw2_solid_ladruno_embedment`)

El modelo emplea hexaedros con formulación estabilizada de un punto (`LadrunoBrick ssp`) y barras discretas `CorotTruss` acopladas mediante `LadrunoEmbeddedRebar` con adherencia perfecta.

Métricas de comparación directa con el ensayo experimental (`ExperimentalData.txt`):

- **Calibración con tamaño de elemento de 200 mm (2 particiones)**:
  - Configuración inicial (`stdBrick` lineal): bloqueo por flexión con un elemento en el espesor (+10.3 % / +9.8 % en corte de pico).
  - Configuración seleccionada it1c (`LadrunoBrick ssp` + escala de alternativas `penalty-stiff` + tolerancia cíclica 1e-4):
    - Corte de pico: **+2.0 % / +0.6 %** respecto al ensayo experimental.
    - Error medio de envolvente (backbone): **16.0 %**.
    - Razón de energía disipada (área del ciclo modelo / ensayo): **0.73**.
- **Corrida final con registro en cada nodo de hormigón**:
  - Corte de pico: -0.7 % / +2.2 % vs ensayo experimental.
  - Error medio de envolvente: 16.1 %.
  - Razón de energía disipada: 0.68.
- **Observaciones de respuesta**:
  - Se observa una sobre-resistencia de +20 a 30 % en derivas pequeñas (2 a 14 mm) respecto al ensayo, explicada por la flexibilidad real de la base (deslizamiento de armaduras y penetración de deformaciones en el pedestal), efectos no incorporados en la unión con fijación perfecta.

## 3. Estado de los modelos sólidos SW1-1 y SW02

1. **SW1-1 (`sw1_1_lu_solid_ladruno_embedment`)**:
   - Geometría de 1000 x 2000 x 125 mm con elementos de borde confinados.
   - Discretización con `max_size = 200` y barras 4 veces más refinadas (`bar_refine = 4`).
   - Carga axial constante de 246 kN y 24 puntos de inversión del ensayo experimental (`sw1-1_Test.txt`).
   - Materiales: hormigón `ASDConcrete3D` 9P diferenciado en alma (20.7 MPa) y núcleo confinado (25.0 MPa); acero `Hysteretic`.
2. **SW02 (`sw02_pizarro_solid_ladruno_embedment`)**:
   - Geometría de 3000 x 2550 x 200 mm a escala real, sin elementos de borde.
   - Viga de carga superior rígida de 500 x 900 mm que aplica carga axial de 1800 kN y peso propio real.
   - Protocolo de 46 puntos de inversión experimentales con incrementos de 0.25 mm.
   - Esquema de resolución: `KrylovNewton -maxDim 10` con escala de convergencia `penalty-stiff`.

## 4. Verificaciones de documentación

- Todos los parámetros de entrada se encuentran documentados con su variable exacta (`base_depth`, `hw`, `lw`, `tw`, `k_perfect`, `fcp_conf`, `pscale_c`, `b_h`, `ASDConcrete3D`, etc.).
- Las referencias a modelos shell, frame y carpetas eliminadas fueron depuradas de los archivos de documentación.
- Toda la documentación Markdown del proyecto se encuentra traducida al español, manteniendo la fidelidad técnica con los reportes experimentales originales.
