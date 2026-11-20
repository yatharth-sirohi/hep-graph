// Small reviewed evidence pilots; primary versions and locators are explicit.
// Add a reviewed entry for another result; absence means no evidence card, not no evidence.
// Display strings preserve the distinction between a mass fit and a significance scan.
const higgsReading = {
  context: 'These are the paper’s findings, following the 4 July announcement.',
  expectedLabel: 'Expected with a Standard Model Higgs signal',
  nextQuestion: {
    title: 'Do the two mass measurements agree?',
    description: 'Use the quoted mass fits and uncertainties, with an independent-error approximation. Make a prediction, then reveal the sourced calculation in the Higgs hunt tour.',
    tour: 'higgs-hunt', step: 7, label: 'Compare the Higgs masses',
  },
  interpretation: [
    'Observed significance measures how incompatible the data are with a background-only model at one tested mass, expressed as an equivalent one-sided Gaussian tail. Expected significance is the median sensitivity assuming a Standard Model Higgs signal; it is not another observation.',
    'Neither is the probability that the Higgs exists. A global significance also accounts for searching over many masses; it depends on the search window.',
  ],
  definition: { label: 'CMS §4, printed p. 6 (PDF page 8): local and global p-values', url: 'https://arxiv.org/pdf/1207.7235v1#page=8' },
  conclusion: 'ATLAS and CMS are separate analyses. No joint significance is calculated here. The papers established a new boson compatible with the Higgs; further property measurements followed.',
};
const trails = {
  'result:sno-nc-evidence-2002': {
    experiment:'SNO', paper:'arXiv:nucl-ex/0204008v2 (9 May 2002 revision)',
    context:'Pure-D₂O phase; standard ⁸B spectral shape assumed for the quoted fluxes.',
    measurement:'SNO inferred ⁸B solar-neutrino fluxes from charged-current (CC), neutral-current (NC) and elastic-scattering (ES) signals.',
    observedLabel:'Reported non-electron-flavor significance',
    significance:{ scope:'Reported flavor-transformation evidence', observed:'5.3σ above zero',
      at:'Joint CC/NC/ES fit: νμ + ντ flux = 3.41 ± 0.45 (stat.) +0.48 / −0.45 (syst.) × 10⁶ cm⁻² s⁻¹.',
      note:'The 5.3σ result uses the fitted non-electron component. The CC/NC central-value ratio is not this test statistic.' },
    interpretation:['These are inferred fluxes after accounting for reaction and detector responses, not raw event counts. The fit also uses ES and correlated uncertainties.'],
    channelReader:{
      title:'Compare what the reactions probe',
      intro:'Switch reactions and follow the labeled active flavors. Both reported fluxes remain visible below.',
      assumption:'Standard ⁸B spectral shape; pure-D₂O phase. This reader highlights CC and NC; the paper also fits ES.',
      quantityLabel:'Inferred ⁸B flux', units:'10⁶ cm⁻² s⁻¹',
      unitsDescription:'Millions of neutrinos per square centimetre per second.',
      flavors:[{id:'electron',label:'Electron νₑ'},{id:'muon',label:'Muon νμ'},{id:'tau',label:'Tau ντ'}],
      channels:[
        {id:'cc',label:'Charged current (CC)',reaction:'νₑ + d → p + p + e⁻',probes:['electron'],
          sensitivity:'Only electron neutrinos in this solar-energy measurement.',signal:'An outgoing electron produces light in the detector.',
          flux:{value:'1.76',stat:'+0.06 / −0.05',syst:'±0.09'}},
        {id:'nc',label:'Neutral current (NC)',reaction:'νx + d → p + n + νx',probes:['electron','muon','tau'],
          sensitivity:'x = e, μ or τ: all three active flavors have equal NC sensitivity.',signal:'The neutron is detected via a gamma ray from capture on deuterium.',
          flux:{value:'5.09',stat:'+0.44 / −0.43',syst:'+0.46 / −0.43'}},
      ],
      reactionSource:{label:'Check the reactions and flavor sensitivity',locator:'PDF page 2: reaction definitions and neutron-capture readout.',url:'https://arxiv.org/pdf/nucl-ex/0204008v2#page=2'},
      fluxSource:{label:'Check the reported channel fluxes',locator:'PDF page 4: shape-constrained flux equations below Table II.',url:'https://arxiv.org/pdf/nucl-ex/0204008v2#page=4'},
    },
    evidence:[{label:'Check the fitted non-electron component',locator:'PDF page 5: component equations, 5.3σ passage and Figure 3.',url:'https://arxiv.org/pdf/nucl-ex/0204008v2#page=5',
      supports:'The joint flavor fit and its reported evidence. The nearby shape-unconstrained NC result uses a different assumption.'}],
    conclusion:'The result supports solar-neutrino flavor transformation. It is not a single-energy survival probability or a fit of the lab’s illustrative vacuum parameters.',
    nextQuestion:{title:'What if all arriving active neutrinos were electron flavor?',description:'Predict whether the inferred CC and NC fluxes should agree, then use the existing tour’s sourced comparison.',
      tour:'neutrino-oscillation-story',step:3,label:'Try the SNO flux question'},
  },
  'result:atlas-higgs-observation-2012': {
    ...higgsReading,
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
    ...higgsReading,
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
