/* Shared XUYI Blog card pager. All published links remain in source HTML. */
(() => {
  "use strict";
  const grid = document.querySelector(".blog-listing__grid");
  if (!grid) return;
  const cards = [...grid.children].filter(card => card.matches("article.news-card"));
  const PAGE_SIZE = 12;
  if (cards.length <= PAGE_SIZE) return;

  const labels = {
    en: {nav:"Blog pages",prev:"Previous",next:"Next",show:"Showing",of:"of",guides:"guides",page:"Page"},
    es: {nav:"Páginas del blog",prev:"Anterior",next:"Siguiente",show:"Mostrando",of:"de",guides:"guías",page:"Página"},
    pt: {nav:"Páginas do blog",prev:"Anterior",next:"Próxima",show:"Mostrando",of:"de",guides:"guias",page:"Página"},
    ru: {nav:"Страницы блога",prev:"Назад",next:"Вперёд",show:"Показано",of:"из",guides:"статей",page:"Страница"},
    tr: {nav:"Blog sayfaları",prev:"Önceki",next:"Sonraki",show:"Gösterilen",of:"/",guides:"rehber",page:"Sayfa"}
  };
  const locale = (document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const t = labels[locale] || labels.en;
  const count = Math.ceil(cards.length / PAGE_SIZE);
  const shell = grid.parentElement;
  grid.id ||= "blog-card-grid";
  const summary = document.createElement("p");
  summary.className = "blog-pager__summary";
  summary.setAttribute("role", "status");
  summary.setAttribute("aria-live", "polite");
  const nav = document.createElement("nav");
  nav.className = "blog-pager";
  nav.setAttribute("aria-label", t.nav);
  shell.appendChild(summary);
  shell.appendChild(nav);

  function currentPage() {
    const raw = new URL(window.location.href).searchParams.get("page");
    const number = raw && /^[1-9]\d*$/.test(raw) ? Number(raw) : 1;
    return Number.isSafeInteger(number) ? Math.max(1, Math.min(count, number)) : 1;
  }
  function linkFor(page) {
    const url = new URL(window.location.href);
    if (page === 1) url.searchParams.delete("page");
    else url.searchParams.set("page", String(page));
    return url.pathname + url.search;
  }
  function go(page) {
    if (page < 1 || page > count) return;
    window.history.pushState({xuyiBlogPage:page}, "", linkFor(page));
    render(page);
    grid.scrollIntoView({block:"start",behavior:"instant"});
  }
  function appendLink(page, label, kind) {
    const a = document.createElement("a");
    a.className = "blog-pager__link" + (kind ? " blog-pager__link--" + kind : "");
    a.href = linkFor(page);
    a.textContent = label;
    if (!kind && page === selected) a.setAttribute("aria-current", "page");
    a.addEventListener("click", event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey ||
          event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      go(page);
    });
    nav.appendChild(a);
  }
  let selected = 1;
  function render(page) {
    selected = page;
    const start = (page - 1) * PAGE_SIZE;
    cards.forEach((card, index) => {
      card.hidden = index < start || index >= start + PAGE_SIZE;
      const img = card.querySelector("img");
      if (img) img.loading = "lazy";
    });
    summary.textContent = t.show + " " + (start + 1) + "–" +
      Math.min(start + PAGE_SIZE, cards.length) + " " + t.of + " " +
      cards.length + " " + t.guides;
    nav.replaceChildren();
    if (page > 1) appendLink(page - 1, "← " + t.prev, "prev");
    const numbers = count <= 7
      ? Array.from({length:count}, (_, i) => i + 1)
      : [...new Set([1,2,page-1,page,page+1,count-1,count]
          .filter(n => n >= 1 && n <= count))].sort((a,b) => a-b);
    let last = 0;
    for (const number of numbers) {
      if (last && number - last > 1) {
        const gap = document.createElement("span");
        gap.className = "blog-pager__ellipsis";
        gap.textContent = "…";
        gap.setAttribute("aria-hidden", "true");
        nav.appendChild(gap);
      }
      appendLink(number, String(number), "");
      last = number;
    }
    if (page < count) appendLink(page + 1, t.next + " →", "next");
    nav.setAttribute("aria-label", t.nav + " — " + t.page + " " + page + " / " + count);
  }
  render(currentPage());
  window.addEventListener("popstate", () => render(currentPage()));
})();