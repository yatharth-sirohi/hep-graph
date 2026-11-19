"""Evidence readers can reach the existing sourced mass-compatibility exercise."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')


@pytest.mark.skipif(not NODE, reason='Node is required for evidence-registry checks')
def test_both_higgs_trails_reach_the_existing_sourced_mass_question():
    result = subprocess.run([NODE, '--input-type=module', '-e', """
      import {evidenceFor} from './static/atlas/js/result-evidence-data.js';
      console.log(JSON.stringify(['result:atlas-higgs-observation-2012','result:cms-higgs-boson-observation-2012']
        .map(id=>evidenceFor(id).nextQuestion)));
    """], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    destinations = json.loads(result.stdout)
    tour = json.loads((ROOT / 'data/atlas/tours/higgs-hunt.json').read_text())
    for destination in destinations:
        assert destination is not None
        assert destination['tour'] == 'higgs-hunt'
        question = tour['steps'][destination['step'] - 1]['question']
        assert '126.0' in question['prompt'] and '125.3' in question['prompt']
        assert 'independent' in question['answer']
        assert {claim['ref'] for claim in question['claims']} == {
            'result:atlas-higgs-observation-2012', 'result:cms-higgs-boson-observation-2012',
        }
        assert question['calculation']
        assert '0.82' in question['answer']
        assert destination['label'] and destination['description']
