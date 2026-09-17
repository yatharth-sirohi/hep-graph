/* HEP Graph front-end: no external runtime; all data is read from the local API. */
(() => {
  "use strict";
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const state = {
    dataset: null,
    mode: "database",
    people: new Map(),
    source: null,
    target: null,
    lastPath: null,
    displayGraph: null,
    revision: 0,
    pathRequest: 0,
    deepJob: null,
    profileRequest: 0,
    lineage: null,
    lineageRequest: 0,
    graph: {
      nodes: new Map(),
      edges: [],
      scale: 1,
      tx: 0,
      ty: 0,
      drag: null,
      pan: null,
    },
    searches: { source: [], target: [] },
    timers: {},
    filterSignature: null,
    preparation: {
      timers: new Map(),
      inflight: new Map(),
      completed: new Set(),
    },
    restoring: false,
  };
  const allowedHosts = new Set([
    "inspirehep.net",
    "arxiv.org",
    "doi.org",
    "doi.org",
  ]);
  const choiceValue = (selectId, customId) =>
    $(selectId).value === "custom"
      ? $(customId).value.trim()
      : $(selectId).value;
  const filters = () => ({
    min_authors: choiceValue("#min-authors", "#min-authors-custom"),
    max_authors: choiceValue("#max-authors", "#max-authors-custom"),
    min_shared: choiceValue("#min-shared", "#min-shared-custom"),
    year_start: $("#year-start").value,
    year_end: $("#year-end").value,
    genealogy: $("#genealogy").checked ? "true" : "false",
  });
  const formatDate = (value) =>
    value
      ? new Date(value).toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        })
      : "not recorded";
  const personName = (p) => (p && (p.name || p.id)) || "Unknown researcher";
  const canonicalFilters = (f = filters()) => ({
    min_authors: String(f?.min_authors ?? 1),
    max_authors: f?.max_authors == null ? "all" : String(f.max_authors),
    min_shared: String(f?.min_shared ?? 1),
    year_start: String(f?.year_start ?? ""),
    year_end: String(f?.year_end ?? ""),
    genealogy: String(f?.genealogy ?? "false"),
  });
  const filterKey = () => JSON.stringify([state.mode, canonicalFilters()]);
  const queryKey = () =>
    JSON.stringify([state.mode, canonicalFilters(), state.source?.id, state.target?.id]);
  const updateDate = (value) => {
    const date = value ? new Date(value) : null;
    return date && !Number.isNaN(date.getTime())
      ? new Intl.DateTimeFormat("en-US", {
          timeZone: "America/Chicago", month: "2-digit", day: "2-digit", year: "numeric",
        }).format(date)
      : "09/16/2026";
  };
  const lastUpdatedText = () =>
    `Last updated ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}`;
  const canQuery = (person) =>
    Boolean(person && (person.queryable === true || person.indexed === true));
  const teamSizeDescription = (f) => {
    const min = Number(f?.min_authors ?? 1);
    const max = f?.max_authors == null || f.max_authors === "all"
      ? null
      : Number(f.max_authors);
    if (min === 1 && max === 10) return "small-team papers (up to 10 authors)";
    if (min === 11 && max == null) return "large-team papers (more than 10 authors)";
    if (min === 1 && max == null) return "all paper team sizes";
    if (max == null) return `papers with at least ${min} authors`;
    if (min === max) return `papers with exactly ${min} authors`;
    return `papers with ${min}–${max} authors`;
  };
  const filterDescription = (f) => {
    const active = { min_authors: 1, min_shared: 1, ...f };
    return `${teamSizeDescription(active)} · ${active.min_shared} shared work minimum · ${active.year_start || "all years"} to ${active.year_end || "all years"} · ${active.genealogy === false || active.genealogy === "false" ? "PhD excluded" : "PhD included"}`;
  };
  const remember = (person) => {
    if (person?.id) state.people.set(person.id, person);
    return person;
  };
  const byId = (id) =>
    state.graph.nodes.get(id)?.person ||
    state.people.get(id) || { id, name: id };
  const setStatus = (message, kind = "") => {
    const el = $("#global-status");
    el.className = `notice ${kind}`;
    el.textContent = message;
  };
  const clearStatus = () => ($("#global-status").className = "notice hidden");
  const safeHref = (href) => {
    try {
      const u = new URL(href);
      return u.protocol === "https:" && allowedHosts.has(u.hostname)
        ? u.href
        : null;
    } catch {
      return null;
    }
  };
  const link = (text, href) => {
    const a = document.createElement("a");
    a.textContent = text;
    const safe = safeHref(href);
    if (safe) {
      a.href = safe;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    } else {
      a.removeAttribute("href");
    }
    return a;
  };
  const api = async (path) => {
    const response = await fetch(path, {
      headers: { Accept: "application/json" },
    });
    let body;
    try {
      body = await response.json();
    } catch {
      body = { message: "The service returned an unreadable response." };
    }
    if (!response.ok) {
      const e = new Error(
        body.message || `Request failed (${response.status}).`,
      );
      e.body = body;
      e.status = response.status;
      throw e;
    }
    return body;
  };
  const urlWithFilters = (pathname, extras = {}) => {
    const u = new URL(pathname, location.origin);
    const f = filters();
    Object.entries({ ...f, ...extras, mode: "database" }).forEach(([k, v]) => {
      if (v !== "" && v != null) u.searchParams.set(k, v);
    });
    return u.pathname + "?" + u.searchParams.toString();
  };
  const setLoading = (button, loading, label) => {
    button.dataset.label ??= button.textContent;
    button.disabled = loading;
    if (loading) {
      button.textContent = label || "Loading…";
    } else button.textContent = button.dataset.label || button.textContent;
  };

  function validateFilters() {
    const f = filters();
    const numeric = [
      ["Minimum authors", f.min_authors, 1, 100000],
      ["Maximum authors", f.max_authors, 1, 100000],
      ["Minimum shared works", f.min_shared, 1, 1000],
    ];
    for (const [label, value, min, max] of numeric) {
      if (value === "all" && label === "Maximum authors") continue;
      if (
        !/^[1-9][0-9]*$/.test(value) ||
        Number(value) < min ||
        Number(value) > max
      ) {
        setStatus(
          `${label} must be a whole number from ${min} to ${max}.`,
          "error",
        );
        return false;
      }
    }
    if (f.max_authors !== "all" && Number(f.min_authors) > Number(f.max_authors)) {
      setStatus("Minimum authors cannot exceed maximum authors.", "error");
      return false;
    }
    return true;
  }

  function clearPreparation() {
    state.preparation.timers.forEach((timer) => clearTimeout(timer));
    state.preparation.timers.clear();
    state.preparation.inflight.forEach((entry) => entry.controller.abort());
    state.preparation.inflight.clear();
  }

  function preparationUrl(person, activeFilters) {
    const u = new URL("/api/prepare", location.origin);
    const params = {
      mode: "live",
      person: String(person.id),
      ...canonicalFilters(activeFilters),
    };
    Object.entries(params).forEach(([key, value]) => u.searchParams.set(key, value));
    return u.pathname + "?" + u.searchParams.toString();
  }

  async function preparePerson(person, signature, activeFilters) {
    if (state.mode !== "live" || !canQuery(person) || signature !== filterKey()) return;
    if (![state.source?.id, state.target?.id].some((id) => String(id) === String(person.id))) return;
    const key = JSON.stringify([String(person.id), canonicalFilters(activeFilters)]);
    if (state.preparation.completed.has(key) || state.preparation.inflight.has(key)) return;
    const controller = new AbortController();
    state.preparation.inflight.set(key, { controller });
    try {
      const response = await fetch(preparationUrl(person, activeFilters), {
        method: "POST",
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      try { await response.json(); } catch { /* Preparation is an optional warm-up. */ }
      if (response.ok) state.preparation.completed.add(key);
    } catch (error) {
      if (error.name !== "AbortError") {
        /* A failed warm-up must not block identity selection or path search. */
      }
    } finally {
      state.preparation.inflight.delete(key);
    }
  }

  function schedulePreparation(people, delay = 0, timerKey = "selection") {
    if (state.mode !== "live") return;
    const old = state.preparation.timers.get(timerKey);
    if (old) clearTimeout(old);
    const signature = filterKey();
    const activeFilters = canonicalFilters();
    const unique = [...new Map(
      people.filter(Boolean).map((person) => [String(person.id), person]),
    ).values()];
    const timer = setTimeout(() => {
      state.preparation.timers.delete(timerKey);
      unique.forEach((person) => preparePerson(person, signature, activeFilters));
    }, delay);
    state.preparation.timers.set(timerKey, timer);
  }

  function invalidateResults() {
    const hadDeepJob = Boolean(state.deepJob);
    cancelDeepJob();
    state.revision++;
    $("#person-panel").classList.add("hidden");
    $("#person-content").replaceChildren();
    $("#edge-inspector").classList.add("hidden");
    $("#edge-inspector").replaceChildren();
    setLoading($("#find-connection"), false);
    if (state.lastPath || state.displayGraph) {
      $("#path-meta").textContent =
        "Inputs changed. Run the connection query again; the previous result is no longer in scope.";
      $("#path-message").className = "notice warning";
      $("#path-message").textContent =
        "Previous path cleared because the selected inputs changed.";
      $("#path-cards").replaceChildren();
      hideRouteOffer();
      state.lastPath = null;
      state.displayGraph = null;
      state.graph.nodes.clear();
      state.graph.edges = [];
      renderGraph();
    }
    if (hadDeepJob) {
      $("#connection-empty").classList.remove("hidden");
      $("#connection-results").classList.add("hidden");
    }
  }
  function updateCustomVisibility() {
    ["min-authors", "max-authors", "min-shared"].forEach((base) => {
      const custom = $(`#${base}-custom`);
      custom.classList.toggle("hidden", $(`#${base}`).value !== "custom");
    });
  }
  function applyTeamSizePreset(value) {
    const presets = {
      small: ["1", "10"],
      large: ["11", "all"],
      all: ["1", "all"],
    };
    const preset = presets[value];
    if (!preset) return;
    $("#min-authors").value = preset[0];
    $("#max-authors").value = preset[1];
  }
  function syncTeamSizeFromBounds() {
    const f = filters();
    const min = String(f.min_authors);
    const max = String(f.max_authors);
    $("#paper-team-size").value =
      min === "1" && max === "10" ? "small" :
        min === "11" && max === "all" ? "large" :
          min === "1" && max === "all" ? "all" : "custom";
  }
  function updateFilterSummary({ invalidate = true } = {}) {
    updateCustomVisibility();
    const f = filters();
    const customInvalid =
      ($("#min-authors").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.min_authors) ||
          Number(f.min_authors) > 100000)) ||
      ($("#max-authors").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.max_authors) ||
          Number(f.max_authors) > 100000)) ||
      ($("#min-shared").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.min_shared) || Number(f.min_shared) > 1000));
    const nextSignature = JSON.stringify(canonicalFilters(f));
    const changed = state.filterSignature !== null && nextSignature !== state.filterSignature;
    state.filterSignature = nextSignature;
    $("#filter-summary").textContent =
      `${teamSizeDescription(f)} · ${f.min_shared} shared work${f.min_shared === "1" ? "" : "s"} · ${f.genealogy === "true" ? "PhD included" : "PhD excluded"}`;
    if (invalidate && changed) {
      invalidateResults();
      clearPreparation();
      schedulePreparation([state.source, state.target], 400, "filters");
    }
    if (customInvalid)
      setStatus(
        "Enter a positive whole number in the visible custom filter field before running a calculation.",
        "error",
      );
    if (!state.restoring) syncUrl();
  }
  function syncUrl() {
    const u = new URL(location.href),
      f = filters();
    Object.entries(f).forEach(([k, v]) =>
      v === "" ? u.searchParams.delete(k) : u.searchParams.set(k, v),
    );
    u.searchParams.set("mode", "database");
    u.searchParams.delete("version");
    if (state.source) u.searchParams.set("source", state.source.id);
    else u.searchParams.delete("source");
    if (state.target) u.searchParams.set("target", state.target.id);
    else u.searchParams.delete("target");
    history.replaceState(null, "", u);
  }
  function setFilterFromUrl(base, value) {
    const select = $(`#${base.replace("_", "-")}`),
      custom = $(`#${base.replace("_", "-")}-custom`);
    if (!value) return;
    if ([...select.options].some((o) => o.value === value))
      select.value = value;
    else {
      select.value = "custom";
      custom.value = value;
    }
  }
  function restoreUrl() {
    state.restoring = true;
    const u = new URL(location.href);
    setFilterFromUrl("min_authors", u.searchParams.get("min_authors") || "1");
    setFilterFromUrl("max_authors", u.searchParams.get("max_authors"));
    setFilterFromUrl("min_shared", u.searchParams.get("min_shared"));
    for (const key of ["year_start", "year_end"])
      if (u.searchParams.has(key))
        $(`#${key.replace("_", "-")}`).value = u.searchParams.get(key);
    if (u.searchParams.has("genealogy"))
      $("#genealogy").checked = u.searchParams.get("genealogy") === "true";
    state.restore = {
      source: u.searchParams.get("source"),
      target: u.searchParams.get("target"),
    };
    state.mode = "database";
    syncTeamSizeFromBounds();
    updateFilterSummary({ invalidate: false });
    state.restoring = false;
  }
  function coverageText(coverage) {
    if (!coverage) return "Coverage metadata is unavailable.";
    return `Last updated ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}. ${coverage.complete ? "Coverage verified for this release." : "Coverage is partial or bounded."}`;
  }

  function showTab(id) {
    $$(".tab").forEach((x) => {
      const active = x.dataset.tab === id;
      x.classList.toggle("is-active", active);
      x.setAttribute("aria-selected", active ? "true" : "false");
    });
    $$(".view").forEach((x) => x.classList.toggle("is-active", x.id === id));
  }

  function renderPicker(which) {
    const p = state[which],
      holder = $(`#${which}-selected`);
    holder.replaceChildren();
    holder.hidden = !p;
    if (!p) return;
    remember(p);
    const name = document.createElement("b");
    name.textContent = personName(p);
    holder.append(name);
    const sub = document.createElement("span");
    sub.textContent = ` · ${p.id}`;
    holder.append(sub);
    const badge = document.createElement("span");
    badge.className = `status ${p.indexed === false ? "unindexed" : "indexed"}`;
    badge.textContent = p.indexed === false ? "not in this release" : "available";
    holder.append(badge);
  }
  function clearPicker(which) {
    if (which === "lineage") {
      clearLineage();
      return;
    }
    invalidateResults();
    state[which] = null;
    $(`#${which}-query`).value = "";
    $(`#${which}-results`).replaceChildren();
    $(`#${which}-results`).classList.remove("inline-search-notice");
    renderPicker(which);
    syncUrl();
  }
  function choosePerson(which, result) {
    const chosen = result.person || result;
    if (which === "lineage") {
      // The lineage root is independent of the connection query, so picking
      // one must not disturb a path result already on screen.
      setLineageRoot({ ...chosen, indexed: result.indexed ?? chosen.indexed });
      return;
    }
    invalidateResults();
    const p = result.person || result;
    state[which] = remember({
      ...p,
      indexed: result.indexed ?? p.indexed,
      queryable: result.queryable ?? p.queryable ?? false,
      indexed_publications:
        result.indexed_publications ?? p.indexed_publications,
    });
    $(`#${which}-query`).value = "";
    $(`#${which}-results`).replaceChildren();
    $(`#${which}-results`).classList.remove("inline-search-notice");
    $(`#${which}-query`).setAttribute("aria-expanded", "false");
    renderPicker(which);
    syncUrl();
    schedulePreparation([state[which]], 0, which);
  }
  function searchResultText(result) {
    const p = result.person || result;
    const parts = [];
    parts.push(`INSPIRE ${p.id}`);
    if (p.affiliations?.length) parts.push(p.affiliations.join("; "));
    if (p.orcid) parts.push(`ORCID ${p.orcid}`);
    if (result.indexed === false) parts.push("not in this release");
    else if (result.indexed_publications != null)
      parts.push(
        `${result.indexed_publications} indexed publication${result.indexed_publications === 1 ? "" : "s"}`,
      );
    if (result.representative_work?.title)
      parts.push(result.representative_work.title);
    return parts.join(" · ");
  }
  function renderSearches(which, data) {
    const menu = $(`#${which}-results`);
    menu.replaceChildren();
    menu.classList.remove("inline-search-notice");
    state.searchResults = state.searchResults || {};
    state.searchResults[which] = data.results || [];
    if (data.status === "not_found") {
      const x = document.createElement("div");
      x.className = "search-result search-notice";
      x.textContent = data.message || "No matching researcher found.";
      menu.append(x);
      menu.classList.add("inline-search-notice");
      return;
    }
    if (data.status === "ambiguous") {
      const x = document.createElement("div");
      x.className = "search-result";
      x.textContent = data.message || "Several matches found — choose one.";
      menu.append(x);
    }
    if (data.status === "upstream_unavailable") {
      const x = document.createElement("div");
      x.className = "search-result";
      x.textContent =
        data.message ||
        "Live lookup is unavailable. Local results are shown if available.";
      menu.append(x);
    }
    if (data.status === "search_incomplete") {
      const x = document.createElement("div");
      x.className = "search-result search-notice";
      x.textContent = data.message || "Live search returned a bounded partial result.";
      menu.append(x);
    }
    (data.results || []).forEach((r, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "search-result";
      b.setAttribute("role", "option");
      b.dataset.index = i;
      const strong = document.createElement("strong");
      strong.textContent = personName(r.person || r);
      b.append(strong);
      const small = document.createElement("small");
      small.textContent = searchResultText(r);
      b.append(small);
      b.addEventListener("click", () => choosePerson(which, r));
      menu.append(b);
    });
    $(`#${which}-query`).setAttribute(
      "aria-expanded",
      (data.results || []).length ? "true" : "false",
    );
  }

  function setupSearch(which) {
    const input = $(`#${which}-query`);
    input.addEventListener("input", () => {
      invalidateResults();
      if (state[which]) {
        state[which] = null;
        renderPicker(which);
        syncUrl();
      }
      state.searches[which] = {
        query: input.value,
        token: (state.searches[which]?.token || 0) + 1,
      };
      clearTimeout(state.timers[which]);
      state.timers[which] = setTimeout(() => searchPeople(which), 220);
    });
    input.addEventListener("keydown", (e) => {
      const buttons = $$(
        '.search-result[role="option"]',
        $(`#${which}-results`),
      );
      if (e.key === "Escape") {
        $(`#${which}-results`).replaceChildren();
      }
      if (e.key === "ArrowDown" && buttons[0]) {
        e.preventDefault();
        buttons[0].focus();
      }
    });
  }

  function statusForPath(data) {
    if (data.client_message) return data.client_message;
    if (data.status === "ok") return null;
    if (data.mode === "database" && data.status === "settled") {
      if (data.route_status === "exact_route_proven") return null;
      if (data.paths?.length) return "This route is documented, but a shorter one has not been ruled out.";
      if (data.route_status === "no_path") return "No connection was found in this release under the selected filters.";
      return data.message || "The search ended without a proven connection. The absence of a route is not conclusive.";
    }
    const hasPath = Boolean(data.paths?.length);
    if (hasPath) {
      const withPath = {
        searching:
          "A verified route is shown. The exact search continues in the background; if a shorter route is found it is announced above the result and never swapped in by itself.",
        search_incomplete:
          "A verified path is shown, but the exact graph search is incomplete. A shorter path may still be found.",
        resource_limit:
          "A verified path is shown, but the graph search reached its current resource limit. Continue the search to look for a shorter route.",
        cancelled:
          "The graph search was stopped. The verified path shown is supported by retrieved evidence, but shortestness is not established.",
        upstream_unavailable:
          "Source details became unavailable after a route was found. The result remains scoped to this release, and the search is incomplete.",
      };
      if (data.status === "searching") return withPath.searching;
      if (withPath[data.status]) return data.message || withPath[data.status];
    }
    const messages = {
      not_indexed:
        "At least one selected researcher is not included in this release, so no connection claim can be calculated.",
      no_path:
        "No documented connection was found within the indexed data and selected filters.",
      not_found: "The selected researcher was not found by the active source.",
      search_incomplete:
        "The search ended before exploration was complete; any route shown is scoped to this release.",
      searching:
        "The search is still exploring source records; no complete connection claim is available yet.",
      cancelled:
        "The search was stopped. Any route shown is an incomplete result from this release.",
      upstream_unavailable:
        "The search service is temporarily unavailable. Try again shortly.",
      resource_limit:
        "This calculation reached a resource limit before a path could be established.",
    };
    return (
      data.message ||
      messages[data.status] ||
      "No result is available for this request."
    );
  }

  function deepJobCurrent(job) {
    return state.deepJob === job && !job.cancelled &&
      job.revision === state.revision && job.mode === state.mode &&
      job.key === queryKey();
  }

  function deepEndpoint(job, suffix = "") {
    return `/api/search-jobs/${encodeURIComponent(job.jobId)}${suffix}?mode=${encodeURIComponent(job.mode)}`;
  }

  function sendDeepCancel(job) {
    if (!job?.jobId || job.cancelSent) return;
    job.cancelSent = true;
    fetch(deepEndpoint(job, "/cancel"), {
      method: "POST",
      headers: { Accept: "application/json" },
    }).catch(() => {});
  }

  function cancelDeepJob() {
    const job = state.deepJob;
    if (!job) return;
    job.cancelled = true;
    if (job.timer) clearTimeout(job.timer);
    job.timer = null;
    sendDeepCancel(job);
    forgetDeepJob(job);
    state.deepJob = null;
    hideRouteOffer();
    $("#deep-progress")?.classList.add("hidden");
  }

  // Only a temporary job handle and query configuration are kept in this tab.
  // Author and paper records remain in the server's bounded memory workspace.
  function rememberDeepJob(job) {
    if (!job.jobId || job.cancelled) return;
    try {
      sessionStorage.setItem("hep-graph-active-search", JSON.stringify({
        jobId: job.jobId, source: job.source, target: job.target,
        filters: canonicalFilters(job.filters), savedAt: Date.now(),
      }));
    } catch { /* Storage-disabled browsers still support ordinary searches. */ }
  }

  function forgetDeepJob(job) {
    try {
      const raw = sessionStorage.getItem("hep-graph-active-search");
      if (raw && JSON.parse(raw).jobId === job.jobId)
        sessionStorage.removeItem("hep-graph-active-search");
    } catch { /* No stored handle needs to be cleared. */ }
  }

  function retainedDeepJob(job) {
    try {
      const raw = sessionStorage.getItem("hep-graph-active-search");
      if (!raw || raw.length > 2000) return null;
      const saved = JSON.parse(raw);
      if (!/^[a-f0-9]{32}$/.test(saved.jobId) ||
          String(saved.source) !== String(job.source) || String(saved.target) !== String(job.target) ||
          !Number.isFinite(saved.savedAt) || Date.now() - saved.savedAt > 3 * 60 * 60 * 1000 ||
          !Object.hasOwn(saved.filters || {}, "min_authors") ||
          JSON.stringify(canonicalFilters(saved.filters)) !== JSON.stringify(canonicalFilters(job.filters))) return null;
      return saved.jobId;
    } catch { return null; }
  }

  function deepProgressText(progress = {}) {
    const people = progress.people_explored ?? 0;
    const works = progress.works_retrieved ?? 0;
    const elapsed = progress.elapsed_seconds == null
      ? "elapsed time unavailable"
      : `${Math.max(0, Math.round(progress.elapsed_seconds))}s elapsed`;
    const stageLabels = {
      expand_target: "Checking researchers from the target side",
      expand_source: "Checking researchers from the source side",
      check_candidate: "Checking a candidate route",
      retrieve_works: "Retrieving documented works",
      retrieve_people: "Retrieving neighboring researchers",
      source_profile: "Confirming the starting researcher",
      target_profile: "Confirming the target researcher",
      direct_pair: "Checking direct evidence",
      cross_frontier: "Checking links between both sides",
      validate_identity: "Checking profile and paper author names",
      guide_verify: "Verifying a possible connection",
      guide_profile_missing: "Checking another possible connection",
      guide_pair_cap: "Continuing the broader search",
      continue_search: "Continuing automatically with the records already retrieved",
      prove_shortest: "Looking for a shorter route",
      rate_limit_wait: "Waiting for INSPIRE’s rate limit, then continuing automatically",
      retry_upstream: "Waiting briefly for INSPIRE, then retrying automatically",
      discover_coauthors: "Exploring INSPIRE’s coauthor summaries from both ends",
    };
    const stage = stageLabels[progress.stage] || progress.stage || "exploring source records";
    if (progress.expansions != null)
      return `${progress.expansions} search steps · ${stage}`;
    return `${people} people explored · ${works} works retrieved · ${elapsed} · ${stage}`;
  }

  function renderDeepProgress(data, job) {
    const box = $("#deep-progress");
    box.classList.remove("hidden");
    const terminal = data.status !== "searching";
    $("#deep-title").textContent = data.status === "searching"
      ? (job?.displayed ? "Looking for a shorter route…" : "Finding a connection…")
      : data.status === "cancelled"
        ? "Search stopped"
      : data.status === "resource_limit"
          ? "Search reached its current limit"
      : data.status === "search_incomplete"
            ? "Search is incomplete"
            : "Search finished";
    $("#deep-summary").textContent = data.progress
      ? deepProgressText(data.progress)
      : data.message || (terminal ? "The search has ended." : "The search is starting.");
    const stop = $("#deep-stop"), cont = $("#deep-continue");
    const retryableFailure = data.status === "upstream_unavailable" && job?.jobId;
    stop.classList.toggle("hidden", (terminal && !retryableFailure) || job?.cancelled || job?.continuing);
    const verified = Boolean(data.paths?.length || job?.displayed || job?.best);
    cont.textContent = verified ? "Continue exact search" : "Continue search";
    cont.classList.toggle("hidden", !(terminal && data.can_continue === true));
  }

  // The server reports the best route it can currently stand behind
  // (best_route); which route this tab shows (job.displayed) is decided here
  // and is never swapped under the reader. A shorter route is offered in
  // #route-update and shown only when the reader asks for it.
  function routeSnapshot(data) {
    if (!data.paths?.length) return null;
    const best = data.best_route || {
      route_id: data.paths[0].route_id || (data.paths[0].people || []).map((p) => p.id).join(">"),
      hops: data.paths[0].hops,
    };
    return {
      routeId: best.route_id, hops: best.hops, paths: data.paths,
      version: data.version, foundAt: best.found_at_seconds ?? null,
    };
  }

  function routeState(data, job) {
    const displayed = job?.displayed, best = data.best_route;
    if (displayed && best && best.hops < displayed.hops) return "BETTER_ROUTE_AVAILABLE";
    // A route shorter than the server's best (a job restarted on another
    // server that has not re-found it): the server's proof is about a
    // different length and says nothing about this route.
    // Likewise when the server currently has no route at all.
    if (displayed && (!best || best.hops > displayed.hops))
      return data.status === "searching" ? "VERIFIED_ROUTE_FOUND"
        : data.status === "cancelled" ? "VERIFIED_SEARCH_STOPPED" : "SEARCH_INCOMPLETE";
    switch (data.route_status) {
      case "searching_no_path": return "SEARCHING_NO_PATH";
      case "verified_route_found": return "VERIFIED_ROUTE_FOUND";
      case "exact_route_proven": return "EXACT_ROUTE_PROVEN";
      case "verified_search_stopped": return "VERIFIED_SEARCH_STOPPED";
      case "no_path": return "NO_PATH";
      case undefined: return undefined;
      default: return "SEARCH_INCOMPLETE";
    }
  }

  function displayedResult(data, job) {
    const displayed = job.displayed;
    if (!displayed) return { ...data, route_state: routeState(data, job) };
    const best = data.best_route;
    const isBest = Boolean(best && best.route_id === displayed.routeId);
    // A proof closes on a hop count: every verified route of that length is a
    // shortest one, whichever of them is on screen.
    const proven = data.global_shortest_proven === true && Boolean(best) && displayed.hops === best.hops;
    return {
      ...data, paths: displayed.paths, version: displayed.version || data.version,
      ...(job.note ? { client_message: job.note } : {}),
      global_shortest_proven: proven,
      exact_for_retrieved_graph: isBest ? data.exact_for_retrieved_graph : false,
      displayed_route_id: displayed.routeId, displayed_is_best: isBest,
      route_state: routeState(data, job),
    };
  }

  function renderDisplayed(data, job, cards) {
    const shown = displayedResult(data, job);
    if (cards || !job.rendered) renderPath(shown); else renderPathHeading(shown);
    job.rendered = true;
  }

  function showRouteOffer(job, kind) {
    const best = job.best, displayed = job.displayed;
    if (!best || !displayed) return;
    const plural = (n) => `${n} hop${n === 1 ? "" : "s"}`;
    $("#route-update-text").textContent = kind === "exact"
      ? `Exact shortest path found: ${plural(best.hops)}. The ${plural(displayed.hops)} route shown is verified but not the shortest.`
      : `Shorter route found: ${plural(displayed.hops)} → ${plural(best.hops)}. The route shown stays until you switch.`;
    $("#route-update-show").textContent = kind === "exact" ? "Show exact route" : "Show shorter route";
    $("#route-update").classList.remove("hidden");
    state.routeOffer = {
      apply() {
        job.displayed = job.best;
        job.note = null;
        hideRouteOffer();
        if (job.lastData) renderDisplayed(job.lastData, job, true);
      },
    };
  }

  function hideRouteOffer() {
    state.routeOffer = null;
    $("#route-update")?.classList.add("hidden");
  }

  function consumeDeepResponse(data, job) {
    if (!deepJobCurrent(job)) return;
    // Versions come from the server. An update older than one already applied
    // is ignored whole, whatever it says; only its polling obligation remains.
    if (Number.isInteger(data.sequence_number) && data.sequence_number < job.sequence) {
      if (data.status === "searching" && !job.cancelled) scheduleDeepPoll(job);
      return;
    }
    const applied = job.sequence;
    if (Number.isInteger(data.sequence_number)) job.sequence = data.sequence_number;
    job.lastData = data;
    job.progress = data.progress || job.progress;
    const best = routeSnapshot(data);
    const displayed = job.displayed;
    // Only a withdrawal the server reports for the route on screen, in a
    // version newer than the last one applied, may take that route down.
    const withdrawn = Boolean(displayed) && (data.events || []).some((e) =>
      e.type === "route_withdrawn" && e.previous_route_id === displayed.routeId &&
      (!Number.isInteger(e.sequence_number) || e.sequence_number > applied));
    job.best = best;
    let cards = false;
    if (best && !displayed) {
      job.displayed = best;
      job.note = null;
      cards = true;
      hideRouteOffer();
    } else if (withdrawn) {
      // The engine's identity guard retracted the route on screen. A route
      // that is no longer verified must not stay up as if it were.
      job.displayed = best;
      job.note = best
        ? `The route shown earlier was withdrawn after identity checks. The best verified route now has ${best.hops} hop${best.hops === 1 ? "" : "s"}.`
        : "The route shown earlier was withdrawn after identity checks. No verified route is currently known.";
      cards = true;
      hideRouteOffer();
    } else if (best && displayed && best.routeId !== displayed.routeId) {
      if (best.hops < displayed.hops) {
        showRouteOffer(job, data.global_shortest_proven === true ? "exact" : "shorter");
      } else {
        // An equal-length route is not an improvement, and a longer one is
        // not better: keep what is shown, and offer nothing.
        hideRouteOffer();
      }
    } else if (!best && displayed) {
      // The route that was on offer is gone; the one on screen stands.
      hideRouteOffer();
    } else if (best && displayed && best.paths.length !== displayed.paths.length) {
      // Same primary route, more (or fewer) equal-length alternatives.
      job.displayed = best;
      cards = true;
    }
    if (job.displayed || data.status !== "searching") renderDisplayed(data, job, cards);
    renderDeepProgress(data, job);
    if (data.status === "searching") {
      if (!job.cancelled) scheduleDeepPoll(job);
      return;
    }
    job.done = true;
    setLoading($("#find-connection"), false);
    if (data.can_continue !== true) {
      forgetDeepJob(job);
      state.deepJob = null;
      $("#deep-progress").classList.add("hidden");
    }
  }

  function scheduleDeepPoll(job) {
    if (!deepJobCurrent(job)) return;
    if (job.timer) clearTimeout(job.timer);
    // The search advances only inside a poll. A poll that took a while was
    // doing that work, so ask again at once rather than idling; a quick one
    // found the job busy or paused, so there is nothing to gain by hurrying.
    const delay = job.lastPollMs > 1000 ? 250 : 1500;
    job.timer = setTimeout(() => pollDeepJob(job), delay);
  }

  async function pollDeepJob(job) {
    job.timer = null;
    if (!deepJobCurrent(job)) return;
    const startedAt = performance.now();
    try {
      const data = await api(deepEndpoint(job));
      job.lastPollMs = performance.now() - startedAt;
      if (!deepJobCurrent(job)) return;
      job.pollFailures = 0;
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) return;
      if (!e.status || e.status >= 500 || e.status === 429) {
        job.pollFailures = (job.pollFailures || 0) + 1;
        renderDeepProgress({ status: "searching", progress: {
          ...job.progress, stage: "Reconnecting to the running search…",
        } }, job);
        job.timer = setTimeout(() => pollDeepJob(job), Math.min(30000, 2000 * job.pollFailures));
        return;
      }
      if (e.status === 404 && !job.done && (job.restarts || 0) < 2) {
        // The job is unknown to the process that answered: the search state
        // lives in one server process, and a poll can reach a different one.
        // Start the same search again there rather than dead-ending. Progress
        // counters begin again with it, and the stage says so.
        job.restarts = (job.restarts || 0) + 1;
        forgetDeepJob(job);
        job.jobId = null;
        job.sequence = -1;
        renderDeepProgress({ status: "searching", progress: {
          ...job.progress, stage: "The search moved to another server; starting it again there…",
        } }, job);
        try {
          const data = await api(urlWithFilters("/api/path", { source: job.source, target: job.target }));
          if (!deepJobCurrent(job)) {
            // The user moved on while the restart was in flight; do not leave
            // the fresh server job running for nobody.
            if (data.job_id) { job.jobId = data.job_id; sendDeepCancel(job); }
            return;
          }
          if (data.job_id) job.jobId = data.job_id;
          rememberDeepJob(job);
          consumeDeepResponse(data, job);
        } catch (restartError) {
          if (!deepJobCurrent(job)) return;
          job.done = true;
          renderDeepProgress({ status: "upstream_unavailable", message: restartError.message, can_continue: true }, job);
          setLoading($("#find-connection"), false);
        }
        return;
      }
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message, can_continue: true }, job);
      setLoading($("#find-connection"), false);
    }
  }

  async function continueDeepSearch(job) {
    if (!deepJobCurrent(job) || !job.done || job.continuing) return;
    job.continuing = true;
    renderDeepProgress({ status: "searching", progress: job.progress, message: "Continuing the search." }, job);
    try {
      const response = await fetch(deepEndpoint(job, "/continue"), {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      let data;
      try { data = await response.json(); } catch { data = { message: "The service returned an unreadable response." }; }
      if (!response.ok) {
        const error = new Error(data.message || `Request failed (${response.status}).`);
        error.body = data;
        error.status = response.status;
        throw error;
      }
      if (!deepJobCurrent(job)) return;
      job.continuing = false;
      job.done = false;
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) return;
      job.continuing = false;
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message, can_continue: true }, job);
    }
  }

  function stopDeepSearch() {
    const job = state.deepJob;
    if (!job) return;
    job.cancelled = true;
    if (job.timer) clearTimeout(job.timer);
    job.timer = null;
    sendDeepCancel(job);
    forgetDeepJob(job);
    state.deepJob = null;
    const last = job.lastData || {};
    // The route on screen was verified before Stop was pressed; Stop only
    // ends the search for a shorter one. A pending offer stays: that shorter
    // route is verified too.
    const data = {
      ...last, status: "cancelled", can_continue: false, mode: "database",
      version: last.version || job.version, filters: last.filters || job.filters,
      coverage: last.coverage || job.coverage,
      paths: job.displayed ? last.paths || [] : [],
      route_status: job.displayed ? "verified_search_stopped" : "search_incomplete",
      message: job.displayed
        ? "The exact search was stopped. The route shown is verified by retrieved evidence; whether a shorter one exists was not established."
        : "The search was stopped before a route was verified; this result is incomplete.",
    };
    job.lastData = data;
    job.done = true;
    renderDisplayed(data, job, false);
    $("#deep-progress").classList.add("hidden");
    setLoading($("#find-connection"), false);
  }

  async function startDeepSearch({ source, target, revision, request, key }) {
    const job = {
      source, target, revision, request, key, mode: "database", jobId: null,
      version: state.dataset?.version, filters: canonicalFilters(), coverage: state.dataset?.coverage,
      cancelled: false, cancelSent: false, timer: null, done: false,
      continuing: false, progress: {}, lastData: null,
      // Versioned delivery: the last applied server version, the best route
      // the server reports, and the route this tab is showing.
      sequence: -1, best: null, displayed: null, rendered: false, note: null,
    };
    state.deepJob = job;
    hideRouteOffer();
    setLoading($("#find-connection"), true, "Exploring…");
    renderDeepProgress({ status: "searching", progress: job.progress }, job);
    $("#connection-empty").classList.add("hidden");
    $("#connection-results").classList.remove("hidden");
    try {
      let data;
      const retained = retainedDeepJob(job);
      if (retained) {
        job.jobId = retained;
        try { data = await api(deepEndpoint(job)); }
        catch (error) {
          if (!error.status || error.status >= 500 || error.status === 429) {
            if (!deepJobCurrent(job)) return;
            renderDeepProgress({ status: "searching", progress: {
              ...job.progress, stage: "Reconnecting to the running search…",
            } }, job);
            scheduleDeepPoll(job);
            return;
          }
          if (error.status !== 404) throw error;
          forgetDeepJob(job);
          job.jobId = null;
        }
      }
      if (!data) data = await api(urlWithFilters("/api/path", { source, target }));
      if (data.job_id) job.jobId = data.job_id;
      job.version = data.version || job.version;
      job.filters = canonicalFilters(data.filters || job.filters);
      job.coverage = data.coverage || job.coverage;
      job.progress = data.progress || job.progress;
      if (!deepJobCurrent(job)) {
        if (job.jobId) sendDeepCancel(job);
        return;
      }
      rememberDeepJob(job);
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) {
        if (e.body?.job_id) { job.jobId = e.body.job_id; sendDeepCancel(job); }
        return;
      }
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message }, job);
      setLoading($("#find-connection"), false);
      state.deepJob = null;
    }
  }

  async function findPath() {
    clearStatus();
    if (!validateFilters()) return;
    if (!state.source || !state.target) {
      setStatus(
        "Choose a queryable researcher in both fields before finding a connection.",
        "warning",
      );
      return;
    }
    if (!canQuery(state.source) || !canQuery(state.target)) {
      setStatus(
        "One of the selected researchers is not included in this release. Choose another result.",
        "warning",
      );
      return;
    }
    const ys = Number($("#year-start").value),
      ye = Number($("#year-end").value);
    if (ys && ye && ys > ye) {
      setStatus(
        "The starting year must be before or equal to the ending year.",
        "error",
      );
      return;
    }
    const btn = $("#find-connection"),
      revision = state.revision,
      request = ++state.pathRequest,
      key = queryKey(),
      current = () =>
        revision === state.revision &&
        request === state.pathRequest &&
        key === queryKey();
    startDeepSearch({ source: state.source.id, target: state.target.id, revision, request, key });
  }

  function addGraphNode(person, kind = "") {
    if (!person?.id) return;
    const old = state.graph.nodes.get(person.id);
    if (old) {
      if (kind) old.kind = kind;
      return old;
    }
    const n = {
      person,
      x: 120 + Math.random() * 600,
      y: 100 + Math.random() * 280,
      kind,
      pinned: false,
    };
    state.graph.nodes.set(person.id, n);
    return n;
  }
  function drawPathGraph(data) {
    state.displayGraph = null;
    state.graph.nodes.clear();
    state.graph.edges = [];
    (data.paths || []).forEach((path, pi) => {
      (path.people || []).forEach((p) => {
        remember(p);
        addGraphNode(p, "path");
      });
      (path.edges || []).forEach((e) => {
        const key = [e.source, e.target].sort().join(":");
        const existing = state.graph.edges.find(
          (edge) => [edge.source, edge.target].sort().join(":") === key,
        );
        if (existing) existing.path ||= pi === 0;
        else state.graph.edges.push({ ...e, path: pi === 0 });
      });
    });
    const nodes = [...state.graph.nodes.values()];
    nodes.forEach((n, idx) => {
      n.x = 160 + (idx % 4) * 240;
      n.y = 160 + Math.floor(idx / 4) * 165;
    });
    state.graph.scale = 1;
    state.graph.tx = 0;
    state.graph.ty = 0;
    renderGraph();
    requestAnimationFrame(() => {
      fitGraph();
      renderGraph();
    });
  }

  function pointerPos(e) {
    const r = $("#connection-graph").getBoundingClientRect();
    return {
      x: (e.clientX - r.left - state.graph.tx) / state.graph.scale,
      y: (e.clientY - r.top - state.graph.ty) / state.graph.scale,
    };
  }
  function startNodeDrag(e, n) {
    e.stopPropagation();
    state.graph.drag = {
      n,
      offset: { x: pointerPos(e).x - n.x, y: pointerPos(e).y - n.y },
      moved: false,
    };
    $("#graph-stage").setPointerCapture?.(e.pointerId);
  }
  function setupGraphInteractions() {
    const stage = $("#graph-stage");
    stage.addEventListener("pointerdown", (e) => {
      if (e.target === stage || e.target.tagName === "svg") {
        state.graph.pan = {
          x: e.clientX,
          y: e.clientY,
          tx: state.graph.tx,
          ty: state.graph.ty,
        };
        stage.setPointerCapture?.(e.pointerId);
      }
    });
    stage.addEventListener("pointermove", (e) => {
      if (state.graph.drag) {
        const p = pointerPos(e);
        state.graph.drag.n.x = p.x - state.graph.drag.offset.x;
        state.graph.drag.n.y = p.y - state.graph.drag.offset.y;
        state.graph.drag.n.pinned = true;
        state.graph.drag.moved = true;
        renderGraph();
      } else if (state.graph.pan) {
        state.graph.tx = state.graph.pan.tx + e.clientX - state.graph.pan.x;
        state.graph.ty = state.graph.pan.ty + e.clientY - state.graph.pan.y;
        renderGraph();
      }
    });
    stage.addEventListener("pointerup", () => {
      state.graph.drag = null;
      state.graph.pan = null;
    });
    stage.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        state.graph.scale = Math.min(
          2.8,
          Math.max(0.35, state.graph.scale * (e.deltaY < 0 ? 1.12 : 0.89)),
        );
        renderGraph();
      },
      { passive: false },
    );
    $$("[data-graph]").forEach((b) =>
      b.addEventListener("click", () => {
        const a = b.dataset.graph;
        if (a === "zoom-in")
          state.graph.scale = Math.min(2.8, state.graph.scale * 1.2);
        if (a === "zoom-out")
          state.graph.scale = Math.max(0.35, state.graph.scale * 0.8);
        if (a === "reset") {
          state.graph.scale = 1;
          state.graph.tx = 0;
          state.graph.ty = 0;
        }
        if (a === "fit") fitGraph();
        renderGraph();
      }),
    );
    $("#show-labels").addEventListener("change", renderGraph);
  }

  function personButton(p, extra = "") {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "person-link";
    b.textContent = personName(p);
    if (extra) b.append(document.createTextNode(extra));
    b.addEventListener("click", () => openProfile(p.id));
    return b;
  }
  async function hydratePeople(ids) {
    const revision = state.revision;
    const mode = state.mode;
    const current = () => revision === state.revision && mode === state.mode;
    await Promise.all(
      [...new Set(ids)]
        .filter((x) => x && !state.people.has(x))
        .map(async (id) => {
          try {
            if (!current()) return;
            const d = await api(
              urlWithFilters(`/api/person/${encodeURIComponent(id)}`, state.mode === "live" ? { summary: "1" } : {}),
            );
            if (!current()) return;
            remember({
              ...d.person,
              indexed: d.indexed ?? d.person?.indexed ?? false,
              queryable: d.queryable ?? d.person?.queryable ?? false,
            });
          } catch {
            /* ID is still shown if this profile is unavailable */
          }
        }),
    );
  }

  function jsonExport() {
    const result = state.lastPath || state.displayGraph;
    if (!result) return;
    const shown = {
      nodes: [...state.graph.nodes.values()].map((n) => ({
        person: n.person,
        x: n.x,
        y: n.y,
        pinned: n.pinned,
        kind: n.kind,
      })),
      edges: state.graph.edges,
      transform: {
        scale: state.graph.scale,
        x: state.graph.tx,
        y: state.graph.ty,
      },
    };
    const payload = {
      mode: result.mode || state.mode,
      snapshot_version: result.version || state.dataset?.version,
      filters: { min_authors: 1, ...(result.filters || filters()) },
      path_result: state.lastPath || null,
      // The export describes the route on screen, which may be an older
      // verified route than the server's best; both are named here.
      route_delivery: state.lastPath ? {
        route_status: state.lastPath.route_status ?? null,
        route_state: state.lastPath.route_state ?? null,
        displayed_route_id: state.lastPath.displayed_route_id ?? state.lastPath.paths?.[0]?.route_id ?? null,
        displayed_is_best: state.lastPath.displayed_is_best ?? (state.lastPath.best_route ? true : null),
        best_route: state.lastPath.best_route ?? null,
        sequence_number: state.lastPath.sequence_number ?? null,
        metrics: state.lastPath.metrics ?? null,
        events: state.lastPath.events ?? null,
      } : null,
      display_scope: state.displayGraph || null,
      displayed_graph: shown,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    download(
      blob,
      `hep-graph-path-${payload.snapshot_version || "snapshot"}.json`,
    );
  }
  function svgExport() {
    const result = state.lastPath || state.displayGraph;
    if (!result) return;
    const copy = $("#connection-graph").cloneNode(true);
    copy.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    copy.setAttribute(
      "viewBox",
      `0 0 ${$("#graph-stage").clientWidth} ${$("#graph-stage").clientHeight}`,
    );
    const style = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "style",
    );
    style.textContent =
      ".edge{stroke:#168b85;stroke-width:2.4;fill:none}.edge.phd{stroke:#b86c06;stroke-dasharray:7 4}.edge.selected{stroke-width:4}.edge-label{font:11px system-ui;fill:#4c626d;paint-order:stroke;stroke:#fff;stroke-width:3}.node circle{fill:#e8f7f5;stroke:#168b85;stroke-width:2.3}.node.path circle{fill:#d1f1ed;stroke-width:3.3}.node.expanded circle{fill:#fff1d8;stroke:#b86c06}.node text{font:12px system-ui;fill:#233e4b;paint-order:stroke;stroke:#fff;stroke-width:3}";
    copy.prepend(style);
    copy.querySelector("desc").textContent =
      `HEP Graph: bounded display of documented coauthorship ties. Filters ${JSON.stringify({ min_authors: 1, ...(result.filters || filters()) })}. ${coverageText(result.coverage)} The displayed neighborhood does not define the path calculation.`;
    const blob = new Blob([new XMLSerializer().serializeToString(copy)], {
      type: "image/svg+xml",
    });
    download(blob, "hep-graph-connection.svg");
  }
  function download(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  async function resolvePerson(id) {
    const revision = state.revision;
    const mode = state.mode;
    const d = await api(
      urlWithFilters(`/api/person/${encodeURIComponent(id)}`, state.mode === "live" ? { summary: "1" } : {}),
    );
    if (revision !== state.revision || mode !== state.mode) return null;
    return remember({
      ...d.person,
      indexed: d.indexed ?? d.person?.indexed ?? false,
      queryable: d.queryable ?? d.person?.queryable ?? false,
      indexed_publications: d.indexed_publications ?? d.person?.indexed_publications,
    });
  }

  function registerModelContext() {
    const mc = navigator.modelContext;
    if (!mc?.registerTool) return;
    try {
      mc.registerTool({
        name: "findConnection",
        description:
          "Find documented researcher connections in the published research data. Searches may return a resumable job that can be polled for progress.",
        inputSchema: {
          type: "object",
          properties: {
            source: { type: "string" },
            target: { type: "string" },
          },
          required: ["source", "target"],
        },
        execute: async ({ source, target }) =>
          api(urlWithFilters("/api/path", { source, target })),
      });
      mc.registerTool({
        name: "setFilters",
        description:
          "Set HEP Graph connection filters in the active research workspace.",
        inputSchema: {
          type: "object",
          properties: {
            min_authors: { type: "number" },
            max_authors: { type: "string" },
            min_shared: { type: "number" },
            year_start: { type: "number" },
            year_end: { type: "number" },
            genealogy: { type: "boolean" },
          },
        },
        execute: async (f) => {
          Object.entries(f).forEach(([k, v]) => {
            const el = $(`#${k.replace("_", "-")}`);
            if (el)
              el.type === "checkbox"
                ? (el.checked = Boolean(v))
                : (el.value = String(v));
          });
          updateFilterSummary();
          return { filters: filters() };
        },
      });
    } catch {
      /* WebMCP is optional and varies by browser */
    }
  }
  function phdDirection(edge) {
    if (!edge.types?.includes("phd")) return null;
    const record = (edge.phd || [])[0];
    return record
      ? { source: String(record.adviser), target: String(record.student) }
      : null;
  }
  function edgeInspector(edge) {
    const box = $("#edge-inspector");
    box.replaceChildren();
    box.classList.remove("hidden");
    const h = document.createElement("strong");
    h.textContent = `Relationship evidence: ${personName(byId(edge.source))} and ${personName(byId(edge.target))}`;
    box.append(h);
    box.append(evidenceItem(edge));
    box.focus?.();
  }
  function evidenceItem(edge) {
    const div = document.createElement("div");
    div.className = "evidence-item";
    const labels = [];
    if (edge.types?.includes("coauthor"))
      labels.push(
        `${edge.shared_works || 0} eligible shared work${edge.shared_works === 1 ? "" : "s"}`,
      );
    if (edge.phd?.length)
      labels.push(
        `${edge.phd?.length || 0} ${edge.types?.includes("coauthor") ? "supplemental " : ""}doctoral record${edge.phd?.length === 1 ? "" : "s"}`,
      );
    div.append(
      document.createTextNode(labels.join(" · ") || "Documented relationship"),
    );
    for (const work of edge.works || []) {
      const row = document.createElement("div");
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = "WORK";
      row.append(tag, link(work.title || `Work ${work.id}`, work.source_url));
      const date = work.date || work.year || "undated";
      row.append(
        document.createTextNode(
          ` · documented ${date} (${work.date_source || "date source not supplied"}) · full author count ${work.author_count ?? "not supplied"}`,
        ),
      );
      for (const doi of work.doi || []) {
        row.append(
          document.createTextNode(" · "),
          link(`DOI ${doi}`, `https://doi.org/${doi}`),
        );
      }
      for (const arxiv of work.arxiv || []) {
        const id = String(arxiv).replace(/^arXiv:/i, "");
        row.append(
          document.createTextNode(" · "),
          link(`arXiv ${id}`, `https://arxiv.org/abs/${id}`),
        );
      }
      if (work.retrieved_at)
        row.append(
          document.createTextNode(
            ` · retrieved ${formatDate(work.retrieved_at)}`,
          ),
        );
      div.append(row);
    }
    for (const phd of edge.phd || []) {
      const row = document.createElement("div");
      const tag = document.createElement("span");
      tag.className = "tag phd";
      tag.textContent = edge.types?.includes("coauthor") ? "PHD CONTEXT" : "PHD";
      row.append(
        tag,
        personButton(byId(String(phd.adviser))),
        document.createTextNode(" (adviser) → "),
        personButton(byId(String(phd.student))),
        document.createTextNode(
          ` (student) · ${phd.degree || "doctoral degree"}${phd.year ? ` · ${phd.year}` : ""}`,
        ),
      );
      if (phd.uncertainty)
        row.append(
          document.createTextNode(
            ` · uncertainty: ${phd.uncertainty === "curated_relation_not_true" ? "INSPIRE link not marked curator-verified" : phd.uncertainty}`,
          ),
        );
      if (phd.source_kind === "institutional_historical_supplement")
        row.append(document.createTextNode(" · institutional historical source"));
      row.append(
        document.createTextNode(" · "),
        link(phd.source_record || "source record", phd.source_url),
      );
      if (phd.retrieved_at)
        row.append(
          document.createTextNode(
            ` · retrieved ${formatDate(phd.retrieved_at)}`,
          ),
        );
      div.append(row);
    }
    return div;
  }
  function renderGraph() {
    const svg = $("#connection-graph"),
      vp = $(".viewport", svg),
      edgeLayer = $(".edge-layer", svg),
      nodeLayer = $(".node-layer", svg),
      ns = "http://www.w3.org/2000/svg";
    edgeLayer.replaceChildren();
    nodeLayer.replaceChildren();
    vp.setAttribute(
      "transform",
      `translate(${state.graph.tx} ${state.graph.ty}) scale(${state.graph.scale})`,
    );
    const el = (tag, attrs = {}) => {
      const x = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([k, v]) => x.setAttribute(k, String(v)));
      return x;
    };
    if (!svg.querySelector("defs")) {
      const defs = el("defs"),
        m = el("marker", {
          id: "arrowhead",
          viewBox: "0 0 10 10",
          refX: 9,
          refY: 5,
          markerWidth: 7,
          markerHeight: 7,
          orient: "auto",
        });
      m.append(el("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#b86c06" }));
      defs.append(m);
      svg.prepend(defs);
    }
    const addLine = (
      edge,
      a,
      b,
      kind,
      offset = 0,
      orientationA = a,
      orientationB = b,
    ) => {
      const dx = orientationB.x - orientationA.x,
        dy = orientationB.y - orientationA.y,
        len = Math.hypot(dx, dy) || 1,
        ox = (-dy / len) * offset,
        oy = (dx / len) * offset,
        lineDx = b.x - a.x,
        lineDy = b.y - a.y,
        lineLength = Math.hypot(lineDx, lineDy) || 1,
        startInset = kind === "phd" ? 20 : 0,
        endInset = kind === "phd" ? 24 : 0;
      const line = el("line", {
        x1: a.x + ox + (lineDx / lineLength) * startInset,
        y1: a.y + oy + (lineDy / lineLength) * startInset,
        x2: b.x + ox - (lineDx / lineLength) * endInset,
        y2: b.y + oy - (lineDy / lineLength) * endInset,
        class: `edge ${kind} ${edge.path ? "selected" : ""}`,
        tabindex: "0",
        role: "button",
        "aria-label": `${kind === "phd" ? "PhD adviser to student" : "Coauthorship"} evidence`,
      });
      if (kind === "phd") line.setAttribute("marker-end", "url(#arrowhead)");
      line.addEventListener("click", (e) => {
        e.stopPropagation();
        edgeInspector(edge);
      });
      line.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          edgeInspector(edge);
        }
      });
      edgeLayer.append(line);
    };
    state.graph.edges.forEach((edge) => {
      const a = state.graph.nodes.get(edge.source),
        b = state.graph.nodes.get(edge.target);
      if (!a || !b) return;
      if (edge.types?.includes("coauthor"))
        addLine(edge, a, b, "coauthor");
      else if (edge.types?.includes("phd")) {
        const d = phdDirection(edge),
          from = d && state.graph.nodes.get(d.source),
          to = d && state.graph.nodes.get(d.target);
        if (from && to) addLine(edge, from, to, "phd", 0, a, b);
      }
      if (state.graph.scale > 0.72 && edge.shared_works) {
        const t = el("text", {
          x: (a.x + b.x) / 2,
          y: (a.y + b.y) / 2 - 8,
          class: "edge-label",
        });
        t.textContent = `${edge.shared_works} work${edge.shared_works === 1 ? "" : "s"}`;
        edgeLayer.append(t);
      }
    });
    state.graph.nodes.forEach((n) => {
      const g = el("g", {
        class: `node ${n.kind || ""}`,
        transform: `translate(${n.x} ${n.y})`,
        tabindex: "0",
        role: "button",
        "aria-label": `Open profile for ${personName(n.person)}`,
      });
      g.append(el("circle", { r: 20 }));
      if ($("#show-labels").checked) {
        const t = el("text", { x: 0, y: 36, "text-anchor": "middle" });
        t.textContent = personName(n.person);
        g.append(t);
      }
      g.addEventListener("click", () => openProfile(n.person.id));
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openProfile(n.person.id);
        }
      });
      g.addEventListener("pointerdown", (e) => startNodeDrag(e, n));
      nodeLayer.append(g);
    });
  }
  async function expandNeighborhood(id) {
    const revision = state.revision,
      key = filterKey(),
      prior = state.lastPath;
    try {
      const data = await api(
        urlWithFilters(`/api/neighborhood/${encodeURIComponent(id)}`, {
          limit: 40,
        }),
      );
      if (
        revision !== state.revision ||
        key !== filterKey() ||
        prior !== state.lastPath
      )
        return;
      if (!state.graph.nodes.has(id)) addGraphNode(byId(id), "expanded");
      const available = Math.max(0, 100 - state.graph.nodes.size),
        people = (data.people || [])
          .filter((p) => !state.graph.nodes.has(p.id))
          .slice(0, available);
      people.forEach((p) => {
        remember(p);
        addGraphNode(p, "expanded");
      });
      (data.edges || []).forEach((e) => {
        if (
          state.graph.nodes.has(e.source) &&
          state.graph.nodes.has(e.target) &&
          !state.graph.edges.some(
            (x) =>
              [x.source, x.target].sort().join(":") ===
                [e.source, e.target].sort().join(":") &&
              JSON.stringify(x.types) === JSON.stringify(e.types),
          )
        )
          state.graph.edges.push({ ...e, path: false });
      });
      const anchor = state.graph.nodes.get(id),
        added = people.map((p) => state.graph.nodes.get(p.id));
      added.forEach((n, i) => {
        const ring = Math.floor(Math.sqrt(i / 8)),
          slots = Math.max(8, (ring + 1) * 10),
          angle = ((i % slots) / slots) * Math.PI * 2,
          radius = 125 + ring * 105;
        n.x = (anchor?.x || 360) + radius * Math.cos(angle);
        n.y = (anchor?.y || 240) + radius * Math.sin(angle);
      });
      renderGraph();
      if (!state.lastPath) {
        state.displayGraph = {
          type: "bounded_neighborhood",
          center: id,
          version: data.version || state.dataset?.version,
          filters: data.filters || filters(),
          coverage: data.coverage || state.dataset?.coverage,
          truncated: Boolean(data.truncated) || state.graph.nodes.size >= 100,
        };
        showTab("connections");
        $("#person-panel").classList.add("hidden");
        $("#connection-empty").classList.add("hidden");
        $("#connection-results").classList.remove("hidden");
        $("#copy-share").hidden = true;
        $("#path-cards").replaceChildren();
        $("#path-title").textContent = "Bounded local neighborhood";
        $("#path-meta").textContent =
          `${lastUpdatedText()} · ${filterDescription(state.displayGraph.filters)} · neighborhood around ${personName(byId(id))} · this display does not define the path calculation.`;
        fitGraph();
        renderGraph();
      }
      if (
        data.truncated ||
        available <
          (data.people || []).filter((p) => !state.graph.nodes.has(p.id)).length
      )
        setStatus(
          `The displayed neighborhood is bounded to ${Math.min(100, state.graph.nodes.size)} people. This does not alter path calculations.`,
          "warning",
        );
    } catch (e) {
      setStatus(e.message, "error");
    }
  }
  async function searchPeople(which) {
    const q = $(`#${which}-query`).value.trim();
    const token = state.searches[which]?.token;
    if (q.length < 2) {
      $(`#${which}-results`).replaceChildren();
      return;
    }
    try {
      const data = await api(
        urlWithFilters("/api/search", { q }),
      );
      if (
        token !== state.searches[which]?.token ||
        q !== $(`#${which}-query`).value.trim()
      )
        return;
      renderSearches(which, data);
    } catch (e) {
      if (
        token !== state.searches[which]?.token ||
        q !== $(`#${which}-query`).value.trim()
      )
        return;
      renderSearches(which, {
        status: "not_found",
        message: e.message,
        results: [],
      });
    }
  }
  function copyShare() {
    const value = location.href;
    const done = () => {
      const b = $("#copy-share");
      b.textContent = "Link copied";
      setTimeout(() => (b.textContent = "Copy share link"), 1500);
    };
    if (navigator.clipboard?.writeText)
      navigator.clipboard
        .writeText(value)
        .then(done)
        .catch(() => shareFallback(value));
    else shareFallback(value);
  }
  function shareFallback(value) {
    let input = $("#share-url");
    if (!input) {
      input = document.createElement("input");
      input.id = "share-url";
      input.className = "share-url";
      input.readOnly = true;
      $("#path-meta").append(document.createElement("br"), input);
    }
    input.value = value;
    input.focus();
    input.select();
  }
  function populateAbout(coverage) {
    const card = $("#about-coverage");
    if (!coverage) return;
    card.replaceChildren();
    const h = document.createElement("h2");
    h.textContent = "Data coverage";
    const p = document.createElement("p");
    p.textContent = `Connections reflect source records available as of ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}. An absent route does not prove that no connection exists outside this release.`;
    const meta = document.createElement("p");
    meta.className = "muted";
    meta.textContent = `Completeness: ${coverage.complete ? "declared complete" : "partial / bounded"} · queries recorded: ${(coverage.queries || []).length} · failures recorded: ${(coverage.failures || []).length}`;
    card.append(h, p, meta);
  }
  function displayCoverage(coverage) {
    populateAbout(coverage);
  }
  async function loadDataset({ restoreQuery = true } = {}) {
    const revision = state.revision;
    try {
      const d = await api("/api/dataset?mode=database");
      if (revision !== state.revision) return;
      state.dataset = d;
      if (d.source_mode !== "database") throw new Error("The research data is unavailable.");
      state.mode = "database";
      if (d.capabilities?.genealogy !== true) {
        $("#genealogy").checked = false;
        $("#genealogy").disabled = true;
        $("#genealogy-note").textContent = "Not in this release; routes use coauthorship only.";
        updateFilterSummary({ invalidate: false });
      }
      $("#last-updated").textContent = lastUpdatedText();
      displayCoverage(d.coverage);
      clearStatus();
      if (!state.restoring) syncUrl();
      $("#version-warning").classList.add("hidden");
      const ids = restoreQuery
        ? [state.restore?.source, state.restore?.target].filter(Boolean)
        : [];
      if (ids.length && revision === state.revision) {
        try {
          const people = await Promise.all(ids.map(resolvePerson));
          if (revision !== state.revision) return;
          if (state.restore.source)
            state.source = people[ids.indexOf(state.restore.source)];
          if (state.restore.target)
            state.target = people[ids.indexOf(state.restore.target)];
          renderPicker("source");
          renderPicker("target");
          syncUrl();
          schedulePreparation([state.source, state.target], 0, "restore");
          if (state.source && state.target) findPath();
        } catch (e) {
          setStatus(
            `This shared query could not restore one or more profiles: ${e.message}`,
            "warning",
          );
        }
      }
    } catch (e) {
      setStatus(`Could not load the research data: ${e.message}`, "error");
    }
  }

  const seconds = (value) => `${value < 10 ? Math.round(value * 10) / 10 : Math.round(value)}s`;

  // Title, message and meta line only: updated on every poll without
  // rebuilding the route cards, so an opened evidence panel stays open.
  function renderPathHeading(data) {
    state.lastPath = data;
    $("#copy-share").hidden = false;
    $("#connection-empty").classList.add("hidden");
    $("#connection-results").classList.remove("hidden");
    $("#connection-results").dataset.routeState = data.route_state || "";
    const message = statusForPath(data),
      msg = $("#path-message");
    msg.className = `notice ${message ? "" : "hidden"} ${data.status === "resource_limit" ? "warning" : ""}`;
    msg.textContent = message || "";
    const routes = data.paths?.length || 0;
    const hops = data.paths?.[0]?.hops;
    const hopText = Number.isInteger(hops) ? ` · ${hops} hop${hops === 1 ? "" : "s"}` : "";
    const rs = routes ? data.route_state : null;
    $("#path-title").textContent =
      rs === "EXACT_ROUTE_PROVEN"
        ? `Exact shortest path${hopText}${routes > 1 ? ` · ${routes} routes` : ""}`
        : rs === "VERIFIED_ROUTE_FOUND"
          ? `Verified route shown${hopText} · looking for a shorter one`
          : rs === "BETTER_ROUTE_AVAILABLE"
            ? `Verified route shown${hopText} · shorter route available`
            : rs === "VERIFIED_SEARCH_STOPPED"
              ? `Verified route${hopText} · search stopped`
              : rs === "SEARCH_INCOMPLETE"
                ? `Verified route${hopText} · exact search incomplete`
                : data.status === "ok"
                  ? `${routes} documented route${routes === 1 ? "" : "s"}`
                  : routes
                    ? `${routes} verified route${routes === 1 ? "" : "s"} · exact search incomplete`
                    : "Connection result";
    const scopedFilters = data.filters || filters();
    const hasPath = Boolean(data.paths?.length);
    const incomplete = ["search_incomplete", "resource_limit", "cancelled", "upstream_unavailable"].includes(data.status);
    const precision = data.global_shortest_proven === true
      ? "proven shortest in this release and filters"
      : hasPath
        ? "verified route; shortestness not established"
        : incomplete || data.route_status !== "no_path"
          ? "search incomplete; no no-path conclusion"
          : "no path in this release and filters";
    const retrievalInfo = data.retrieval || data.coverage?.retrieved;
    const retrieval = retrievalInfo
      ? ` · retrieved ${retrievalInfo.people ?? retrievalInfo.profiles ?? "?"} people / ${retrievalInfo.works ?? "?"} works${data.retrieval?.truncated || data.coverage?.partial ? " · truncated" : ""}`
      : "";
    const metrics = data.metrics || {};
    const timing = hasPath && metrics.time_to_first_verified_path != null
      ? ` · first route after ${seconds(metrics.time_to_first_verified_path)}${
        metrics.time_to_exact_proof != null ? `, proven shortest after ${seconds(metrics.time_to_exact_proof)}` : ""}`
      : "";
    $("#path-meta").textContent =
      `${lastUpdatedText()} · ${precision} · ${filterDescription(scopedFilters)}${retrieval}${timing}`;
    displayCoverage(data.coverage || state.dataset?.coverage);
  }

  function renderPath(data) {
    renderPathHeading(data);
    $("#path-cards").replaceChildren();
    (data.paths || []).forEach((path, index) => {
      const card = document.createElement("article");
      card.className = "path-card";
      const route = document.createElement("div");
      route.className = "path-route";
      path.people.forEach((p, i) => {
        remember(p);
        const b = personButton(p);
        route.append(b);
        if (i < path.people.length - 1) {
          const e = path.edges[i],
            d = e.types?.includes("coauthor") ? null : phdDirection(e),
            next = path.people[i + 1],
            arrow = document.createElement("span");
          arrow.className = "route-arrow";
          arrow.textContent = d
            ? String(d.source) === String(p.id) &&
              String(d.target) === String(next.id)
              ? "→"
              : "←"
            : "—";
          arrow.title = d
            ? "Actual adviser → student direction; this route may traverse it in either direction."
            : e.types?.includes("coauthor")
              ? "Coauthorship tie; supplemental doctoral metadata does not add another hop."
              : "Documented relationship";
          route.append(arrow);
        }
      });
      card.append(route);
      const summary = document.createElement("p");
      summary.className = "edge-summary";
      summary.textContent = `Route ${index + 1} · ${path.hops} person-to-person hop${path.hops === 1 ? "" : "s"}.`;
      card.append(summary);
      (path.edges || []).forEach((e, i) => {
        const details = document.createElement("details");
        details.className = "evidence";
        const sum = document.createElement("summary");
        sum.textContent = `Evidence for hop ${i + 1}: ${personName(byId(e.source))} ↔ ${personName(byId(e.target))}`;
        details.append(sum, evidenceItem(e));
        card.append(details);
      });
      $("#path-cards").append(card);
    });
    drawPathGraph(data);
  }
  function fitGraph() {
    const ns = [...state.graph.nodes.values()];
    if (!ns.length) return;
    const width = $("#graph-stage").clientWidth,
      height = $("#graph-stage").clientHeight,
      labelPad = $("#show-labels").checked ? 130 : 60,
      xs = ns.map((n) => n.x),
      ys = ns.map((n) => n.y),
      minX = Math.min(...xs) - labelPad,
      maxX = Math.max(...xs) + labelPad,
      minY = Math.min(...ys) - 60,
      maxY = Math.max(...ys) + ($("#show-labels").checked ? 88 : 60);
    state.graph.scale = Math.min(
      1.6,
      Math.max(0.3, Math.min(width / (maxX - minX), height / (maxY - minY))),
    );
    state.graph.tx = width / 2 - (state.graph.scale * (minX + maxX)) / 2;
    state.graph.ty = height / 2 - (state.graph.scale * (minY + maxY)) / 2;
  }
  async function openProfile(id) {
    const panel = $("#person-panel"),
      content = $("#person-content"),
      revision = state.revision,
      request = ++state.profileRequest,
      key = filterKey(),
      current = () =>
        revision === state.revision &&
        request === state.profileRequest &&
        key === filterKey();
    panel.classList.remove("hidden");
    content.textContent = "Loading researcher profile…";
    try {
      const d = await api(
        urlWithFilters(`/api/person/${encodeURIComponent(id)}`),
      );
      if (!current()) return;
      if (d.status && d.status !== "ok")
        throw new Error(d.message || "Profile unavailable.");
      const p = remember(d.person),
        ties = [...(d.advisers || []), ...(d.students || [])];
      (d.collaborators || []).forEach((x) => remember(x.person));
      await hydratePeople(
        ties.map((x) => (x.adviser === id ? x.student : x.adviser)),
      );
      if (!current()) return;
      content.replaceChildren();
      const title = document.createElement("div"),
        h = document.createElement("h2"),
        meta = document.createElement("p");
      title.className = "profile-title";
      h.textContent = personName(p);
      meta.className = "profile-meta";
      meta.textContent = `${p.id}${p.profile_status === "literature_only" ? " · literature only" : ""}${p.orcid ? ` · ORCID ${p.orcid}` : ""}${p.affiliations?.length ? ` · Affiliations reported in retrieved sources: ${p.affiliations.join("; ")}` : " · Affiliations reported in retrieved sources: not supplied"}`;
      title.append(h, meta);
      if (p.source_url)
        title.append(link("Open source profile ↗", p.source_url));
      content.append(title);
      const stats = document.createElement("div");
      stats.className = "profile-stats";
      for (const [field, label] of [
        ["indexed_publications", "Indexed works"],
        ["eligible_publications", "Eligible works"],
        ["coauthor_count", "Unique coauthors"],
        ["combined_degree", "Combined degree"],
      ]) {
        const cell = document.createElement("div"),
          number = document.createElement("strong"),
          caption = document.createElement("span");
        number.dataset.stat = field;
        const value = d[field];
        number.textContent =
          value == null ? "Not supplied" : String(value);
        caption.textContent = label;
        cell.append(number, caption);
        stats.append(cell);
      }
      content.append(stats);
      const scope = document.createElement("p");
      scope.className = "profile-meta";
      scope.textContent = `${lastUpdatedText()}. Counts refer to this release, not all upstream publications. Active filters: ${filterDescription(d.filters || filters())}. Paper eligibility controls eligible works; the repeat threshold controls coauthor ties.`;
      content.append(scope);
      const actions = document.createElement("div");
      actions.className = "profile-actions";
      [
        ["Use as From", "source"],
        ["Use as To", "target"],
      ].forEach(([text, slot]) => {
        const b = document.createElement("button");
        b.className = "secondary-button";
        b.type = "button";
        b.textContent = text;
        b.addEventListener("click", () => {
          invalidateResults();
          state[slot] = {
            ...p,
            indexed: d.indexed ?? p.indexed ?? false,
            queryable: d.queryable ?? p.queryable ?? false,
          };
          renderPicker(slot);
          syncUrl();
          schedulePreparation([state[slot]], 0, slot);
          showTab("connections");
        });
        actions.append(b);
      });
      const lineage = document.createElement("button");
      lineage.className = "secondary-button";
      lineage.type = "button";
      lineage.textContent = "View doctoral lineage";
      lineage.addEventListener("click", () => setLineageRoot({ ...p }));
      actions.append(lineage);
      const expand = document.createElement("button");
      expand.className = "secondary-button";
      expand.type = "button";
      expand.textContent = "Add graph neighborhood";
      expand.addEventListener("click", () => expandNeighborhood(id));
      actions.append(expand);
      content.append(actions);
      const reach = document.createElement("p");
      reach.className = "profile-meta";
      reach.textContent = `Reachability: ${
        d.reachability
          ? Object.entries(d.reachability)
              .map(
                ([k, v]) =>
                  `${k.replaceAll("_", " ")} ${typeof v === "object" ? JSON.stringify(v) : v}`,
              )
              .join(" · ")
          : "not supplied"
      }`;
      content.append(reach);
      const coll = document.createElement("div"),
        ch = document.createElement("h3"),
        ul = document.createElement("ul");
      coll.className = "profile-section";
      ch.textContent = "Collaborators";
      ul.className = "profile-list";
      (d.collaborators || []).slice(0, 15).forEach((x) => {
        const li = document.createElement("li");
        li.append(
          personButton(
            x.person,
            ` · ${x.shared_works} shared work${x.shared_works === 1 ? "" : "s"}`,
          ),
        );
        ul.append(li);
      });
      if (!ul.children.length)
        ul.textContent = "No eligible coauthor ties under these filters.";
      coll.append(ch, ul);
      content.append(coll);
      const phd = document.createElement("div"),
        ph = document.createElement("h3"),
        pu = document.createElement("ul");
      phd.className = "profile-section";
      ph.textContent = "Documented doctoral ties";
      pu.className = "profile-list";
      ties.forEach((x) => {
        const other = x.adviser === id ? x.student : x.adviser,
          side = x.adviser === id ? "Student" : "Adviser",
          li = document.createElement("li");
        li.append(
          document.createTextNode(`${side}: `),
          personButton(byId(other)),
          document.createTextNode(
            ` · ${x.degree || "doctoral degree"} · ${x.year || "year unknown"} · `,
          ),
          link(x.source_record || "source record", x.source_url),
        );
        pu.append(li);
      });
      if (!pu.children.length)
        pu.textContent = "No doctoral records in this release.";
      phd.append(ph, pu);
      content.append(phd);
      displayCoverage(d.coverage || state.dataset?.coverage);
    } catch (e) {
      if (current()) content.textContent = `Profile unavailable: ${e.message}`;
    }
  }
  // --- Doctoral lineage -----------------------------------------------------
  // Adviser→student records only. A person may have several advisers, so the
  // rendering groups people by generation and lists every documented relation
  // that reached them rather than assuming a single parent.
  const degreeLabels = {
    phd: "PhD",
    doctorate: "Doctorate",
    doctoral: "Doctoral degree",
    habilitation: "Habilitation",
    master: "Master's",
    masters: "Master's",
    diploma: "Diploma",
    bachelor: "Bachelor's",
    bachelors: "Bachelor's",
    other: "Degree kind recorded as other",
  };
  const degreeLabel = (degree) =>
    degree
      ? degreeLabels[String(degree).toLowerCase()] || String(degree)
      : "degree not recorded";
  const lineageDirection = () =>
    $("#lineage-direction").value === "descendants"
      ? "descendants"
      : "ancestors";
  const lineageDepth = () => {
    const value = Number($("#lineage-depth").value);
    return Number.isInteger(value) && value >= 1 && value <= 6 ? value : 3;
  };
  const inspireAuthorUrl = (id) =>
    /^\d+$/.test(String(id ?? ""))
      ? `https://inspirehep.net/authors/${String(id)}`
      : null;
  const generationLabel = (generation, direction, count) => {
    if (generation === 0) return "Selected researcher";
    if (!Number.isFinite(generation)) return "Generation not recorded";
    if (generation === 1)
      return direction === "ancestors"
        ? count === 1
          ? "Adviser"
          : "Advisers"
        : count === 1
          ? "Student"
          : "Students";
    return `${generation} generation${generation === 1 ? "" : "s"} ${direction === "ancestors" ? "back" : "forward"}`;
  };
  const lineageNotice = (message, kind = "") => {
    const box = $("#lineage-message");
    box.className = `notice ${kind}`;
    box.textContent = message;
  };
  function renderLineagePicker() {
    const holder = $("#lineage-selected");
    holder.replaceChildren();
    holder.hidden = !state.lineage;
    if (!state.lineage) return;
    const name = document.createElement("b");
    name.textContent = personName(state.lineage);
    const sub = document.createElement("span");
    sub.textContent = ` · ${state.lineage.id}`;
    holder.append(name, sub);
  }
  function setLineageRoot(person) {
    if (!person?.id) return;
    // A lineage entry without a name must not overwrite a known profile.
    const known = state.people.get(String(person.id));
    state.lineage = person.name ? remember({ ...person }) : known || person;
    $("#lineage-query").value = "";
    $("#lineage-results").replaceChildren();
    $("#lineage-results").classList.remove("inline-search-notice");
    $("#lineage-query").setAttribute("aria-expanded", "false");
    renderLineagePicker();
    $("#person-panel").classList.add("hidden");
    showTab("lineage");
    loadLineage();
  }
  function clearLineage() {
    state.lineageRequest++;
    state.lineage = null;
    $("#lineage-query").value = "";
    $("#lineage-results").replaceChildren();
    $("#lineage-results").classList.remove("inline-search-notice");
    $("#lineage-query").setAttribute("aria-expanded", "false");
    renderLineagePicker();
    $("#lineage-generations").replaceChildren();
    lineageNotice("", "hidden");
    $("#lineage-output").classList.add("hidden");
    $("#lineage-empty").classList.remove("hidden");
    setLoading($("#lineage-run"), false);
  }
  function lineagePersonButton(person) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "person-link";
    b.textContent = personName(person);
    b.title = `Show the doctoral lineage of ${personName(person)}`;
    b.addEventListener("click", () => setLineageRoot(person));
    return b;
  }
  function lineageRelationRow(edge, lookup, direction) {
    const li = document.createElement("li");
    li.className = "lineage-relation";
    const counterpart = lookup(
      direction === "ancestors" ? edge.student : edge.adviser,
    );
    li.append(
      document.createTextNode(
        direction === "ancestors" ? "Adviser of " : "Student of ",
      ),
      lineagePersonButton(counterpart),
      document.createTextNode(` · ${degreeLabel(edge.degree)} · `),
    );
    const tag = document.createElement("span");
    tag.className = `status ${edge.curated === true ? "curated" : "uncurated"}`;
    tag.textContent =
      edge.curated === true ? "INSPIRE-confirmed" : "not curator-confirmed";
    li.append(tag);
    if (edge.source_record != null && edge.source_record !== "") {
      const record = document.createElement("span");
      record.className = "lineage-id";
      record.textContent = ` · source record ${edge.source_record}`;
      li.append(record);
    }
    return li;
  }
  function lineagePersonCard(person, relations, lookup, direction, isRoot) {
    const li = document.createElement("li");
    li.className = "lineage-person";
    const head = document.createElement("div");
    head.className = "lineage-person-head";
    head.append(lineagePersonButton(person));
    const id = document.createElement("span");
    id.className = "lineage-id";
    id.textContent = `INSPIRE ${person.id}`;
    head.append(id);
    const href = person.source_url || inspireAuthorUrl(person.id);
    if (href && safeHref(href)) head.append(link("Profile ↗", href));
    li.append(head);
    if (person.details_unavailable === true) {
      const note = document.createElement("p");
      note.className = "lineage-note";
      const reason = String(person.reason || "").trim();
      note.textContent = `Name not retrieved${reason ? `: ${reason.replace(/[.;:,]$/, "")}` : ""}. The INSPIRE identifier is shown instead.`;
      li.append(note);
    }
    if (relations.length > 1) {
      const note = document.createElement("p");
      note.className = "lineage-note";
      note.textContent =
        direction === "ancestors"
          ? `Documented as adviser to ${relations.length} people shown here.`
          : `Documented as student of ${relations.length} people shown here.`;
      li.append(note);
    }
    if (isRoot) return li;
    const list = document.createElement("ul");
    list.className = "lineage-relations";
    relations.forEach((edge) =>
      list.append(lineageRelationRow(edge, lookup, direction)),
    );
    if (!relations.length) {
      const empty = document.createElement("li");
      empty.className = "lineage-relation";
      empty.textContent =
        "No relation record accompanied this person in the response.";
      list.append(empty);
    }
    li.append(list);
    return li;
  }
  function lineageGroup(generation, entries, direction, lookup, relations) {
    const section = document.createElement("section");
    section.className = `lineage-generation${generation === 0 ? " is-root" : ""}`;
    const headingId = `lineage-gen-${Number.isFinite(generation) ? generation : "unknown"}`;
    section.setAttribute("aria-labelledby", headingId);
    const heading = document.createElement("h3");
    heading.id = headingId;
    heading.textContent = `${generationLabel(generation, direction, entries.length)} · ${entries.length} ${entries.length === 1 ? "person" : "people"}`;
    section.append(heading);
    const list = document.createElement("ul");
    list.className = "lineage-people";
    entries.forEach((person) =>
      list.append(
        lineagePersonCard(
          person,
          relations.get(String(person.id)) || [],
          lookup,
          direction,
          generation === 0,
        ),
      ),
    );
    section.append(list);
    return section;
  }
  function renderLineage(data, context) {
    const { person, direction, depth } = context;
    const holder = $("#lineage-generations");
    holder.replaceChildren();
    const status = data.status || "ok";
    if (status !== "ok") {
      $("#lineage-heading").textContent =
        status === "unavailable"
          ? "Doctoral lineage is not available"
          : "No doctoral record found";
      $("#lineage-meta").textContent =
        status === "unavailable"
          ? "Nothing is claimed about this researcher's advisers or students."
          : `${personName(person)} · INSPIRE ${person.id}`;
      lineageNotice(
        data.message ||
          (status === "unavailable"
            ? "Doctoral lineage records are not configured in this release."
            : "This researcher was not found in the doctoral records of this release. That silence describes the records, not the researcher."),
      );
      return;
    }
    const root = data.person && data.person.id != null ? data.person : person;
    if (root.name) remember({ ...root });
    const shown =
      data.direction === "descendants"
        ? "descendants"
        : data.direction === "ancestors"
          ? "ancestors"
          : direction;
    $("#lineage-heading").textContent =
      shown === "ancestors"
        ? `Doctoral ancestors of ${personName(root)}`
        : `Doctoral descendants of ${personName(root)}`;
    const people = Array.isArray(data.people) ? data.people : [];
    const edges = Array.isArray(data.edges) ? data.edges : [];
    const known = new Map();
    people.forEach((p) => {
      if (p && p.id != null && !known.has(String(p.id)))
        known.set(String(p.id), p);
    });
    const lookup = (id) =>
      known.get(String(id)) ||
      (String(id) === String(root.id) ? root : null) ||
      state.people.get(String(id)) || { id: String(id) };
    // The near side of an edge is the person further from the root: their
    // adviser links for ancestors, their student links for descendants.
    const nearKey = shown === "ancestors" ? "adviser" : "student";
    const relations = new Map();
    edges.forEach((edge) => {
      if (!edge || edge[nearKey] == null) return;
      const key = String(edge[nearKey]);
      if (!relations.has(key)) relations.set(key, []);
      relations.get(key).push(edge);
    });
    const groups = new Map();
    const seen = new Map();
    people.forEach((p) => {
      if (!p || p.id == null) return;
      const raw = Number(p.generation);
      const generation = Number.isFinite(raw) && raw > 0 ? raw : NaN;
      const key = Number.isFinite(generation) ? generation : "unknown";
      if (!groups.has(key)) {
        groups.set(key, []);
        seen.set(key, new Set());
      }
      if (seen.get(key).has(String(p.id))) return;
      seen.get(key).add(String(p.id));
      groups.get(key).push(p);
    });
    const ordered = [...groups.keys()]
      .filter((k) => k !== "unknown")
      .sort((a, b) => a - b);
    if (groups.has("unknown")) ordered.push("unknown");
    holder.append(
      lineageGroup(0, [root], shown, lookup, new Map()),
      ...ordered.map((key) =>
        lineageGroup(
          key === "unknown" ? NaN : key,
          groups
            .get(key)
            .slice()
            .sort((a, b) => personName(a).localeCompare(personName(b))),
          shown,
          lookup,
          relations,
        ),
      ),
    );
    const total = [...groups.values()].reduce((n, list) => n + list.length, 0);
    const curated = edges.filter((edge) => edge.curated === true).length;
    $("#lineage-meta").textContent =
      `${lastUpdatedText()} · ${shown === "ancestors" ? "adviser" : "student"} records to ${data.depth ?? depth} generation${(data.depth ?? depth) === 1 ? "" : "s"} · ` +
      `${total} ${total === 1 ? "person" : "people"} · ${edges.length} documented relation${edges.length === 1 ? "" : "s"}, ` +
      `${curated} INSPIRE-confirmed · ${data.version ? `records ${data.version}` : "record version not supplied"}`;
    if (data.truncated === true)
      lineageNotice(
        "This lineage is truncated: more documented relations exist than are shown. Open a person shown here to continue from them, or reduce the depth.",
        "warning",
      );
    else if (!total)
      lineageNotice(
        shown === "ancestors"
          ? "No documented adviser is recorded for this researcher in this release. That is a gap in the records, not proof that none exists."
          : "No documented student is recorded for this researcher in this release. That is a gap in the records, not proof that none exists.",
      );
    else lineageNotice("", "hidden");
  }
  async function loadLineage() {
    const person = state.lineage;
    if (!person?.id) {
      clearLineage();
      return;
    }
    const direction = lineageDirection(),
      depth = lineageDepth(),
      request = ++state.lineageRequest,
      current = () =>
        request === state.lineageRequest && state.lineage === person;
    const button = $("#lineage-run");
    setLoading(button, true, "Loading…");
    $("#lineage-empty").classList.add("hidden");
    $("#lineage-output").classList.remove("hidden");
    $("#lineage-generations").replaceChildren();
    lineageNotice("", "hidden");
    $("#lineage-heading").textContent =
      direction === "ancestors"
        ? `Doctoral ancestors of ${personName(person)}`
        : `Doctoral descendants of ${personName(person)}`;
    $("#lineage-meta").textContent = "Loading documented doctoral records…";
    try {
      const u = new URL(
        `/api/ancestry/${encodeURIComponent(person.id)}`,
        location.origin,
      );
      u.searchParams.set("direction", direction);
      u.searchParams.set("depth", String(depth));
      const data = await api(u.pathname + "?" + u.searchParams.toString());
      if (!current()) return;
      renderLineage(data, { person, direction, depth });
    } catch (e) {
      if (!current()) return;
      const body = e.body || {};
      if (body.status === "unavailable" || body.status === "not_found")
        renderLineage(body, { person, direction, depth });
      else {
        $("#lineage-generations").replaceChildren();
        $("#lineage-meta").textContent =
          "No lineage is shown for this request.";
        lineageNotice(`Doctoral lineage is unavailable: ${e.message}`, "error");
      }
    } finally {
      if (current()) setLoading(button, false);
    }
  }
  function setupLineageSearch() {
    const input = $("#lineage-query");
    input.addEventListener("input", () => {
      state.searches.lineage = {
        query: input.value,
        token: (state.searches.lineage?.token || 0) + 1,
      };
      clearTimeout(state.timers.lineage);
      state.timers.lineage = setTimeout(() => searchPeople("lineage"), 220);
    });
    input.addEventListener("keydown", (e) => {
      const buttons = $$(
        '.search-result[role="option"]',
        $("#lineage-results"),
      );
      if (e.key === "Escape") $("#lineage-results").replaceChildren();
      if (e.key === "ArrowDown" && buttons[0]) {
        e.preventDefault();
        buttons[0].focus();
      }
    });
  }

  function init() {
    restoreUrl();
    setupSearch("source");
    setupSearch("target");
    setupLineageSearch();
    document.addEventListener("pointerdown", (event) => {
      ["source", "target", "lineage"].forEach((which) => {
        const field = $(`#${which}-query`).closest(".identity-field");
        if (!field.contains(event.target)) {
          const menu = $(`#${which}-results`);
          if (!menu.classList.contains("inline-search-notice")) {
            menu.replaceChildren();
            $(`#${which}-query`).setAttribute("aria-expanded", "false");
          }
        }
      });
    });
    $("#search-form").addEventListener("submit", (e) => {
      e.preventDefault();
      findPath();
    });
    $("#lineage-form").addEventListener("submit", (e) => {
      e.preventDefault();
      loadLineage();
    });
    ["lineage-direction", "lineage-depth"].forEach((id) =>
      $("#" + id).addEventListener("change", () => {
        if (state.lineage) loadLineage();
      }),
    );
    $$(".clear-picker").forEach((b) =>
      b.addEventListener("click", () => clearPicker(b.dataset.clear)),
    );
    $("#swap-people").addEventListener("click", () => {
      invalidateResults();
      [state.source, state.target] = [state.target, state.source];
      renderPicker("source");
      renderPicker("target");
      syncUrl();
    });
    $("#paper-team-size").addEventListener("change", () => {
      applyTeamSizePreset($("#paper-team-size").value);
      updateFilterSummary();
    });
    ["min-authors", "max-authors", "min-authors-custom", "max-authors-custom"].forEach((id) =>
      $("#" + id).addEventListener("change", () => {
        syncTeamSizeFromBounds();
        updateFilterSummary();
      }),
    );
    $$(".tab").forEach((b) =>
      b.addEventListener("click", () => showTab(b.dataset.tab)),
    );
    [
      "min-shared",
      "year-start",
      "year-end",
      "genealogy",
      "min-shared-custom",
    ].forEach((id) =>
      $("#" + id).addEventListener("change", () => updateFilterSummary()),
    );
    $("#copy-share").addEventListener("click", copyShare);
    $("#deep-stop").addEventListener("click", stopDeepSearch);
    $("#deep-continue").addEventListener("click", () => {
      if (state.deepJob) continueDeepSearch(state.deepJob);
    });
    $("#route-update-show").addEventListener("click", () => state.routeOffer?.apply());
    $("#export-json").addEventListener("click", jsonExport);
    $("#export-svg").addEventListener("click", svgExport);
    $("#close-profile").addEventListener("click", () => {
      state.profileRequest++;
      $("#person-panel").classList.add("hidden");
    });
    setupGraphInteractions();
    const graphStage = $("#graph-stage");
    let graphSize = "";
    const fitGraphOnResize = () => {
      const size = `${graphStage.clientWidth}x${graphStage.clientHeight}`;
      if (size === graphSize) return;
      graphSize = size;
      if (state.graph.nodes.size) {
        fitGraph();
        renderGraph();
      }
    };
    if (window.ResizeObserver) {
      new ResizeObserver(fitGraphOnResize).observe(graphStage);
    } else {
      window.addEventListener("resize", fitGraphOnResize);
    }
    fitGraphOnResize();
    registerModelContext();
    loadDataset();
  }
  document.addEventListener("DOMContentLoaded", init);
})();
