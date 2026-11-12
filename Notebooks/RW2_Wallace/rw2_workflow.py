"""Run archives and postprocessing for the RW2 solid notebook (N, mm, MPa).

Importing this module does not create a run or launch OpenSees.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

NAME = "rw2_solid_ladruno_embedment"
NOMINAL_DRIFTS = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 1.0, 1.5, 2.0, 2.5]
PARAMETER_GROUPS = {
    "Hormigon": "ec nu ft fc0 fcr gt gc pscale_t pscale_c fcp_unconf ecp_unconf fcp_conf ecp_conf concrete_implex",
    "Acero": "es b_h fy3 fu3 eu3 s2_3 fy2 fu2 eu2 s2_2 pinch_x pinch_y steel_damage1 steel_damage2 steel_beta steel_e2",
    "Modelacion": "max_size brick bar_refine k_perfect record_all record_local nparts base_e",
    "Carga": "p_axial gamma_c",
    "Analisis": "d_step n_cyclic n_gravity gravity_tol gravity_max_iter cyclic_tol cyclic_max_iter krylov_max_dim strategy_name",
    "Medicion_local": "lvdt_z0_mm lvdt_length_mm steel_base_z_mm steel_story_z_mm concrete_gage_z_mm concrete_gage_length_mm rotation_height_mm story_height_mm shear_alpha strain_reference profile_cycle",
}
PHASE_KEYS = {
    "geometry": "lw hw tw lbe h_conf max_size base_overhang base_depth p_axial gamma_c",
    "reinforcement": "lw hw tw edge db3 db2 dbw be_step web_step hoop_step anchor_depth h_conf k_perfect",
    "mesh": "max_size bar_refine nparts",
    "materials": PARAMETER_GROUPS["Hormigon"] + " " + PARAMETER_GROUPS["Acero"] + " base_e brick",
}


def input_signature(namespace, phase):
    values = {key: plain(namespace[key]) for key in PHASE_KEYS[phase].split() if key in namespace}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def now():
    return datetime.now(ZoneInfo("America/Santiago")).isoformat(timespec="seconds")


def plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    return value


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(plain(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def metadata(run_dir):
    return json.loads((Path(run_dir) / "parametros.json").read_text(encoding="utf-8"))


def reserve_run(notebook_dir):
    root = Path(notebook_dir) / "runs"
    root.mkdir(exist_ok=True)
    number = max([int(p.name.split("_")[-1]) for p in root.glob("wallace_*") if p.is_dir() and p.name.split("_")[-1].isdigit()] or [0]) + 1
    while True:
        run_dir = root / f"wallace_{number:04d}"
        try:
            run_dir.mkdir()
            break
        except FileExistsError:
            number += 1
    for folder in ("datos", "figuras"):
        (run_dir / folder).mkdir()
    return run_dir


def create_run(notebook_dir, namespace, notes=""):
    """Freeze inputs at deck generation; never overwrite an older run."""
    notebook_dir = Path(notebook_dir)
    signatures = namespace.get("rw2_input_signatures", {})
    for phase, signature in signatures.items():
        if signature != input_signature(namespace, phase):
            raise ValueError(f"Las entradas de {phase} cambiaron despues de construir esa parte. Reejecuta sus celdas antes de generar el Tcl.")
    run_dir = reserve_run(notebook_dir)
    parameters = {group: {key: plain(namespace[key]) for key in names.split() if key in namespace}
                  for group, names in PARAMETER_GROUPS.items()}
    protocol = {key: plain(namespace[key]) for key in ("peaks", "disp_values", "time_values")}
    protocol["nominal_drifts_pct"] = plain(namespace.get("nominal_drifts_pct", NOMINAL_DRIFTS))
    configuration = {key: plain(namespace[key]) for key in ("lw", "hw", "tw", "lbe", "h_conf", "base_depth", "base_overhang", "edge")}
    record = dict(schema_version=1, run_id=run_dir.name, created=now(), status="configurando",
                  notes=notes, parameter_origin="valores congelados al generar el Tcl", parameters=parameters,
                  protocol=protocol, model_reference=configuration, analysis_complete=False,
                  python=sys.executable, solver=str(namespace.get("opensees_mp", "")),
                  launcher=str(namespace.get("launcher", "")), notebook_dir=str(notebook_dir.resolve()))
    write_json(run_dir / "parametros.json", record)
    refresh_report(run_dir)
    return run_dir


def parse_deck(path):
    text = Path(path).read_text(encoding="utf-8")
    nodes, bricks, steel = {}, [], []
    for line in text.splitlines():
        tokens = line.split()
        if tokens[:1] == ["node"] and len(tokens) >= 5:
            nodes[int(tokens[1])] = [float(x) for x in tokens[2:5]]
        elif tokens[:2] == ["element", "LadrunoBrick"]:
            bricks.append({"tag": int(tokens[2]), "nodes": [int(x) for x in tokens[3:11]], "material": int(tokens[11])})
        elif len(tokens) > 6 and tokens[:1] == ["element"] and tokens[1].lower() == "corottruss":
            steel.append({"tag": int(tokens[2]), "nodes": [int(x) for x in tokens[3:5]], "area_mm2": float(tokens[5]), "material": int(tokens[6])})
    for element in bricks + steel:
        xyz = np.array([nodes[n] for n in element["nodes"]])
        element["center"] = xyz.mean(axis=0).tolist()
        element["low"] = xyz.min(axis=0).tolist()
        element["high"] = xyz.max(axis=0).tolist()
    path_line = next(line for line in text.splitlines() if line.startswith("timeSeries Path "))
    values, times = path_line.split("-values", 1)[1].split("-time", 1)
    protocol = {"disp_values": [float(x) for x in values.split()], "time_values": [float(x) for x in times.split()]}
    return dict(text=text, nodes=nodes, bricks=bricks, steel=steel, protocol=protocol)


def seal_run(run_dir, notebook_dir):
    """Add passive local recorders using the emitted OpenSees element tags."""
    run_dir, notebook_dir = Path(run_dir), Path(notebook_dir)
    record = metadata(run_dir)
    deck_path = run_dir / (NAME + ".tcl")
    model = parse_deck(deck_path)
    local_parameters = record["parameters"]["Medicion_local"]
    selected_steel = []
    for element in model["steel"]:
        low, high, center = np.array(element["low"]), np.array(element["high"]), np.array(element["center"])
        vertical = high[2] - low[2] > 1e-6 and np.linalg.norm(high[:2] - low[:2]) < 1e-5
        levels = [label for label, z in (("base", local_parameters["steel_base_z_mm"]), ("primer_nivel", local_parameters["steel_story_z_mm"]))
                  if vertical and low[2] <= z < high[2]]
        if levels or (not vertical and 0 < center[2] < 1220 and (abs(center[0] - 610) < 110 or center[0] < 110 or center[0] > 1110)):
            element["levels"] = levels
            selected_steel.append(element)
    selected_bricks = [e for e in model["bricks"] if e["center"][2] >= 0 and e["center"][2] <= 1220]
    layout = dict(steel=selected_steel, concrete=selected_bricks, tensor_order=["xx", "yy", "zz", "xy", "yz", "xz"],
                  steel_order=["stress_MPa", "strain"], damage_order=["damage_tension_max", "damage_compression_max"],
                  measurement=local_parameters)
    lines = ["# RW2: baseline after gravity, before cyclic loading", "set _rw2_baseline [open {baseline_nodes.out} w]",
             "foreach _rw2_n [getNodeTags] {puts $_rw2_baseline \"$_rw2_n [nodeDisp $_rw2_n 1] [nodeDisp $_rw2_n 2] [nodeDisp $_rw2_n 3]\"}",
             "close $_rw2_baseline"]
    if record["parameters"]["Modelacion"].get("record_local", True):
        steel_tags = " ".join(str(e["tag"]) for e in selected_steel)
        concrete_tags = " ".join(str(e["tag"]) for e in selected_bricks)
        lines += ['set _rw2_steel_base [open {baseline_steel.out} w]',
                  f'foreach _rw2_e {{{steel_tags}}} {{puts $_rw2_steel_base "$_rw2_e [eleResponse $_rw2_e material stressStrain]"}}',
                  'close $_rw2_steel_base']
        lines.append(f"recorder Element -file {{local_steel_stress_strain.out}} -time -precision 16 -ele {steel_tags} material stressStrain")
        gp_count = 1 if record["parameters"]["Modelacion"]["brick"] in ("ssp", "uri") else 8
        layout["gauss_points_recorded"] = gp_count
        for gp in range(1, gp_count + 1):
            for token in ("stress", "strain", "damage"):
                lines.append(f"recorder Element -file {{local_concrete_{token}_gp{gp}.out}} -time -precision 16 -ele {concrete_tags} material {gp} {token}")
    marker = "set _apesees_rungs"
    position = model["text"].find(marker, model["text"].find("# === Stage: cyclic ==="))
    if position < 0:
        raise ValueError("No se encontro el inicio ciclico del Tcl: no se modifico el deck.")
    deck_path.write_text(model["text"][:position] + "\n".join(lines) + "\n" + model["text"][position:], encoding="utf-8")
    write_json(run_dir / "registradores_locales.json", layout)
    record["resolved_material_commands"] = [line for line in model["text"].splitlines() if line.startswith(("nDMaterial ", "uniaxialMaterial "))]
    record['analysis_commands'] = [line for line in model['text'].splitlines() if line.startswith(('constraints ', 'numberer ', 'system ', 'test ', 'algorithm ', 'integrator ', 'analysis ', 'set _apesees_rungs'))]
    record["deck_sha256"] = digest(deck_path)
    record['status'] = 'preparada'
    notebook_dir = Path(record["notebook_dir"])
    sources = [notebook_dir / (NAME + ".ipynb"), notebook_dir / "rw2_workflow.py"]
    sources.extend(p for p in (notebook_dir / "DatosExperimentales").rglob("*") if p.is_file())
    record["source_hashes"] = {str(p.relative_to(notebook_dir)): digest(p) for p in sources}
    record["source_snapshot_available"] = False
    write_json(run_dir / "parametros.json", record)
    refresh_report(run_dir)


def validate_response(run_dir, expected=None):
    run_dir = Path(run_dir)
    paths = list(run_dir.glob(NAME + "*.ladruno"))
    counts = []
    for path in paths:
        with h5py.File(path, "r") as file:
            for name in file:
                if name.startswith("MODEL_STAGE") and "RESULTS/ON_NODES/DISPLACEMENT/DATA" in file[name]:
                    data = file[name + "/RESULTS/ON_NODES/DISPLACEMENT/DATA"]
                    if data.shape[0] and not np.isfinite(data[-1]).all():
                        raise ValueError("La respuesta final contiene NaN/Inf")
                    counts.append(int(data.shape[0]))
    return bool(counts) and (expected is None or max(counts) >= expected), counts


def run_solver(run_dir, launcher, nparts=1):
    run_dir = Path(run_dir)
    record = metadata(run_dir)
    if nparts != 1:
        raise ValueError("Las barras embebidas requieren nparts=1 en esta version.")
    if record["status"] != "preparada" or list(run_dir.glob("*.ladruno")):
        raise RuntimeError("Esta corrida ya fue iniciada. Genera un deck nuevo para obtener otro numero.")
    deck = run_dir / (NAME + ".tcl")
    if digest(deck) != record["deck_sha256"]:
        raise RuntimeError("El Tcl cambio despues de congelar los parametros. Genera otra corrida.")
    log_path = run_dir / "analisis.log"
    record.update(status="ejecutando", started=now())
    write_json(run_dir / "parametros.json", record)
    started, printed, process = time.monotonic(), 0, None
    interrupted, launch_error, failure = False, None, False
    print(f"{run_dir.name}: {deck}", flush=True)
    try:
        with log_path.open("x", encoding="utf-8") as log:
            process = subprocess.Popen([os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(launcher), str(deck)],
                                       cwd=run_dir, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            record["pid"] = process.pid
            write_json(run_dir / "parametros.json", record)
            try:
                while True:
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        pass
                    finished = process.poll() is not None
                    text = log_path.read_text(encoding="utf-8", errors="replace")
                    progress = [line for line in text.splitlines() if "APEGMSH_PROGRESS" in line]
                    for line in progress[printed:]:
                        print(f"[{(time.monotonic()-started)/60:.1f} min] {line}", flush=True)
                    printed = len(progress)
                    failure = any(token in text for token in ("FAILED", "ERROR", "FATAL", "while executing"))
                    if failure or finished:
                        break
            finally:
                if process.poll() is None:
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
                    process.wait(timeout=30)
    except KeyboardInterrupt:
        interrupted = True
        raise
    except Exception as error:
        launch_error = str(error)
        raise
    finally:
        text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        n = record["parameters"]["Analisis"]["n_cyclic"]
        terminal = f"APEGMSH_PROGRESS i={n} n={n} " in text
        try:
            valid, counts = validate_response(run_dir, n)
        except (OSError, ValueError) as error:
            valid, counts = False, []
            record["artifact_error"] = str(error)
        progress = re.findall(r"APEGMSH_PROGRESS i=(\d+) n=(\d+) t=([^\s]+)", text)
        final_time = float(progress[-1][2]) if progress else 0.0
        complete = bool(process and process.returncode == 0 and not failure and terminal and valid and final_time >= 1-1e-6 and not interrupted and launch_error is None)
        record.update(status="completa" if complete else "interrumpida" if interrupted else "fallida", finished=now(),
                      elapsed_seconds=time.monotonic()-started, return_code=process.returncode if process else None,
                      terminal_progress=terminal, recorded_frames=counts, analysis_complete=complete, launch_error=launch_error)
        record["last_progress"] = progress[-1] if progress else None
        write_json(run_dir / "parametros.json", record)
        refresh_report(run_dir)
    print("return code:", record["return_code"], "| estado:", record["status"])
    if not record["analysis_complete"]:
        raise RuntimeError(f"Corrida {record['status']}; revisar {log_path}")
    return record


def select_run(notebook_dir, run_id="ultima_completa"):
    root = Path(notebook_dir) / "runs"
    if run_id in ("ultima_completa", "ultima"):
        candidates = []
        for p in sorted(root.glob('wallace_*')):
            if not any(p.glob('*.ladruno')) or not (p/'parametros.json').exists():
                continue
            m=metadata(p)
            if run_id=='ultima' or m.get('analysis_complete') or (m.get('status')=='importada_historica' and m.get('artifact_complete')):
                candidates.append(p)
        if candidates:
            return candidates[-1]
        raise FileNotFoundError("No hay una corrida completa disponible. Para revisar una parcial usa su identificador o 'ultima'.")
    candidate = (root / run_id).resolve()
    if candidate.parent != root.resolve() or not (candidate / "parametros.json").is_file():
        raise ValueError(f"Corrida desconocida: {run_id}")
    return candidate


def import_existing(notebook_dir):
    """Preserve the existing output without claiming its unknown launch settings."""
    notebook_dir = Path(notebook_dir)
    source = notebook_dir / NAME
    if not (source / (NAME + ".ladruno")).exists():
        return None
    root = notebook_dir / "runs"
    if root.exists():
        for manifest in root.glob("wallace_*/parametros.json"):
            if json.loads(manifest.read_text(encoding="utf-8")).get("imported_from") == str(source.resolve()):
                return manifest.parent
    run_dir = reserve_run(notebook_dir)
    for path in source.iterdir():
        if path.is_file():
            shutil.copy2(path, run_dir / path.name)
    log = run_dir / (NAME + "_run.log")
    if log.exists():
        shutil.copy2(log, run_dir / "analisis.log")
    model = parse_deck(run_dir / (NAME + ".tcl"))
    protocol = model["protocol"]
    protocol["nominal_drifts_pct"] = NOMINAL_DRIFTS
    text = log.read_text(errors="replace") if log.exists() else ""
    progress = re.findall(r"APEGMSH_PROGRESS i=(\d+) n=(\d+) t=([^\s]+)", text)
    valid, counts = validate_response(run_dir)
    terminal = bool(progress and progress[-1][0] == progress[-1][1])
    record = dict(schema_version=1, run_id=run_dir.name, created=now(), status="importada_historica",
                  imported_from=str(source.resolve()), analysis_complete=False, artifact_complete=terminal and valid,
                  parameter_origin="Solo comandos del Tcl archivado; no existia captura de entradas ni codigo de retorno.",
                  parameters={}, protocol=protocol, model_reference=dict(lw=1220., hw=3660., tw=102., edge=19.),
                  resolved_material_commands=[line for line in model["text"].splitlines() if line.startswith(("nDMaterial ", "uniaxialMaterial "))],
                  recorded_frames=counts, terminal_progress=terminal, return_code=None,
                  notebook_dir=str(notebook_dir.resolve()), notes="Archivo anterior conservado. No se atribuyen los parametros actuales del notebook a esta corrida.")
    for filename in (NAME + ".h5", NAME + ".geometry.h5"):
        if (notebook_dir / filename).exists():
            shutil.copy2(notebook_dir / filename, run_dir / filename)
    record["deck_sha256"] = digest(run_dir / (NAME + ".tcl"))
    write_json(run_dir / "parametros.json", record)
    refresh_report(run_dir)
    return run_dir


def _fmt(value):
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def _parameter_changes(previous, current):
    """Compare saved input parameters, preserving missing historical values."""
    if previous is None:
        return "Referencia inicial"
    if not previous or not current:
        return "Comparación no disponible"
    before = {(group, key): value for group, values in previous.items() for key, value in values.items()}
    after = {(group, key): value for group, values in current.items() for key, value in values.items()}
    changes = []
    for group, key in sorted(before.keys() & after.keys()):
        if before[group, key] != after[group, key]:
            old = json.dumps(before[group, key], ensure_ascii=False).replace("|", r"\|")
            new = json.dumps(after[group, key], ensure_ascii=False).replace("|", r"\|")
            changes.append(f"`{group}.{key}`: {old} → {new}")
    missing = sorted(before.keys() ^ after.keys())
    if missing:
        changes.append("Comparación parcial; falta registro en alguna corrida para " +
                       ", ".join(f"`{group}.{key}`" for group, key in missing))
    return "<br>".join(changes) or "Sin cambios en los parámetros registrados"


def refresh_report(run_dir):
    run_dir = Path(run_dir)
    record = metadata(run_dir)
    lines = [f"# {record['run_id']} — RW2", "", f"- Fecha: {record['created']}", f"- Estado: **{record['status']}**",
             f"- Analisis completo verificado: **{record.get('analysis_complete', False)}**",
             f"- Procedencia de parametros: {record['parameter_origin']}", f"- Notas: {record.get('notes', '')}", "",
             "[Parametros completos](parametros.json) · [Tcl ejecutado](" + NAME + ".tcl) · [Registro](analisis.log)", ""]
    deck_path = run_dir / (NAME + ".tcl")
    if deck_path.exists():
        deck = deck_path.read_text(encoding="utf-8")
        analysis_types = sorted(set(re.findall(r"^\s*analysis\s+(\w+)", deck, re.M)))
        lines += ["## Tipo de análisis", ""]
        if analysis_types == ["Static"] and "# === Stage: cyclic ===" in deck:
            lines += [
                "**Estático no lineal cíclico (cuasiestático).**",
                "",
                "Primero se aplica la carga gravitacional y axial, que se mantiene constante "
                "durante la etapa lateral. Después se impone el historial cíclico de "
                "desplazamientos en la parte superior del muro mediante restricciones `sp` "
                "y una serie `Path`.",
                "",
                "Ambas etapas utilizan `analysis Static`. El avance del historial se realiza "
                "con `integrator LoadControl`; la demanda lateral se prescribe como desplazamiento. "
                "El tiempo registrado corresponde al pseudotiempo del análisis.",
                "",
            ]
        else:
            lines += ["Tipos declarados en el Tcl: " + ", ".join(analysis_types) + ".", ""]
    for path in sorted(run_dir.glob('*.ladruno')) + sorted(run_dir.glob('*.h5')):
        lines.append(f"- [Modelo/respuesta: {path.name}]({path.name})")
    lines.append('')
    for group, values in record.get("parameters", {}).items():
        lines += [f"## {group}", "", "| Variable | Valor utilizado |", "|---|---|"]
        for key, value in values.items():
            lines.append(f"| `{key}` | {_fmt(value)} |")
        lines.append("")
    lines += ["## Datos y figuras", ""]
    for directory in ("datos", "figuras"):
        for path in sorted((run_dir / directory).glob("*")):
            lines.append(f"- [{path.name}]({directory}/{path.name})")
            if path.suffix == ".png":
                lines += [f"![{path.stem}]({directory}/{path.name})", ""]
    if record.get("local_notes"):
        lines += ["", "## Alcance de las comparaciones locales", ""] + [f"- {s}" for s in record["local_notes"]]
    if record.get('global_metrics') or record.get('comparison_metrics'):
        lines += ['', '## Indicadores descriptivos', '', '```json', json.dumps({k:record[k] for k in ('global_metrics','comparison_metrics') if k in record}, indent=2, ensure_ascii=False), '```']
    if record.get('analysis_commands'):
        lines += ['', '## Comandos de solucion emitidos', '', '```tcl']+record['analysis_commands']+['```']
    (run_dir / "resumen.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    index = ["# Historial RW2", "", "Cambios de los parámetros registrados respecto de la corrida anterior, en orden de numeración.", "",
             "| Corrida | Fecha | Estado | Cambios respecto de la anterior |", "|---|---|---|---|"]
    previous = None
    manifests = sorted(run_dir.parent.glob("wallace_*/parametros.json"),
                       key=lambda path: int(path.parent.name.removeprefix("wallace_")))
    for manifest in manifests:
        m = json.loads(manifest.read_text(encoding="utf-8"))
        p = m.get("parameters", {})
        changes = _parameter_changes(previous, p)
        index.append(f"| [{m['run_id']}]({m['run_id']}/resumen.md) | {m['created']} | {m['status']} | {changes} |")
        previous = p
    (run_dir.parent / "indice.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return run_dir / "resumen.md"


class RunResults:
    """Read the archived mesh/results, independent from live notebook variables."""
    def __init__(self, run_dir):
        self.run_dir = Path(run_dir)
        self.meta = metadata(run_dir)
        self.model = parse_deck(self.run_dir / (NAME + ".tcl"))
        self.protocol = self.meta["protocol"]
        self.config = dict(lvdt_z0_mm=0., lvdt_length_mm=229., steel_base_z_mm=25., steel_story_z_mm=950.,
                           concrete_gage_z_mm=92., concrete_gage_length_mm=83., rotation_height_mm=760., story_height_mm=914.5,
                           shear_alpha=0.67, strain_reference="total", profile_cycle=1)
        self.config.update(self.meta.get("parameters", {}).get("Medicion_local", {}))
        paths = sorted(self.run_dir.glob(NAME + "*.ladruno"))
        if len(paths) != 1:
            raise ValueError("Este flujo RW2 espera una sola particion .ladruno.")
        self.result_path = paths[0]
        with h5py.File(paths[0], "r") as file:
            stage = next(file[k] for k in file if k.startswith("MODEL_STAGE") and "RESULTS/ON_NODES/DISPLACEMENT" in file[k])
            group = stage["RESULTS/ON_NODES/DISPLACEMENT"]
            self.ids = np.array(group["ID"]).reshape(-1).astype(int)
            self.time = np.array(group["TIME"]).reshape(-1)
            self.displacement = np.array(group["DATA"])
            reaction = stage["RESULTS/ON_NODES/REACTION_FORCE"]
            reaction_ids = np.array(reaction["ID"]).reshape(-1).astype(int)
            self.reaction = np.array(reaction["DATA"])
            reaction_time = np.array(reaction["TIME"]).reshape(-1)
        if not np.array_equal(self.time, reaction_time):
            raise ValueError("Desplazamientos y reacciones no tienen los mismos pasos.")
        self.columns = {n: i for i, n in enumerate(self.ids)}
        self.coordinates = np.array([self.model["nodes"][n] for n in self.ids])
        top_ids = sorted(set(int(n) for n in re.findall(r"^\s*sp (\d+) 1 ", self.model["text"], re.M)))
        self.top = self.displacement[:, [self.columns[n] for n in top_ids], 0].mean(axis=1)
        rc = {n: i for i, n in enumerate(reaction_ids)}
        self.shear = self.reaction[:, [rc[n] for n in top_ids], 0].sum(axis=1) / 1000.
        self.baseline = np.zeros((len(self.ids), 3))
        baseline_path = self.run_dir / "baseline_nodes.out"
        if baseline_path.exists():
            for row in np.loadtxt(baseline_path, ndmin=2):
                if int(row[0]) in self.columns:
                    self.baseline[self.columns[int(row[0])]] = row[1:4]
        self.experimental_dir = Path(self.meta["notebook_dir"]) / "DatosExperimentales"

    def at(self, points, component):
        points = np.atleast_2d(points)
        values = self.displacement[:, :, component]
        if self.config["strain_reference"] == "after_gravity":
            if not (self.run_dir / "baseline_nodes.out").exists():
                raise ValueError("Esta corrida no tiene estado de gravedad guardado.")
            values = values - self.baseline[:, component]
        result = []
        for point in points:
            candidates = [e for e in self.model["bricks"] if np.all(point >= np.array(e["low"])-1e-6) and np.all(point <= np.array(e["high"])+1e-6)
                          and (point[2] < -1e-6 or e["center"][2] >= 0)]
            if not candidates:
                raise ValueError(f"Punto fuera de la malla: {point}")
            element = min(candidates, key=lambda e: np.prod(np.array(e["high"])-e["low"]))
            try:
                columns = [self.columns[n] for n in element["nodes"]]
            except KeyError as error:
                raise ValueError("La corrida solo registra nodos de carga; se requiere record_all o record_local.") from error
            xyz = np.array([self.model["nodes"][n] for n in element["nodes"]])
            fraction = (point - element["low"]) / (np.array(element["high"])-element["low"])
            weights = np.prod(np.where(np.isclose(xyz, element["high"]), fraction, 1-fraction), axis=1)
            result.append(values[:, columns] @ weights)
        return np.array(result).T

    def nominal_peak_time(self, drift, direction=1, occurrence=0):
        levels = self.protocol.get("nominal_drifts_pct", NOMINAL_DRIFTS)
        groups = [i for i, level in enumerate(levels) if np.isclose(level, drift)]
        if not groups:
            raise ValueError(f"Deriva nominal no definida: {drift}")
        cycle=int(self.config['profile_cycle'])
        if cycle not in (1,2):
            raise ValueError('profile_cycle debe ser 1 o 2')
        reversal = groups[occurrence]*4 + 2*(cycle-1) + (0 if direction > 0 else 1)
        t = self.protocol["time_values"][reversal+1]
        if t > self.time[-1] + 1e-10:
            raise ValueError(f"La corrida no alcanzo {drift}% nominal.")
        return t

    def sample(self, values, t):
        return np.array([np.interp(t, self.time, column) for column in np.asarray(values).reshape(len(self.time), -1).T])


def save_figure(run_dir, figure, name):
    figure.text(.995, .005, Path(run_dir).name, ha='right', va='bottom', fontsize=8, color='.35')
    for suffix in ("png", "pdf"):
        figure.savefig(Path(run_dir) / "figuras" / f"{name}.{suffix}", dpi=180, bbox_inches="tight")


def export_global(run_dir, show=True):
    result = RunResults(run_dir)
    data = pd.DataFrame(dict(pseudo_time=result.time, displacement_mm=result.top, shear_kN=result.shear))
    data.to_csv(result.run_dir / "datos" / "respuesta_global.csv", index=False)
    experiment_path = result.experimental_dir / "ExperimentalData.csv"
    experiment = pd.read_csv(experiment_path)[["displacement_m", "force_tonf"]].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(experiment[:, 0]*1000, experiment[:, 1]*9.80665, "k--", lw=1, label="Ensayo")
    ax.plot(result.top, result.shear, lw=1, label=result.run_dir.name)
    ax.set(xlabel="Desplazamiento superior corregido por pedestal (mm)", ylabel="Corte basal (kN)", title=f"RW2 — {result.run_dir.name}")
    ax.grid(True); ax.legend()
    save_figure(run_dir, fig, "01_respuesta_global")
    if show:
        plt.show()
    else:
        plt.close(fig)
    m = metadata(run_dir)
    m["global_metrics"] = dict(points=len(data), min_shear_kN=float(result.shear.min()), max_shear_kN=float(result.shear.max()),
                               min_displacement_mm=float(result.top.min()), max_displacement_mm=float(result.top.max()))
    write_json(Path(run_dir) / "parametros.json", m)
    refresh_report(run_dir)
    return result


def plot_locations(result, show=True):
    experiment = pd.read_csv(result.experimental_dir / "fig_7_30_concrete_strain.csv")
    xs = sorted(experiment[experiment.nominal_drift_pct==experiment.nominal_drift_pct.min()].x_mm.unique())
    fig, ax = plt.subplots(figsize=(8, 4))
    for x in xs:
        ax.plot([x, x], [result.config["lvdt_z0_mm"], result.config["lvdt_z0_mm"]+result.config["lvdt_length_mm"]], "o-", ms=3)
    ax.plot([0, 1220, 1220, 0, 0], [0, 0, 1050, 1050, 0], "k-", lw=.8)
    ax.axhline(result.config["steel_base_z_mm"], color="tab:red", ls="--", label="Acero: nivel base")
    ax.axhline(result.config["steel_story_z_mm"], color="tab:green", ls="--", label="Acero: primer nivel")
    ax.set(xlabel="x a lo largo del muro (mm)", ylabel="z sobre el pedestal (mm)", title="Sensores virtuales — PEER Fig. 7.10(a)")
    ax.grid(True); ax.legend()
    save_figure(result.run_dir, fig, "02_ubicacion_sensores")
    plt.show() if show else plt.close(fig)


def compare_concrete(result, show=True):
    experiment = pd.read_csv(result.experimental_dir / "fig_7_30_concrete_strain.csv")
    xs = np.sort(experiment[experiment.nominal_drift_pct==experiment.nominal_drift_pct.min()].x_mm.unique())
    z0, length = result.config["lvdt_z0_mm"], result.config["lvdt_length_mm"]
    low = np.array([[x, 0, z0] for x in xs]); high = low + [0, 0, length]
    strains = (result.at(high, 2)-result.at(low, 2))/length
    pd.DataFrame(strains, columns=[f"epsilon_z_x{x:.3f}_mm" for x in xs]).assign(pseudo_time=result.time).to_csv(result.run_dir / "datos" / "historias_lvdt_virtuales.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5)); rows = []
    for color, (drift, group) in zip(("tab:blue", "tab:orange", "tab:green"), experiment.groupby("nominal_drift_pct")):
        group = group.sort_values("x_mm")
        try:
            predicted = result.sample(strains, result.nominal_peak_time(drift))
        except ValueError as error:
            print(error); continue
        ax.plot(group.x_mm, group.strain, "o--", color=color, label=f"Ensayo {drift:g}% nominal")
        ax.plot(xs, predicted, "-", color=color, label=f"Modelo {drift:g}% nominal")
        for x, value in zip(xs, predicted):
            observed = float(np.interp(x, group.x_mm, group.strain))
            rows.append(dict(nominal_drift_pct=drift, x_mm=x, model_strain=value, experimental_strain=observed, difference=value-observed))
    ax.set(xlabel="x a lo largo del muro (mm)", ylabel="Deformacion vertical media (mm/mm)", title=f"Fig. 7.30 — LVDT virtual {length:g} mm — {result.run_dir.name}")
    ax.grid(True); ax.legend(ncol=2)
    pd.DataFrame(rows).to_csv(result.run_dir / "datos" / "comparacion_7_30.csv", index=False)
    if rows:
        errors = np.array([row['difference'] for row in rows])
        record = metadata(result.run_dir)
        record.setdefault('comparison_metrics', {})['fig_7_30'] = dict(
            points=len(rows), mean_absolute_strain_error=float(np.abs(errors).mean()),
            rms_strain_error=float(np.sqrt(np.mean(errors**2))),
            scope='Descriptive errors against digitized LVDT profiles, subject to gauge-location assumptions.')
        write_json(result.run_dir / 'parametros.json', record)
    save_figure(result.run_dir, fig, "03_fig_7_30_hormigon")
    plt.show() if show else plt.close(fig)
    return strains, xs


def compare_steel(result, show=True):
    experiment = pd.read_csv(result.experimental_dir / "fig_7_31_steel_strain.csv")
    raw = result.run_dir / "local_steel_stress_strain.out"
    layout_path = result.run_dir / "registradores_locales.json"
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    numerical = None
    if raw.exists() and layout_path.exists():
        layout = json.loads(layout_path.read_text(encoding="utf-8"))["steel"]
        raw_data = np.loadtxt(raw, ndmin=2)
        if raw_data.shape[1] != 1+2*len(layout):
            raise ValueError("Columnas del registrador de acero incompatibles con su manifiesto.")
        numerical = raw_data
        steel_baseline = {}
        if result.config['strain_reference']=='after_gravity':
            baseline_path=result.run_dir/'baseline_steel.out'
            if not baseline_path.exists():
                raise ValueError('La corrida no tiene deformaciones de acero al final de gravedad.')
            steel_baseline={int(row[0]):row[2] for row in np.loadtxt(baseline_path,ndmin=2)}
    for ax, level in zip(axes, ("base", "primer_nivel")):
        for color, (drift, group) in zip(("tab:blue", "tab:orange", "tab:green", "tab:red"), experiment[experiment.level==level].groupby("nominal_drift_pct")):
            group = group.sort_values("x_mm")
            ax.plot(group.x_mm, group.strain, "o--", color=color, label=f"Ensayo {drift:g}%")
            if numerical is not None:
                try:
                    t = result.nominal_peak_time(drift)
                except ValueError:
                    continue
                selected = [(i, e) for i, e in enumerate(layout) if level in e["levels"]]
                profile = pd.DataFrame([dict(x_mm=e["center"][0], strain=np.interp(t, numerical[:, 0], numerical[:, 2+2*i])-steel_baseline.get(e['tag'],0.)) for i, e in selected]).groupby("x_mm", as_index=False).mean()
                ax.plot(profile.x_mm, profile.strain, color=color, label=f"Modelo {drift:g}%")
                for row in profile.to_dict("records"):
                    rows.append(dict(level=level, nominal_drift_pct=drift, **row))
        ax.set(ylabel="Deformacion axial del acero (mm/mm)", title=level.replace("_", " "))
        ax.grid(True); ax.legend(ncol=2)
        if numerical is None:
            ax.text(.5, .97, "Corrida historica: no registro respuestas internas del acero", transform=ax.transAxes, ha="center", va="top", fontsize=9)
    axes[-1].set_xlabel("x a lo largo del muro (mm)")
    fig.suptitle(f"Fig. 7.31 — {result.run_dir.name}"); fig.tight_layout()
    if rows:
        pd.DataFrame(rows).to_csv(result.run_dir / "datos" / "comparacion_7_31.csv", index=False)
    save_figure(result.run_dir, fig, "04_fig_7_31_acero")
    plt.show() if show else plt.close(fig)
    return numerical is not None


def kinematics(result):
    h, width = result.config["story_height_mm"], 1220.
    values = {}
    for story in (1, 2):
        z0, z1 = (story-1)*h, story*h
        corners = [[0, 0, z0], [width, 0, z0], [0, 0, z1], [width, 0, z1]]
        ux, uz = result.at(corners, 0), result.at(corners, 2)
        # Diagonal lengths of the deformed virtual X; geometric average story distortion.
        xdiag1, zdiag1 = width+ux[:, 3]-ux[:, 0], h+uz[:, 3]-uz[:, 0]
        xdiag2, zdiag2 = width+ux[:, 1]-ux[:, 2], -h+uz[:, 1]-uz[:, 2]
        d1, d2 = np.hypot(xdiag1, zdiag1), np.hypot(xdiag2, zdiag2)
        original = (np.sqrt(np.maximum(d1*d1-h*h, 0))-np.sqrt(np.maximum(d2*d2-h*h, 0)))/2
        theta = ((uz[:, 0]-uz[:, 2])-(uz[:, 1]-uz[:, 3]))/width
        # Same rotation sign as positive lateral drift: theta=(uz_left-uz_right)/width.
        theta = -theta
        flexure = result.config["shear_alpha"]*theta*h
        corrected = original + (.5-result.config["shear_alpha"])*theta*h
        total = (ux[:, 2]+ux[:, 3]-ux[:, 0]-ux[:, 1])/2
        values[story] = dict(rotation=theta, flexure=flexure, shear=corrected, shear_original=original, total=total)
    return values


def compare_kinematics(result, show=True):
    values = kinematics(result)
    out = dict(pseudo_time=result.time, load_kN=result.shear)
    for story, series in values.items():
        out.update({f"story_{story}_{name}": data for name, data in series.items()})
    pd.DataFrame(out).to_csv(result.run_dir / "datos" / "cinematica_por_nivel.csv", index=False)
    exp = pd.read_csv(result.experimental_dir / "fig_9_3_first_story.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, component, label in zip(axes, ("flexure", "shear"), ("Flexion", "Corte")):
        subset = exp[exp.component==component]
        for _, group in subset.groupby("curve", sort=False):
            ax.plot(group.displacement_mm, group.load_kN, "k--", lw=.7)
        ax.plot([], [], "k--", label="Ensayo digitalizado — Fig. 9.3")
        ax.plot(values[1][component], result.shear, lw=.9, label=result.run_dir.name)
        ax.set(xlabel=f"Desplazamiento de {label.lower()} (mm)", ylabel="Carga lateral (kN)", title=label)
        ax.grid(True); ax.legend(fontsize=8)
    save_figure(result.run_dir, fig, "07_fig_9_3_flexion_corte")
    plt.show() if show else plt.close(fig)
    # Reference Fig. 8.3: normalized flexure uses each response's own first-yield value.
    ref = pd.read_csv(result.experimental_dir / "fig_8_3_story_components.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for (component, curve), group in ref.groupby(["component", "curve"], sort=False):
        axes[0 if component=="flexure" else 1].plot(group.displacement, group.load_kN, "o--", ms=3, label=f"Ensayo: {curve}")
    for story in (1, 2):
        axes[1].plot(values[story]["shear"], result.shear, lw=.7, label=f"Modelo nivel {story}")
    axes[0].set(xlabel="Flexion normalizada U_f/U_fy del ensayo", ylabel="Carga lateral (kN)", title="Fig. 8.3(a): referencia experimental")
    axes[1].set(xlabel="Desplazamiento de corte (mm)", ylabel="Carga lateral (kN)", title="Fig. 8.3(b): sensores X virtuales")
    for ax in axes:
        ax.grid(True); ax.legend(fontsize=7)
    save_figure(result.run_dir, fig, "08_fig_8_3_componentes")
    plt.show() if show else plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for row, story in enumerate((1,2)):
        source=result.experimental_dir/'source_figures'/f"fig_7_{23 if story==1 else 24}.png"
        axes[row,0].imshow(plt.imread(source)); axes[row,0].axis('off')
        axes[row,0].set_title(f'Figura original 7.{23 if story==1 else 24}(a): revisar rotulos de unidades', fontsize=9)
        # The publication has inconsistent dimensional labels; keep a separate,
        # correctly labeled numerical panel rather than rescaling by assumption.
        axes[row,1].plot(values[story]['shear']/result.config['story_height_mm'], result.shear, lw=.7)
        axes[row,1].set(xlabel='Distorsion de corte corregida (rad)', ylabel='Carga lateral (kN)', title=f'Modelo: nivel {story}')
        axes[row,1].grid(True)
    fig.tight_layout()
    save_figure(result.run_dir, fig, '08b_fig_7_23_7_24_corte_por_nivel')
    plt.show() if show else plt.close(fig)
    return values


def compare_histories(result, show=True):
    exp = pd.read_csv(result.experimental_dir / "fig_7_29_first_story.csv")
    values = kinematics(result)
    hrot = result.config["rotation_height_mm"]
    uz = result.at([[0, 0, hrot], [1220, 0, hrot], [0, 0, 0], [1220, 0, 0]], 2)
    rotation = ((uz[:, 0]-uz[:, 2])-(uz[:, 1]-uz[:, 3]))/1220.
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))
    # A publication's data-point number is not an OpenSees increment or physical time.
    # Align reversal events, never equate record indices with the solver pseudo-time.
    from scipy.signal import find_peaks
    reference = exp[exp.component=="rotation"].sort_values("data_point")
    grid = np.linspace(reference.data_point.min(), reference.data_point.max(), 4000)
    y = np.interp(grid, reference.data_point, reference.value)
    peaks, _ = find_peaks(np.abs(y), prominence=0.00012, distance=35)
    candidates = grid[peaks]
    signs = np.sign(y[peaks])
    selected, previous = [], -1
    for value in result.protocol["disp_values"][1:41]:
        matches = [i for i in range(previous+1, len(candidates)) if signs[i]==np.sign(value)]
        if not matches:
            break
        previous = matches[0]; selected.append(candidates[previous])
    aligned = len(selected)==40
    if aligned:
        model_x = np.interp(result.time, [0]+result.protocol["time_values"][1:41], [reference.data_point.min()]+selected)
        xlabel = "Numero de registro del informe (modelo alineado aproximadamente por reversiones)"
        pd.DataFrame(dict(reversal=np.arange(1, 41), pseudo_time=result.protocol["time_values"][1:41], publication_data_point=selected)).to_csv(result.run_dir / "datos" / "alineacion_reversiones.csv", index=False)
    else:
        model_x = None
        xlabel = "Numero de registro del informe; modelo en panel separado por pseudo-tiempo"
    for ax, component, numerical in zip(axes, ("rotation", "displacement"), (rotation, values[1]["flexure"])):
        group = exp[exp.component==component]
        ax.plot(group.data_point, group.value, "k--", lw=.9, label="Ensayo digitalizado")
        if aligned:
            ax.plot(model_x, numerical, lw=.8, label="Modelo, alineacion por reversiones")
        ax.set(ylabel="Rotacion (rad)" if component=="rotation" else "Desplazamiento de flexion (mm)")
        ax.grid(True); ax.legend(fontsize=8)
    axes[-1].set_xlabel(xlabel)
    save_figure(result.run_dir, fig, "06_fig_7_29_historias")
    plt.show() if show else plt.close(fig)
    if not aligned:
        fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        axes[0].plot(result.time, rotation); axes[1].plot(result.time, values[1]["flexure"])
        axes[0].set_ylabel("Rotacion (rad)"); axes[1].set(ylabel="Flexion primer nivel (mm)", xlabel="Pseudo-tiempo del modelo")
        save_figure(result.run_dir, fig, "06b_historias_modelo_sin_alinear")
        plt.show() if show else plt.close(fig)
    concrete = pd.read_csv(result.experimental_dir / "fig_7_32_concrete_history.csv")
    z, length = result.config["concrete_gage_z_mm"], result.config["concrete_gage_length_mm"]
    local = (result.at([[25, 0, z+length/2]], 2)-result.at([[25, 0, z-length/2]], 2))[:, 0]/length
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for curve, group in concrete.groupby("curve", sort=False):
        ax.plot(group.data_point, group.strain, lw=.9, label=f"Ensayo: {curve}")
    if aligned:
        ax.plot(model_x, local, lw=.9, label="Modelo: sensor virtual 83 mm; alineacion aproximada")
    ax.axvline(330, color="tab:red", ls=":", label="Falla del sensor embebido")
    ax.axvline(515, color=".5", ls=":", label="Limite de confiabilidad LVDT")
    ax.set(xlabel="Numero de registro del informe", ylabel="Deformacion vertical (mm/mm)", title="Fig. 7.32 — borde sur; x=25 mm como supuesto de ubicacion")
    ax.grid(True); ax.legend(fontsize=8)
    save_figure(result.run_dir, fig, "05_fig_7_32_historia_hormigon")
    plt.show() if show else plt.close(fig)
    pd.DataFrame(dict(pseudo_time=result.time, concrete_gage_strain=local, rotation_760mm=rotation)).to_csv(result.run_dir / "datos" / "historias_locales.csv", index=False)
    return aligned


def compare_profiles(result, show=True):
    exp = pd.read_csv(result.experimental_dir / "fig_7_28_displacement_profiles.csv")
    zs = np.array([0., 914.5, 1829., 2743.5, 3660.])
    total = result.at([[610, 0, z] for z in zs], 0)
    components = kinematics(result)
    correction1 = components[1]["shear"]
    correction2 = components[2]["shear"]
    # Same elastic second-story shear stiffness extrapolation as the report, explicitly labeled.
    correction = np.column_stack([np.zeros(len(result.time)), correction1, correction1+correction2, correction1+2*correction2, correction1+3*correction2])
    flexural = total-total[:, :1]-correction
    fig, ax = plt.subplots(figsize=(10, 7)); rows=[]
    drifts = sorted(exp.nominal_drift_pct.unique())
    colors = dict(zip(drifts, plt.get_cmap('tab10').colors))
    for (drift, direction), group in exp.groupby(["nominal_drift_pct", "direction"], sort=False):
        group = group.sort_values('story')
        color = colors[drift]
        ax.plot(group.displacement_mm, group.story, 'o--', color=color, ms=4, lw=1.2)
        try:
            predicted = result.sample(flexural, result.nominal_peak_time(drift, direction))
        except ValueError:
            continue
        ax.plot(predicted, np.arange(5), color=color, lw=1.2)
        observed = group.set_index('story').displacement_mm
        rows.extend(dict(nominal_drift_pct=drift, direction=direction, story=int(i),
                         model_displacement_mm=value, experimental_displacement_mm=observed.get(i, np.nan))
                    for i,value in enumerate(predicted))
    handles = [Line2D([], [], color=colors[drift], label=f'{drift:g}% nominal') for drift in drifts]
    handles += [Line2D([], [], color='black', marker='o', ls='--', label='Ensayo digitalizado'),
                Line2D([], [], color='black', label='Modelo')]
    ax.set(xlabel="Desplazamiento lateral de flexion (mm)", ylabel="Nivel", title="Fig. 7.28 — corte superior extrapolado desde segundo nivel")
    ax.set_yticks(np.arange(5))
    ax.grid(True); ax.legend(handles=handles, ncol=3, fontsize=8)
    fig.tight_layout()
    pd.DataFrame(rows).to_csv(result.run_dir / "datos" / "comparacion_7_28.csv", index=False)
    save_figure(result.run_dir, fig, "09_fig_7_28_perfiles")
    plt.show() if show else plt.close(fig)


def export_internal(result, show=True):
    """Export all selected steel/continuum histories, with physical IDs and units."""
    path = result.run_dir / "registradores_locales.json"
    if not path.exists():
        return False
    layout = json.loads(path.read_text(encoding="utf-8"))
    raw_files = list(result.run_dir.glob("local_*.out"))
    for raw in raw_files:
        data = np.loadtxt(raw, ndmin=2)
        if "steel" in raw.name:
            elements, labels = layout["steel"], ["stress_MPa", "strain"]
        else:
            elements = layout["concrete"]
            labels = layout["damage_order"] if "damage" in raw.name else [f"{v}_{'MPa' if 'stress' in raw.name else 'strain'}" for v in layout["tensor_order"]]
        expected = 1+len(elements)*len(labels)
        if data.shape[1] != expected:
            raise ValueError(f"{raw.name}: {data.shape[1]} columnas, se esperaban {expected}")
        columns = ["pseudo_time"] + [f"element_{e['tag']}_{label}" for e in elements for label in labels]
        pd.DataFrame(data, columns=columns).to_csv(result.run_dir / "datos" / (raw.stem+".csv"), index=False)
    # Material loops and damage are model interpretation, not measured wall stresses/damage.
    raw = result.run_dir / "local_steel_stress_strain.out"
    if raw.exists():
        data = np.loadtxt(raw, ndmin=2)
        fig, ax = plt.subplots(figsize=(7, 5))
        selected = [(i,e) for i,e in enumerate(layout["steel"]) if "base" in e["levels"]]
        for i,e in selected[:1] + selected[-1:]:
            ax.plot(data[:, 2+2*i], data[:, 1+2*i], lw=.8, label=f"Barra {e['tag']} x={e['center'][0]:.1f}")
        ax.set(xlabel="Deformacion axial (mm/mm)", ylabel="Tension axial (MPa)", title="Acero: respuesta interna del modelo")
        ax.grid(True); ax.legend()
        save_figure(result.run_dir, fig, "10_acero_tension_deformacion")
        plt.show() if show else plt.close(fig)
    stress_path = result.run_dir / 'local_concrete_stress_gp1.out'
    strain_path = result.run_dir / 'local_concrete_strain_gp1.out'
    damage_path = result.run_dir / 'local_concrete_damage_gp1.out'
    if stress_path.exists() and strain_path.exists():
        stress, strain = np.loadtxt(stress_path, ndmin=2), np.loadtxt(strain_path, ndmin=2)
        fig, ax = plt.subplots(figsize=(7, 5))
        for i in (0, len(layout['concrete'])-1):
            element = layout['concrete'][i]
            ax.plot(strain[:, 3+6*i], stress[:, 3+6*i], lw=.8, label=f"Elemento {element['tag']}")
        ax.set(xlabel='Deformacion vertical en GP1 (mm/mm)', ylabel='Tension vertical (MPa)', title='Hormigon: respuesta interna del modelo')
        ax.grid(True); ax.legend()
        save_figure(result.run_dir, fig, '11_hormigon_tension_deformacion')
        plt.show() if show else plt.close(fig)
    if damage_path.exists():
        damage = np.loadtxt(damage_path, ndmin=2)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(damage[:, 0], damage[:, 1::2].max(axis=1), label='Maximo dano de traccion en elementos registrados')
        ax.plot(damage[:, 0], damage[:, 2::2].max(axis=1), label='Maximo dano de compresion en elementos registrados')
        ax.set(xlabel='Pseudo-tiempo del modelo', ylabel='Indice de dano (adimensional)', title='Hormigon: interpretacion numerica, sin referencia experimental de dano')
        ax.grid(True); ax.legend(fontsize=8)
        save_figure(result.run_dir, fig, '12_dano_hormigon')
        plt.show() if show else plt.close(fig)
    return bool(raw_files)


def export_all(run_dir, show=False):
    result = export_global(run_dir, show=show)
    plot_locations(result, show=show)
    compare_concrete(result, show=show)
    steel_available = compare_steel(result, show=show)
    aligned = compare_histories(result, show=show)
    compare_kinematics(result, show=show)
    compare_profiles(result, show=show)
    export_internal(result, show=show)
    record = metadata(run_dir)
    record["postprocessed"] = now()
    record['postprocessing_configuration'] = result.config
    record['postprocessing_experimental_source_hashes'] = {
        str(p.relative_to(result.experimental_dir)):digest(p)
        for p in result.experimental_dir.rglob('*') if p.is_file()}
    code_path=Path(__file__).resolve()
    code_hash=digest(code_path)
    record['postprocessing_code'] = {
        'sha256': code_hash,
        'current_file': str(Path('..') / '..' / code_path.name),
        'snapshot_available': False,
    }
    record["local_notes"] = [
        "Datos experimentales digitalizados de los trazos Test del informe PEER 2006/07; no son archivos originales del ensayo.",
        "Las derivas nominales se asignan por bloque del protocolo publicado, no dividiendo el desplazamiento corregido por la altura.",
        "El protocolo actual coincide con la columna (b) de la Tabla 7.3: movimiento del pedestal descontado, corte incluido.",
        "Fig. 7.30: promedio sobre 229 mm, inicio z=0 mm como supuesto configurable; interpolacion trilineal en la malla archivada.",
        "Los perfiles experimentales no identifican el numero de ciclo; la seleccion numerica usa profile_cycle, guardado en la configuracion de postproceso.",
        "Fig. 7.32: x=25 mm supuesto del borde sur; centro z=92 mm, longitud 83 mm; traccion del sensor embebido no confiable, falla en registro 330.",
        "La separacion X usa alfa=0.67; en segundo nivel se muestra una estimacion corregida numerica, mientras el ensayo no disponia de WPs verticales para corregirlo.",
        "Fig. 8.3(a) conserva solo la referencia experimental normalizada: no se inventa U_fy del ensayo para superponer unidades incompatibles.",
        "Fig. 9.3: los trazos experimentales son ciclicos; las predicciones del informe eran monotonicas y no se incorporan como datos experimentales.",
        "Acero interno disponible: " + str(steel_available),
        "Historias alineadas aproximadamente por reversiones: " + str(aligned) + "; no se evalua error punto a punto de historias sin sincronizacion original.",
        "Los mapas/indices de dano constituyen interpretacion numerica; no equivalen a una medicion experimental de dano ni ancho de fisura.",
    ]
    write_json(Path(run_dir) / "parametros.json", record)
    refresh_report(run_dir)
    print(f"Exportacion: {Path(run_dir)/'resumen.md'}")
    return result
