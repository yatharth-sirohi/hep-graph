// Native question links shared by panels and learning views; one tour player.
function visitParams(search) {
  const context = new URLSearchParams(search);
  const params = new URLSearchParams();
  for (const key of ['data', 'embed', 'theme']) if (context.has(key)) params.set(key, context.get(key));
  return params;
}

export function tourStepHref(slug, step, search = '') {
  const params=visitParams(search);params.set('step',String(step));
  return `?${params}#/tour/${slug}`;
}

export function mapStepHref(slug, year, proton, search = '') {
  const params=visitParams(search);params.set('y',String(year));params.set('proton',String(proton));
  return `?${params}#/map/${slug}`;
}

function nativeLearningLink(href, text, patch, navigate, marker) {
  const link = document.createElement('a');
  link.className = 'entity-link';
  link.setAttribute(marker, '');
  link.setAttribute('href', href);
  link.textContent = text;
  // Native activation wins over presenter navigation, except when any key must
  // first dismiss the presenter's black/white screen.
  link.addEventListener('keydown', event => {
    if (event.key !== 'Enter') return;
    const blank = document.getElementById('tour-blank');
    if (!blank || blank.hidden) event.stopPropagation();
  });
  link.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(patch);
  });
  return link;
}

export function createTourStepLink(slug, step, text, navigate) {
  return nativeLearningLink(tourStepHref(slug,step,window.location.search),text,
    {entity:{type:'tour',slug},step},navigate,'data-tour-step-link');
}

export function createMapStepLink(slug, year, proton, text, navigate) {
  return nativeLearningLink(mapStepHref(slug,year,proton,window.location.search),text,
    {entity:{type:'map',slug},year,range:null,proton,levels:null,sel:null},navigate,'data-map-step-link');
}

// Registered once by panels.init. Theme events precede their URL patch and do
// not remount panels/views; update live links without retaining detached nodes.
export function syncTourLinkThemes(event) {
  const theme = event.detail?.theme;
  if (!['projector', 'standard'].includes(theme)) return;
  for (const link of document.querySelectorAll('a[data-tour-step-link], a[data-map-step-link]')) {
    const url = new URL(link.href);
    url.searchParams.set('theme', theme);
    link.setAttribute('href', `${url.search}${url.hash}`);
  }
}
