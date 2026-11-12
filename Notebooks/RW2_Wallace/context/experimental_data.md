# Datos experimentales

| ítem | valor |
|---|---|
| archivo | `../DatosExperimentales/ExperimentalData.csv` |
| ensayo | RW2, Thomsen & Wallace (1995), carga lateral cíclica a 3.66 m con carga axial constante |
| formato | 674 filas de datos, 2 columnas separadas por comas, con encabezado |
| columna 1 | `displacement_m`, desplazamiento superior, **m** (rango -0.0796 a 0.0805) |
| columna 2 | `force_tonf`, fuerza lateral, **tonf** (rango -16.07 a 16.13) |

Conversión empleada por el cuaderno (a mm, kN):

```python
disp_mm  = col1 * 1000
force_kn = col2 * 9.80665
```

Verificación: valor de pico aproximado de 16.1 tonf = 158 kN a cerca de 80 mm (deriva de 2.2 %). El protocolo experimental alcanza 80.46 mm (2.2 % de 3660 mm), coincidiendo con la deriva máxima registrada.
