/* Small authenticated CRUD panel for the public YouTube video gallery. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const token = () => sessionStorage.getItem("xuyiAdminToken") || "";
  const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
  let items = [];
  const status = message => { const el = $("youtube-video-status"); if (el) el.textContent = message; };
  async function call(body) {
    if (!token()) throw new Error("请先登录网站后台");
    const options = { method: body ? "POST" : "GET", headers: { authorization: "Bearer " + token() }, cache: "no-store" };
    if (body) { options.headers["content-type"] = "application/json"; options.body = JSON.stringify(body); }
    const response = await fetch("/api/admin/youtube-videos", options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "HTTP " + response.status);
    return data;
  }
  function render() {
    const root = $("youtube-video-list");
    if (!root) return;
    root.innerHTML = items.length ? items.map(item =>
      '<article class="blog-admin-row"><div><strong>' + esc(item.title || "LEYA MOULD video") + '</strong><small>' + esc(item.youtubeUrl) + ' · ' + esc(item.publishedAt || item.createdAt || "") + '</small></div><button type="button" class="btn ghost" data-youtube-delete="' + esc(item.id) + '">删除</button></article>'
    ).join("") : '<p class="muted">暂无视频链接。</p>';
  }
  async function load() {
    status("正在读取 YouTube 视频…");
    try { const data = await call(); items = data.items || []; render(); status("已读取 " + items.length + " 条视频链接。"); }
    catch (error) { status("读取失败：" + error.message); }
  }
  $("youtube-video-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const input = $("youtube-video-url");
    const button = $("youtube-video-save");
    const url = input.value.trim();
    if (!url) return;
    button.disabled = true;
    try { await call({ action: "save", youtubeUrl: url }); input.value = ""; await load(); status("视频链接已增加。"); }
    catch (error) { status("保存失败：" + error.message); }
    finally { button.disabled = false; }
  });
  $("youtube-video-refresh")?.addEventListener("click", load);
  $("youtube-video-list")?.addEventListener("click", async event => {
    const button = event.target.closest("[data-youtube-delete]");
    if (!button) return;
    if (!confirm("确认删除这个 YouTube 视频链接？")) return;
    button.disabled = true;
    try { await call({ action: "delete", id: button.dataset.youtubeDelete }); await load(); status("视频链接已删除。"); }
    catch (error) { status("删除失败：" + error.message); button.disabled = false; }
  });
  document.querySelector('[data-admin-target="videos"]')?.addEventListener("click", load);
})();

