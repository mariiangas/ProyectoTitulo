# Plantilla Memoria UAndes — Overleaf (con logo)

## Cómo usar
1. Sube este ZIP a Overleaf (**New Project → Upload Project**).
2. Para **Times New Roman** exacta, elige **XeLaTeX** como compilador.
3. La portada usa `figuras/Logo Uandes.png` (definido en `\LogoPath` en `main.tex`). Puedes reemplazarlo por otro logo cambiando ese archivo o la ruta.
4. La bibliografía usa **biblatex** (estilo autor-año) con Biber; Overleaf lo maneja automáticamente. En `references.bib`, separa los autores con `and` (no con "y") y usa doble llave `{{...}}` para autores institucionales.
5. Si no hay Profesor Co-Guía, deja el comando vacío: `\newcommand{\ProfesorCoGuia}{}` — la línea desaparece sola de la portada.

## Estructura
- `main.tex` — Documento principal con portada (logo y líneas estilo plantilla oficial), índices, capítulos, tablas/figuras y anexos.
- `references.bib` — Entradas BibTeX de ejemplo.
- `figuras/Logo Uandes.png` — Logo institucional usado en la portada (la carpeta incluye otros logos alternativos).