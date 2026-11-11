# Bibliografía — Base de datos de ensayos de muros de hormigón armado (APA 7)

Referencias de los ensayos y publicaciones correspondientes a los modelos del proyecto, agrupadas por carpeta. Cada sección detalla los documentos disponibles localmente y las fuentes de calibración para los modelos de OpenSees.

---

## [Wallace](Wallace/) — Muro rectangular RW2 (Thomsen & Wallace 1995)

- Orakcal, K., Massone, L. M., & Wallace, J. W. (2006). *Analytical modeling of reinforced concrete walls for predicting flexural and coupled–shear-flexural responses* (PEER Report 2006/07). Pacific Earthquake Engineering Research Center, University of California, Berkeley.
  - Documento local disponible: `Wallace/Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf`.
  - Contenido: Capítulo 7 con geometría, disposición de barras, propiedades de materiales (Tablas 7.1 y 7.2) y curvas de respuesta del espécimen RW2.
- Thomsen, J. H., IV, & Wallace, J. W. (1995). *Displacement-based design of reinforced concrete structural walls: An experimental investigation of walls with rectangular and T-shaped cross-sections* (Report No. CU/CEE-95-06). Clarkson University.
- Thomsen, J. H., IV, & Wallace, J. W. (2004). Displacement-based design of slender reinforced concrete structural walls—Experimental verification. *Journal of Structural Engineering, 130*(4), 618–630. https://doi.org/10.1061/(ASCE)0733-9445(2004)130:4(618)

## [Lu](Lu/) — Muro rectangular esbelto SW1-1 (Zhang 2007 / Lu et al. 2015)

- Lu, X., Xie, L., Guan, H., Huang, Y., & Lu, X. Z. (2015). A shear wall element based on the composite truss model. *Journal of Earthquake Engineering, 19*(7), 1105–1128. https://doi.org/10.1080/13632469.2015.1037402
  - Contenido: Geometría del muro SW1-1 (Fig. 7a), propiedades mecánicas de hormigón y armaduras, e historial cíclico.
- Zhang, B. (2007). *Experimental study on seismic behavior of reinforced concrete shear walls with different aspect ratios* [Tesis de maestría, Tongji University].
  - Contenido: Registro experimental original de ensayo cíclico utilizado en el modelo de validación (`sw1-1_Test.txt`).

## [Pizarro](Pizarro/) — Muro de baja esbeltez SW02 (Pizarro et al. 2025)

- Pizarro Pohl, P., Kovarbasic, V., & Stojadinovic, B. (2025). Experimental and numerical evaluation of squat reinforced concrete walls. *Journal of Structural Engineering, 151*(4), 04025011. https://doi.org/10.1061/JSENDH.STENG-13421
  - Contenido: Geometría a escala real (3000 x 2550 x 200 mm), ensayos de probetas de hormigón y cupones de acero, plano de armado y datos de ensayo cíclico con carga axial de 1800 kN.
