"""A scheduled restart cannot end the last reported beam condition by itself."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AFFECTED = [
    'accelerator:fermilab-main-injector', 'beamline:numi', 'experiment:nova',
    'detector:nova-near-detector', 'detector:nova-far-detector',
]


def test_last_reported_beam_state_is_retained_without_claiming_a_restart():
    from hepgraph.atlas.load import DATA_DIR, load_atlas
    from hepgraph.atlas import schema
    from hepgraph.atlas.validate import validate_atlas
    atlas = load_atlas(DATA_DIR)
    for entity_id in AFFECTED:
        record = atlas.get(entity_id)
        last = next(row for row in record['intervals'] if row.get('status') == 'shutdown' and row.get('start') == '2024-07')
        assert last['end'] is None, 'an unconfirmed restart plan must not close the reported shutdown'
        assert 'last reported' in last['note'].lower()
        assert 'not confirmed' in last['note'].lower()
        assert schema.state_at(record, '2026-11', build_date='2026-11-19')['status'] == 'shutdown'
        assert schema.state_at(record, '2023', build_date='2026-11-19')['status'] == 'active'
        plan = next(row for row in record['intervals'] if row.get('kind') == 'run' and row.get('status') == 'planned')
        assert plan['start']['planned'] is True and plan['start']['date'] == '2026-10'
        assert plan['end']['planned'] is True
        assert 'src:currency2-fnal-pac-report-2026-09' in plan['sources']
    errors = [f for f in validate_atlas(atlas, build_date='2026-11-19') if f.level == 'error']
    assert not errors, [(f.rule, f.entity_id, f.message) for f in errors]


def test_rebuilt_nova_remains_explorable_at_the_current_cutoff():
    from hepgraph.atlas.build import build
    from hepgraph.atlas.load import DATA_DIR
    result = build(DATA_DIR, ROOT / 'static/atlas/generated', build_date='2026-11-19', check=True)
    atlas = json.loads(result.files['atlas.json'])
    record = atlas['experiments']['experiment:nova']
    assert record['status'] == 'shutdown'
    assert record['coverage']['validated'] is True
    assert record['coverage']['globe_ready'] is True
    assert any(row[1] == 'experiment:nova' for row in json.loads(result.files['search.json'])['entries'])


@pytest.mark.skipif(not shutil.which('node'), reason='Node is needed for the real browser helper')
def test_unconfirmed_restart_context_respects_precision_history_and_later_reports():
    script = """
      import {unconfirmedRestart} from './static/atlas/js/restart-context.js';
      const shutdown={status:'shutdown',start:'2024-07',end:null};
      const plan={kind:'run',status:'planned',start:{date:'2026-10',planned:true},end:{date:'2027-02',planned:true}};
      const make=rows=>({intervals:rows});
      const at=(rows,date='2026-11-19',year=2026)=>unconfirmedRestart(make(rows),date,{year});
      const base=[shutdown,plan];
      console.log(JSON.stringify({normal:at(base),early:at(base,'2026-10-20'),historical:at(base,'2026-11-19',2023),
       later:at([...base,{status:'active',start:'2026-11-01',end:null}]),
       closed:at([{...shutdown,end:'2026-11-01'},plan]),
       bounded:at([shutdown,{...plan,start:{date:'2026-10',latest:'2026-12',planned:true}}]),
       annual:at([shutdown,{...plan,start:{date:'2026',planned:true}}]),
       day:at([shutdown,{...plan,start:{date:'2026-11-18',planned:true}}]),
       missing:at([]),invalid:at(base,'no-date'),
       range:unconfirmedRestart(make(base),'2026-11-19',{range:[2018,2023]})}));
    """
    result = subprocess.run([shutil.which('node'), '--input-type=module', '-e', script], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['normal']['stateIndex'] == 0 and data['normal']['planIndex'] == 1
    assert data['normal']['start']['date'] == '2026-10'
    assert data['day'] is not None
    assert all(data[key] is None for key in ['early','historical','later','closed','bounded','annual','missing','invalid','range'])
