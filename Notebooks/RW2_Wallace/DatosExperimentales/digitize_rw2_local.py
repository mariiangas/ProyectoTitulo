"""Extract published Test traces from the vector PDF; never extract Analysis traces.

Coordinates and drawing indices refer to the SHA256 recorded in provenance.json.
Run only when intentionally regenerating the experimental reference files.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT.parents[1] / "Bibliografia/Wallace/Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf"
OUTPUT = Path(__file__).resolve().parent


def extract_displacement_profiles(doc):
    """Sample the dashed Test traces of Fig. 7.28 at the five story levels."""
    drawings = doc[153].get_drawings()
    # Dashed Test segments span three PDF paths. The solid Analysis paths
    # begin at item 109 of drawing 5 and are excluded from this extraction.
    segments = drawings[3]['items'][7:] + drawings[4]['items'] + drawings[5]['items'][:109]
    traces = []
    for segment in segments:
        assert segment[0] == 'l'
        start, end = segment[1:]
        if not traces or start.y < traces[-1][-1].y - 1:
            traces.append([])
        traces[-1].extend([start, end])
    assert len(traces) == 14
    rows = []
    drifts = (.25, .5, .75, 1., 1.5, 2., 2.5)
    story_y = (317.88, 276.90, 235.92, 194.94, 154.02)
    for trace_index, trace in enumerate(traces):
        direction = 1 if trace_index < 7 else -1
        drift = drifts[trace_index % 7]
        points_xy = np.array([(point.x, point.y) for point in trace])
        points_xy = points_xy[np.argsort(points_xy[:, 1])]
        assert np.isclose(points_xy[0, 1], story_y[-1], atol=.01)
        assert points_xy[-1, 1] >= story_y[0] - 2.6
        for story, y in enumerate(story_y):
            # Linear interpolation bridges only the gaps between printed dashes.
            x = np.interp(y, points_xy[:, 1], points_xy[:, 0])
            displacement = 0. if story == 0 else 160 * (x - 322.62) / (476.76 - 168.48)
            rows.append(dict(nominal_drift_pct=drift, direction=direction, story=story,
                             displacement_mm=displacement,
                             source='geometric_origin' if story == 0 else 'digitized_vector_Test',
                             figure='7.28', pdf_page=154, printed_page=143))
    return pd.DataFrame(rows).sort_values(['nominal_drift_pct', 'direction', 'story'])


def points(drawing):
    values = []
    for item in drawing["items"]:
        if item[0] == "l":
            values.extend([tuple(item[1]), tuple(item[2])])
        elif item[0] == "c":
            a,b,c,d = (np.array(v) for v in item[1:])
            for t in np.linspace(0, 1, 9):
                values.append(tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d))
    return np.array(values, dtype=float)


def extract():
    OUTPUT.mkdir(exist_ok=True)
    doc = pymupdf.open(PDF)
    page = doc[155]
    drawings = page.get_drawings()
    concrete, steel = [], []
    # Full plotting frame spans 0..1220 mm. Marker locations identify measured positions.
    def profile(path_index, marker_indices, x0, x1, y0, slope):
        data = points(drawings[path_index])
        order = np.argsort(data[:, 0]); data = data[order]
        xp = np.array([(drawings[i]["rect"].x0+drawings[i]["rect"].x1)/2 for i in marker_indices])
        # Interpolate/extrapolate across the tiny graphical dash gaps at markers.
        from scipy.interpolate import interp1d
        yp = interp1d(data[:, 0], data[:, 1], fill_value="extrapolate", bounds_error=False)(xp)
        return 1220*(xp-x0)/(x1-x0), (y0-yp)/slope
    for drift, index, markers in ((.5,2,range(3,10)),(1.,10,range(11,18)),(2.,18,range(19,26))):
        x,y=profile(index,markers,176.46,479.88,227.64,(277.8-77.34)/.08)
        concrete += [dict(nominal_drift_pct=drift,direction=1,cycle="not_reported",x_mm=a,strain=b,source="digitized_vector_Test",figure="7.30",pdf_page=156,printed_page=145) for a,b in zip(x,y)]
    for level, yzero, slope, series in (
        ("base",512.7-.01*(512.7-365.04)/.07,(512.7-365.04)/.07,((.5,66,range(67,79)),(1.,79,range(80,92)),(2.,92,range(93,105)))),
        ("primer_nivel",660.3-.0025*(660.3-512.7)/.0175,(660.3-512.7)/.0175,((.5,145,range(146,152)),(1.,152,range(153,159)),(2.,159,range(160,166)),(2.5,182,range(183,189))))):
        for drift,index,markers in series:
            x,y=profile(index,markers,184.92,480.12,yzero,slope)
            steel += [dict(level=level,nominal_drift_pct=drift,direction=1,cycle="not_reported",x_mm=a,strain=b,source="digitized_vector_Test",figure="7.31",pdf_page=156,printed_page=145) for a,b in zip(x,y)]
    pd.DataFrame(concrete).sort_values(["nominal_drift_pct","x_mm"]).to_csv(OUTPUT/"fig_7_30_concrete_strain.csv",index=False)
    pd.DataFrame(steel).sort_values(["level","nominal_drift_pct","x_mm"]).to_csv(OUTPUT/"fig_7_31_steel_strain.csv",index=False)
    history=[]; drawings=doc[154].get_drawings()
    for component,indices,x0,x1,y0,slope in (
        ("rotation",(4,5,6),181.08,481.26,282.06,(383.22-180.9)/.04),
        ("displacement",(16,17,18),176.04,481.2,547.11,(649.38-444.84)/30)):
        for index in indices:
            xy=points(drawings[index])
            history += [dict(component=component,data_point=700*(a-x0)/(x1-x0),value=(y0-b)/slope,source="digitized_vector_Test",figure="7.29",pdf_page=155,printed_page=144) for a,b in xy]
    pd.DataFrame(history).drop_duplicates(["component","data_point"]).sort_values(["component","data_point"]).to_csv(OUTPUT/"fig_7_29_first_story.csv",index=False)
    drawings=doc[156].get_drawings(); history=[]
    for curve,indices,limit in (("sensor_embebido",(3,),330),("LVDT_interpolado",(9,10),515)):
        for index in indices:
            xy=points(drawings[index])
            for a,b in xy:
                record=100+500*(a-187.1964)/(481.2448-187.1964)
                if record<=limit:
                    history.append(dict(curve=curve,data_point=record,strain=(606.493333-b)/((651.24-449.88)/.045),source="digitized_vector_Test",figure="7.32",pdf_page=157,printed_page=146,reliability="compression_only" if curve=="sensor_embebido" else "until_record_515"))
    pd.DataFrame(history).drop_duplicates(["curve","data_point"]).sort_values(["curve","data_point"]).to_csv(OUTPUT/"fig_7_32_concrete_history.csv",index=False)
    drawings=doc[195].get_drawings(); components=[]
    for component,indices,origin,scale in (("flexure",range(5,12),217.86,(314.04-121.68)/40),("shear",range(17,24),432.18,(528.54-335.82)/12)):
        for curve,index in enumerate(indices,1):
            xy=points(drawings[index])
            components += [dict(component=component,curve=curve,point=j,displacement_mm=(a-origin)/scale,load_kN=(164.22-b)/((249.42-79.02)/400),source="digitized_vector_Test",figure="9.3",pdf_page=196,printed_page=186) for j,(a,b) in enumerate(xy)]
    pd.DataFrame(components).to_csv(OUTPUT/"fig_9_3_first_story.csv",index=False)
    # Only series whose plotted path and legend are identifiable; elastic reference excluded.
    drawings=doc[170].get_drawings(); components=[]
    for component,curve,index,x0,scale,y0,yscale in (
        ("flexure","primer_nivel",2,136.68,(284.64-136.68)/10,485.4,(485.4-328.2)/(40*4.4482216153)),
        ("flexure","segundo_nivel",21,136.68,(284.64-136.68)/10,485.4,(485.4-328.2)/(40*4.4482216153)),
        ("shear","primer_nivel_X_corregida",31,352.38,(475.02-352.38)/6,489.36,(489.36-331.68)/(40*4.4482216153)),
        ("shear","primer_nivel_X_original",52,352.38,(475.02-352.38)/6,489.36,(489.36-331.68)/(40*4.4482216153))):
        for a,b in points(drawings[index]):
            components.append(dict(component=component,curve=curve,displacement=(a-x0)/scale,load_kN=(y0-b)/yscale,displacement_unit="Uf/Ufy" if component=="flexure" else "mm",source="digitized_vector_Test",figure="8.3",pdf_page=171,printed_page=160))
    pd.DataFrame(components).drop_duplicates().to_csv(OUTPUT/"fig_8_3_story_components.csv",index=False)
    # Intermediate Test/Analysis traces overlap. Digitize only the explicit Test
    # markers at the top; retain the full original for intermediate-level review.
    extract_displacement_profiles(doc).to_csv(OUTPUT/"fig_7_28_displacement_profiles.csv",index=False)
    provenance=dict(source_pdf=str(PDF.relative_to(ROOT.parents[1])),sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
                    method="Vector coordinates of experimental Test paths, calibrated to printed axes; not original acquisition data.",
                    approximate_graphical_precision=dict(position_mm=1.,strain=0.0001,load_kN=1.,displacement_mm=.1),
                    exclusions=["Analysis traces", "unreliable embedded-gage tensile readings as quantitative targets", "embedded sensor after record 330", "LVDT interpolation after record 515"],
                    nominal_drifts_pct=[.1,.25,.5,.75,1,1.5,1,1.5,2,2.5],
                    profile_7_28_scope="Dashed Test traces sampled at stories 1-4; linear interpolation across dash gaps; geometric origin at story 0.",
                    profile_7_28_extraction=dict(pdf_drawing_indices=[3,4,5],
                        plot_x_limits_pdf=[168.48,476.76], displacement_limits_mm=[-80,80],
                        story_y_pdf=[317.88,276.9,235.92,194.94,154.02],
                        notes="Solid Analysis traces excluded. Top positive 0.25% marker association corrected by tracing the Test path."))
    (OUTPUT/"provenance.json").write_text(json.dumps(provenance,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    images=OUTPUT/'source_figures';images.mkdir(exist_ok=True)
    for name,page_number,clip in (("fig_7_28",154,(110,80,490,370)),("fig_8_3",171,(95,305,545,550)),
                                  ("fig_7_23",148,(105,70,520,375)),("fig_7_24",149,(105,70,520,375))):
        doc[page_number-1].get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(clip)).save(images/(name+'.png'))
    for p in sorted(OUTPUT.glob('*.csv')):
        print(p.name,len(pd.read_csv(p)))


if __name__=="__main__":
    extract()
