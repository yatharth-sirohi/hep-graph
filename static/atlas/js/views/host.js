// host.js — the frame every Atlas view is drawn in (see registry.js for the
// contract). It owns what is the same for all of them: the full-stage page (the way
// the local map's route takes over #atlas-main), a heading, a back control, the
// "Inputs and method" disclosure, a polite status line, and the error and loading
// states. It loads a view's module only when its route is opened.
//
//   const views = createViewHost({ main, atlas, index, loader, navigate });
//   views.show(state)   state.entity is { type: 'view', slug: '<name>/<arg>' }
//   views.hide(state)   any other route; remembers it as where "Back" should return to
//   views.back()        the back control (and Escape) do this

import { getView, parseViewSlug } from './registry.js';

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

export function createViewHost({ main, atlas, index, loader, navigate }) {
  let dom = null;
  let opened = false;
  let current = null; // { slug, controller, back }
  let returnTo = null; // the last non-view route this page saw: where Back returns to
  let serial = 0;

  function ensureDom() {
    if (dom) return dom;
    const back = h('button', { type: 'button', class: 'view-back', id: 'view-back' }, '← Back to the globe');
    back.addEventListener('click', () => goBack());
    const title = h('h2', { class: 'view-title', id: 'view-title', tabindex: '-1' });
    const subtitle = h('p', { class: 'view-subtitle', id: 'view-subtitle' });
    const head = h('header', { class: 'view-head' }, [back, h('div', { class: 'view-titles' }, [title, subtitle])]);
    const status = h('p', { class: 'visually-hidden', id: 'view-status', role: 'status', 'aria-live': 'polite' });
    const body = h('div', { class: 'view-body', id: 'view-body' });
    const methodBody = h('div', { class: 'view-method-body', id: 'view-method-body' });
    const method = h('details', { class: 'view-method', id: 'view-method' }, [
      h('summary', {}, 'Inputs and method'),
      methodBody,
    ]);
    const page = h('div', { class: 'view-page' }, [head, status, body, method]);
    const root = h('section', { class: 'view-host hidden', id: 'view-host', 'aria-labelledby': 'view-title' }, page);
    main.appendChild(root);
    dom = { root, back, title, subtitle, status, body, method, methodBody };
    return dom;
  }

  function setBack(spec) {
    ensureDom();
    const label = (spec && spec.label) || 'Back to the globe';
    dom.back.textContent = `← ${label.replace(/^←\s*/, '')}`;
    if (current) current.back = spec && spec.route ? spec : null;
  }

  /** Back goes where the reader came from inside this page (the record or the globe
   * they opened the view from); with no such place (a pasted link) to the view's own
   * parent; failing that, to the globe. */
  function goBack() {
    if (returnTo) {
      navigate({ entity: returnTo.entity, mode: returnTo.mode });
      return;
    }
    if (current && current.back && current.back.route) {
      navigate({ entity: current.back.route });
      return;
    }
    navigate({ entity: null });
  }

  function resetFrame() {
    ensureDom();
    dom.title.textContent = '';
    dom.subtitle.textContent = '';
    dom.body.replaceChildren();
    dom.methodBody.replaceChildren();
    dom.method.open = false;
    dom.method.hidden = false;
    dom.status.textContent = '';
    dom.back.textContent = '← Back to the globe';
  }

  function showError(message, retry) {
    ensureDom();
    dom.body.replaceChildren(h('div', { class: 'view-error', role: 'alert' }, [
      h('p', {}, message),
      retry ? (() => {
        const button = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
        button.addEventListener('click', retry);
        return button;
      })() : null,
    ]));
    dom.method.hidden = true;
  }

  async function destroyCurrent() {
    const previous = current;
    current = null;
    if (previous && previous.controller && typeof previous.controller.destroy === 'function') {
      try { previous.controller.destroy(); } catch (error) { window.console.error(error); }
    }
  }

  function makeContext(state, name, arg, host) {
    return {
      arg,
      atlas,
      index,
      loader,
      navigate,
      timelineState: state.range ? { range: state.range } : { year: state.year },
      host,
    };
  }

  async function show(state) {
    ensureDom();
    opened = true;
    dom.root.classList.remove('hidden');
    const { name, arg } = parseViewSlug(state.entity.slug);
    const slug = state.entity.slug;

    // Same view, same argument: only the year or range moved. (This must not take a new
    // ticket: a mount still in flight for this very route would then be abandoned.) An
    // update that arrives before the view has mounted is applied the moment it has.
    if (current && current.slug === slug) {
      current.latest = makeContext(state, name, arg, current.host);
      if (current.controller && typeof current.controller.update === 'function') {
        current.controller.update(current.latest);
      }
      return;
    }

    const ticket = ++serial;
    await destroyCurrent();
    resetFrame();
    const view = getView(name);
    if (!view) {
      dom.title.textContent = 'No such view';
      showError(`The Atlas has no view called “${name}”.`);
      return;
    }
    dom.title.textContent = view.title;
    const parent = view.parent ? view.parent(arg, atlas) : null;
    const host = {
      body: dom.body,
      method: dom.methodBody,
      setTitle: (text) => { dom.title.textContent = text; },
      setSubtitle: (value) => { dom.subtitle.replaceChildren(value == null ? '' : value); },
      setBack,
      announce: (text) => { dom.status.textContent = ''; window.setTimeout(() => { dom.status.textContent = text; }, 30); },
      fail: (message, options = {}) => showError(message, options.retry),
    };
    current = { slug, controller: null, back: parent, host, latest: null };
    if (parent) setBack(parent);
    dom.body.replaceChildren(h('p', { class: 'loading-note', role: 'status' }, 'Loading…'));

    let module;
    try {
      module = await view.load();
    } catch (error) {
      if (ticket !== serial) return;
      showError(`This view could not be loaded: ${error.message}. Check your connection and retry.`, () => {
        current = null;
        show(state);
      });
      return;
    }
    if (ticket !== serial) return;
    dom.body.replaceChildren();
    try {
      const mountContext = makeContext(state, name, arg, host);
      const controller = await module.mount(mountContext);
      if (ticket !== serial) {
        if (controller && typeof controller.destroy === 'function') controller.destroy();
        return;
      }
      current.controller = controller || null;
      if (controller && typeof controller.update === 'function' && current.latest) controller.update(current.latest);
    } catch (error) {
      if (ticket !== serial) return;
      window.console.error(error);
      showError(`This view could not be drawn: ${error.message}.`);
      return;
    }
    // Focus moves to the heading on arrival (and never again for a year change).
    if (ticket === serial && !dom.root.contains(document.activeElement)) {
      dom.title.focus({ preventScroll: true });
    }
  }

  function hide(state) {
    // Whatever the page shows now is where Back returns to.
    if (state) returnTo = { entity: state.entity || null, mode: state.mode || null };
    if (!opened) return;
    opened = false;
    serial += 1;
    destroyCurrent();
    if (dom) {
      dom.root.classList.add('hidden');
      dom.body.replaceChildren();
      dom.methodBody.replaceChildren();
    }
  }

  return {
    show,
    hide,
    back: goBack,
    isOpen: () => opened,
  };
}
