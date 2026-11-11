# Cuadernos de validación — índice de modelos

Modelos numéricos de especímenes de muros de hormigón armado (RC) con ensayos cíclicos publicados, construidos con apeGmsh / apeSees y ejecutados con el fork Ladruno de OpenSees. Este índice describe únicamente las definiciones de los modelos sólidos (sin resultados). Unidades: N, mm, MPa.

## Carpetas

| carpeta | espécimen | cuadernos | parámetros |
|---|---|---|---|
| `RW2_Wallace/` | RW2, Thomsen & Wallace (1995): rectangular, elementos de borde confinados, h_w/l_w = 3.0 | `rw2_solid_ladruno_embedment` | `RW2_Wallace/README.md` |
| `SW1-1_Lu/` | SW1-1, Zhang (2007) / Lu et al. (2015): rectangular, elementos de borde confinados, h_w/l_w = 2.0 | `sw1_1_lu_solid_ladruno_embedment` | `SW1-1_Lu/README.md` |
| `SW02_Pizarro/` | SW02, Pizarro et al. (ETH Zurich, 2025): muro bajo (squat), sin elemento de borde, h_w/l_w = 0.85, empotrado-empotrado | `sw02_pizarro_solid_ladruno_embedment` | `SW02_Pizarro/README.md` |

Cada carpeta de muro contiene una guía `<name>.md` y una carpeta de ejecución `<name>/` (deck `<name>.tcl`, registro de ejecución y resultados `.ladruno`). En `RW2_Wallace/`, la carpeta `context/` contiene las fuentes, geometría y armaduras, materiales y supuestos detrás de cada valor.

## Familia de modelos sólidos

| ítem | modelo sólido |
|---|---|
| cuaderno | `<name>_solid_ladruno_embedment` |
| modelo | `ndm 3`, `ndf 3` |
| elemento de muro | `LadrunoBrick -formulation ssp` |
| sección | - (volumen continuo) |
| hormigón | `ASDConcrete3D` (preajuste STKO 9P) |
| acero | `Hysteretic` en barras `CorotTruss` |
| barra - hormigón | `LadrunoEmbeddedRebar`, adherencia perfecta |
| corte | continuo 3D |
| fundación / viga de carga | hexaedros con `ElasticIsotropic` |
| discretización | hexaedros de 200 mm, uno a través del espesor; barras 4 veces más refinadas |
| apoyos | base de fundación, caras laterales y cara superior expuesta fijas |
| carga axial | tracción uniforme sobre la cara superior |
| procesos | 2 rangos MPI (`OpenSeesMP`) |
| numberer / system | `ParallelRCM` / `Mumps` |
| algoritmo | `KrylovNewton -maxDim 10` + escala de alternativas (`penalty-stiff` ladder) |
| prueba de convergencia | `NormDispIncr` (etapa de gravedad en SW02: `EnergyIncr`) |

Común a todos los modelos: `constraints Transformation`, `analysis Static`; etapa de gravedad con un patrón `Linear` (peso propio + carga axial), `LoadControl` en 10 incrementos, luego `loadConst`; etapa cíclica con `sp` u_x en los nodos de control siguiendo una serie `Path` de los puntos de inversión del ensayo (pseudo-tiempo proporcional al desplazamiento recorrido, punto de retención posterior a t = 1), `LoadControl` con un incremento de desplazamiento fijo; registrador Ladruno de desplazamientos nodales y reacciones. El corte basal corresponde a la suma de las reacciones en x de los nodos con desplazamiento impuesto.

## Regla para los valores de entrada

Cada valor reportado en los documentos de ensayo (geometría, barras, ensayos de materiales, carga axial, historial de carga) se toma directamente de ellos; los valores no reportados conservan los valores calibrados de los modelos base de STKO. El archivo `README.md` de cada muro lista cada parámetro del modelo, leídos desde los cuadernos y sus decks; `context/` detalla la fuente de cada valor.
