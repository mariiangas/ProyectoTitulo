"""Archive and physical interpolation invariants; no real solver is launched."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rw2_workflow as rw2


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rw2-workflow-test-')
        self.root = Path(self.temp.name).resolve()
        assert self.root.parent == Path(tempfile.gettempdir()).resolve()
        for filename in (rw2.NAME+'.ipynb', 'rw2_workflow.py'):
            (self.root/filename).write_text('source snapshot\n', encoding='utf-8')
        (self.root/'DatosExperimentales').mkdir()
        (self.root/'DatosExperimentales/ExperimentalData.csv').write_text(
            'displacement_m,force_tonf\n0,0\n0.01,1\n', encoding='utf-8')
        self.ns = dict(lw=1220., hw=3660., tw=102., lbe=200., h_conf=1220.,
                       base_depth=690., base_overhang=355., edge=19.,
                       peaks=[.1], disp_values=[0,.1,.1], time_values=[0,1,1.5],
                       gc=36., pinch_x=.6, pinch_y=.8, n_cyclic=2)

    def tearDown(self):
        assert self.root.parent == Path(tempfile.gettempdir()).resolve()
        self.temp.cleanup()

    def test_new_numbers_and_frozen_inputs(self):
        first = rw2.create_run(self.root, self.ns)
        self.ns['gc'] = 72.
        second = rw2.create_run(self.root, self.ns)
        self.assertEqual(first.name,'wallace_0001')
        self.assertEqual(second.name,'wallace_0002')
        self.assertEqual(rw2.metadata(first)['parameters']['Hormigon']['gc'],36.)
        self.assertEqual(rw2.metadata(second)['parameters']['Hormigon']['gc'],72.)
        self.assertIn('wallace_0001',(self.root/'runs/indice.md').read_text(encoding='utf-8'))
        index = (self.root/'runs/indice.md').read_text(encoding='utf-8')
        self.assertIn('Referencia inicial', index)
        self.assertIn('`Hormigon.gc`: 36.0 → 72.0', index)
        self.assertFalse((first/'fuentes').exists())
        self.assertTrue((first/'resumen.md').exists())
        self.assertFalse((first/'resumen.tex').exists())
        self.assertFalse((first.parent/'ultima_corrida.json').exists())
        self.assertFalse((first.parent/'ultima_completa.json').exists())

    def test_index_compares_consecutive_runs_and_handles_missing_history(self):
        historical = rw2.create_run(self.root, self.ns)
        record = rw2.metadata(historical)
        record['parameters'] = {}
        rw2.write_json(historical/'parametros.json', record)
        rw2.create_run(self.root, self.ns)
        rw2.create_run(self.root, self.ns)
        self.ns.update(gc=72., pinch_x=.7)
        changed = rw2.create_run(self.root, self.ns)
        index = (changed.parent/'indice.md').read_text(encoding='utf-8')
        rows = [line for line in index.splitlines() if line.startswith('| [wallace_')]
        self.assertIn('Comparación no disponible', rows[1])
        self.assertIn('Sin cambios en los parámetros registrados', rows[2])
        self.assertIn('`Hormigon.gc`: 36.0 → 72.0', rows[3])
        self.assertIn('`Acero.pinch_x`: 0.6 → 0.7', rows[3])
        self.assertNotIn('pinch_y', rows[3])
        record = rw2.metadata(changed)
        del record['parameters']['Acero']['pinch_y']
        rw2.write_json(changed/'parametros.json', record)
        rw2.refresh_report(changed)
        index = (changed.parent/'indice.md').read_text(encoding='utf-8')
        self.assertIn('Comparación parcial', index)
        self.assertIn('`Acero.pinch_y`', index)

    def test_global_export_uses_shared_csv_for_new_and_historical_runs(self):
        for historical in (False, True):
            with self.subTest(historical=historical):
                run = rw2.create_run(self.root, self.ns)
                if historical:
                    record = rw2.metadata(run)
                    record['status'] = 'importada_historica'
                    rw2.write_json(run/'parametros.json', record)
                result = SimpleNamespace(run_dir=run, experimental_dir=self.root/'DatosExperimentales',
                                         time=np.array([0., 1.]),
                                         top=np.array([0., 10.]), shear=np.array([0., 9.80665]))
                with patch.object(rw2, 'RunResults', return_value=result), \
                     patch.object(rw2, 'save_figure') as save:
                    rw2.export_global(run, show=False)
                experiment_line = save.call_args.args[1].axes[0].lines[0]
                np.testing.assert_allclose(experiment_line.get_xdata(), [0., 10.])
                np.testing.assert_allclose(experiment_line.get_ydata(), [0., 9.80665])
                self.assertFalse((run/'fuentes').exists())

    def test_latest_selection_uses_run_metadata_without_pointer_files(self):
        complete = rw2.create_run(self.root, self.ns)
        record = rw2.metadata(complete)
        record.update(status='completa', analysis_complete=True)
        rw2.write_json(complete/'parametros.json', record)
        (complete/(rw2.NAME+'.ladruno')).touch()
        partial = rw2.create_run(self.root, self.ns)
        (partial/(rw2.NAME+'.ladruno')).touch()
        self.assertEqual(rw2.select_run(self.root, 'ultima_completa'), complete)
        self.assertEqual(rw2.select_run(self.root, 'ultima'), partial)

    def test_stale_material_values_are_rejected_before_reserving_run(self):
        self.ns['rw2_input_signatures'] = {'materials':rw2.input_signature(self.ns,'materials')}
        self.ns['pinch_x'] = .2
        with self.assertRaisesRegex(ValueError,'materials'):
            rw2.create_run(self.root,self.ns)
        self.assertFalse((self.root/'runs').exists())

    def test_existing_run_cannot_be_executed_again(self):
        run = rw2.create_run(self.root,self.ns)
        record = rw2.metadata(run);record['status']='completa'
        rw2.write_json(run/'parametros.json',record)
        with self.assertRaisesRegex(RuntimeError,'ya fue iniciada'):
            rw2.run_solver(run,Path('does-not-exist.bat'))

    def test_selection_rejects_path_outside_runs(self):
        rw2.create_run(self.root,self.ns)
        with self.assertRaises(ValueError):
            rw2.select_run(self.root,'../../somewhere')

    def test_latest_complete_does_not_silently_select_failed_partial_results(self):
        run=rw2.create_run(self.root,self.ns)
        record=rw2.metadata(run);record['status']='fallida'
        rw2.write_json(run/'parametros.json',record)
        (run/(rw2.NAME+'.ladruno')).touch()
        with self.assertRaises(FileNotFoundError):
            rw2.select_run(self.root,'ultima_completa')
        self.assertEqual(rw2.select_run(self.root,'ultima'),run)

    def test_virtual_gauge_reproduces_affine_displacement_exactly(self):
        run = rw2.create_run(self.root,self.ns)
        xyz=np.array([[0,0,0],[1220,0,0],[1220,102,0],[0,102,0],
                      [0,0,3660],[1220,0,3660],[1220,102,3660],[0,102,3660]],float)
        lines=[f'node {i+1} {x} {y} {z}' for i,(x,y,z) in enumerate(xyz)]
        lines += ['element LadrunoBrick 1 1 2 3 4 5 6 7 8 1 -formulation ssp',
                  'timeSeries Path 1 -values 0 .1 .1 -time 0 1 1.5', 'sp 5 1 1.0']
        (run/(rw2.NAME+'.tcl')).write_text('\n'.join(lines)+'\n')
        displacement=np.zeros((2,8,3));displacement[:,:,2]=.001*xyz[:,2]+.0001*xyz[:,0]
        with h5py.File(run/(rw2.NAME+'.ladruno'),'w') as file:
            stage=file.create_group('MODEL_STAGE[2]')
            for response,data in (('DISPLACEMENT',displacement),('REACTION_FORCE',np.zeros_like(displacement))):
                group=stage.create_group('RESULTS/ON_NODES/'+response)
                group['ID']=np.arange(1,9)[:,None];group['TIME']=[.5,1.];group['DATA']=data
        result=rw2.RunResults(run)
        low=result.at([[610,51,100]],2)
        high=result.at([[610,51,329]],2)
        np.testing.assert_allclose((high-low)/229,.001,rtol=1e-12)
        np.testing.assert_allclose(low[:,0],.161,rtol=1e-12)

    def test_experimental_gage_histories_respect_reported_failure_limits(self):
        import pandas as pd
        data=pd.read_csv(ROOT/'DatosExperimentales/fig_7_32_concrete_history.csv')
        self.assertLessEqual(data[data.curve=='sensor_embebido'].data_point.max(),330)
        self.assertLessEqual(data[data.curve=='LVDT_interpolado'].data_point.max(),515)

    def test_displacement_profiles_extract_test_traces_at_all_story_levels(self):
        import runpy
        import pymupdf
        digitizer = runpy.run_path(str(ROOT/'DatosExperimentales/digitize_rw2_local.py'))
        pdf = ROOT.parents[1]/'Bibliografia/Wallace/Orakcal_Massone_Wallace_2006_PEER-2006-07.pdf'
        with pymupdf.open(pdf) as doc:
            data = digitizer['extract_displacement_profiles'](doc)
        self.assertEqual(len(data), 70)
        for (drift, direction), profile in data.groupby(['nominal_drift_pct', 'direction']):
            self.assertEqual(profile.story.tolist(), [0, 1, 2, 3, 4])
            self.assertEqual(profile.displacement_mm.iloc[0], 0.)
            self.assertTrue(np.all(np.diff(profile.displacement_mm.to_numpy()*direction) > 0))
        top = data[(data.nominal_drift_pct==.25) & (data.direction==1) & (data.story==4)]
        self.assertAlmostEqual(float(top.displacement_mm.iloc[0]), 4.017, places=2)


if __name__=='__main__':
    unittest.main()
