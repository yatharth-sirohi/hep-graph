// classroom-boot.js — the classroom modes' first-paint half. A classic script in
// <head>, no imports: it must run before the page paints so a projector-theme or
// embedded page never flashes the standard chrome. js/classroom.js (a module) does
// the rest once the app is up. Nothing here throws: storage and URL parsing are
// wrapped, and every failure means "standard theme, full chrome".
//
//   ?theme=projector   the light, high-contrast theme, for this link only
//   ?theme=standard    the standard theme, whatever was remembered
//   (no ?theme=)       the choice remembered by the header's Projector button
//   ?embed=1           minimal chrome for a course page or LMS iframe
(function () {
  var root = document.documentElement;
  var params = null;
  try {
    params = new URLSearchParams(window.location.search);
  } catch (error) {
    params = null;
  }
  var theme = params && params.get('theme');
  if (theme !== 'projector' && theme !== 'standard') {
    theme = null;
    try {
      theme = window.localStorage.getItem('hep-atlas.theme');
    } catch (error) {
      theme = null;
    }
  }
  if (theme === 'projector') root.setAttribute('data-theme', 'projector');
  if (params && params.get('embed') === '1') {
    root.classList.add('is-embed');
    // The timeline stays in an embed only for a route that needs it: an address that
    // names a year or a range, or a local map (whose features have valid years).
    if (params.has('y') || params.has('r') || /^#\/map\//.test(window.location.hash)) {
      root.classList.add('embed-timeline');
    }
  }
}());
