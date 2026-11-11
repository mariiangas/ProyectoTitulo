# Catálogo de ensayos de muros de hormigón armado para el flujo de trabajo apeGmsh / apeSees

Catálogo de especímenes de muros de hormigón armado modelados en el proyecto. Unidades de análisis: N, mm, MPa. Cada muro cuenta con su modelo numérico sólido en la carpeta `Notebooks/` y sus antecedentes bibliográficos en `Bibliografia/`.

## Especímenes modelados en el proyecto

| id | geometría / sección | tipo de ensayo | datos experimentales | fuente / carpeta | modelo sólido | idoneidad / notas |
|---|---|---|---|---|---|---|
| **RW2** (Thomsen & Wallace 1995; Orakcal et al. 2006) | Rectangular con elementos de borde confinados, 1220 x 3660 x 102 mm, h_w/l_w = 3.0 | Cíclico cuasi-estático en voladizo, carga axial constante de 372.8 kN (0.07 Ag f'c) | Sí (`Notebooks/RW2_Wallace/ExperimentalData.txt`, 674 puntos) | `Bibliografia/Wallace/` (PDF PEER 2006/07 disponible) | `rw2_solid_ladruno_embedment` | Alta: muro esbelto de referencia con datos completos de materiales, geometría y curvas experimentales digitalizadas. |
| **SW1-1** (Zhang 2007; Lu et al. 2015) | Rectangular con elementos de borde confinados, 1000 x 2000 x 125 mm, h_w/l_w = 2.0 | Cíclico cuasi-estático, carga axial constante de 246 kN (0.10 Ag f'c) | Sí (`Notebooks/SW1-1_Lu/sw1-1_Test.txt`, 24 puntos de inversión) | `Bibliografia/Lu/` | `sw1_1_lu_solid_ladruno_embedment` | Alta: muro esbelto con detallamiento dúctil, armadura confinada y protocolo cíclico definido. |
| **SW02** (Pizarro et al. 2025) | Rectangular de baja esbeltez (squat), sin elemento de borde, 3000 x 2550 x 200 mm, h_w/l_w = 0.85 | Cíclico cuasi-estático empotrado-empotrado con carga axial de 1800 kN | Sí (46 puntos de inversión del ensayo experimental) | `Bibliografia/Pizarro/` | `sw02_pizarro_solid_ladruno_embedment` | Alta: muro a escala real gobernado por interacción flexo-cortante y corte diagonal; viga de carga superior rígida. |

## Carpetas de bibliografía

- `Wallace/`: Contiene el reporte completo en PDF: `Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf`.
- `Lu/`: Referencias del espécimen SW1-1 (artículo Lu et al. 2015 y tesis Zhang 2007).
- `Pizarro/`: Referencias del espécimen SW02 (artículo JSE 2025, tesis y planos).
