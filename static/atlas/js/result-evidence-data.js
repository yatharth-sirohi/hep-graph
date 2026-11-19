// Editorial evidence pilot, checked against the explicit July 2012 paper versions.
// Add a reviewed entry for another result; absence means no evidence card, not no evidence.
// Display strings preserve the distinction between a mass fit and a significance scan.
const trails = {
  'result:atlas-higgs-observation-2012': {
    experiment: 'ATLAS', paper: 'arXiv:1207.7214v1 (31 July 2012)',
    measurement: 'ATLAS reconstructed decay products in 7 and 8 TeV proton–proton collisions. Excesses in two-photon and four-lepton invariant masses, with other channels, supported a new neutral boson compatible with a Standard Model Higgs.',
    mass: '126.0 ± 0.4 (stat.) ± 0.4 (sys.) GeV, fitted from γγ and ZZ → 4ℓ.',
    significance: { scope:'Local significance', observed:'5.9σ', expected:'4.9σ', at:'Mass hypothesis: 126.5 GeV (distinct from the fitted mass).',
      note:'Table 7 gives an intermediate 6.0σ observed / 4.9σ expected. Section 9.2 reduces the observed value to 5.9σ after photon/electron energy-scale and resolution uncertainties. It reports about 5.1σ globally over 110–600 GeV.' },
    evidence: [
      { label:'See the measured excess', locator:'Figure 4, printed p. 10 (PDF page 11)', url:'https://arxiv.org/pdf/1207.7214v1#page=11',
        supports:'Diphoton mass distribution and residuals above the fitted background; weighted and unweighted panels are labeled.' },
      { label:'Check the observed and expected significance', locator:'§9.2, printed p. 18 (PDF page 19); Table 7 on preceding page', url:'https://arxiv.org/pdf/1207.7214v1#page=19',
        supports:'The passage distinguishing the intermediate 6.0σ from the final 5.9σ, and the expected 4.9σ.' },
      { label:'Check the mass measurement', locator:'§9.3 and Figure 9, printed p. 19 (PDF page 20)', url:'https://arxiv.org/pdf/1207.7214v1#page=20',
        supports:'Mass fit and uncertainties; Figure 9 distinguishes observed from signal-expected local p-values.' },
    ],
    companion: { slug:'cms-higgs-boson-observation-2012', label:'Read CMS’s evidence trail' },
  },
  'result:cms-higgs-boson-observation-2012': {
    experiment:'CMS', paper:'arXiv:1207.7235v1 (31 July 2012)',
    measurement:'CMS searched five decay modes in 7 and 8 TeV proton–proton collisions. The clearest mass excesses were in two photons and four leptons; the significance below uses all five modes.',
    mass:'125.3 ± 0.4 (stat.) ± 0.5 (syst.) GeV, fitted from γγ and ZZ.',
    significance:{ scope:'Local significance', observed:'5.0σ', expected:'5.8σ', at:'Mass hypothesis: 125.5 GeV (distinct from the fitted mass).',
      note:'Table 6’s last row combines CMS decay modes and CMS’s 7 and 8 TeV data. It does not combine CMS with ATLAS.' },
    evidence:[
      { label:'See the measured excess', locator:'Figure 3, printed p. 11 (PDF page 13)', url:'https://arxiv.org/pdf/1207.7235v1#page=13',
        supports:'Weighted diphoton mass distribution, signal/background fits and an unweighted inset.' },
      { label:'Check the observed and expected significance', locator:'§7.1 and Table 6, printed p. 25 (PDF page 27)', url:'https://arxiv.org/pdf/1207.7235v1#page=27',
        supports:'The five-mode row gives 5.8σ expected and 5.0σ observed, in separately labeled columns.' },
      { label:'Check the mass measurement', locator:'Abstract, PDF page 1; §7.2, printed p. 27 (PDF page 29)', url:'https://arxiv.org/pdf/1207.7235v1#page=1',
        supports:'The mass fit, with statistical and systematic uncertainties stated separately.' },
    ],
    companion:{ slug:'atlas-higgs-observation-2012', label:'Read ATLAS’s evidence trail' },
  },
};
export function evidenceFor(resultId) {
  return Object.prototype.hasOwnProperty.call(trails,resultId) ? trails[resultId] : null;
}
