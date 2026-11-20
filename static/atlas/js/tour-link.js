// Native question links shared by panels and learning views; one tour player.
export function tourStepHref(slug, step, search = '') {
  const context = new URLSearchParams(search);
  const params = new URLSearchParams();
  for (const key of ['data', 'embed', 'theme']) if (context.has(key)) params.set(key, context.get(key));
  params.set('step', String(step));
  return `?${params}#/tour/${slug}`;
}

export function createTourStepLink(slug, step, text, navigate) {
  const link = document.createElement('a');
  link.className = 'entity-link';
  link.setAttribute('data-tour-step-link', '');
  link.setAttribute('href', tourStepHref(slug, step, window.location.search));
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
    navigate({ entity: { type: 'tour', slug }, step });
  });
  return link;
}

// Registered once by panels.init. Theme events precede their URL patch and do
// not remount panels/views; update live links without retaining detached nodes.
export function syncTourLinkThemes(event) {
  const theme = event.detail?.theme;
  if (!['projector', 'standard'].includes(theme)) return;
  for (const link of document.querySelectorAll('a[data-tour-step-link]')) {
    const url = new URL(link.href);
    url.searchParams.set('theme', theme);
    link.setAttribute('href', `${url.search}${url.hash}`);
  }
}
