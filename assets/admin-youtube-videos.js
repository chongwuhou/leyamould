/* Small authenticated CRUD panel for the public YouTube video gallery. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const token = () => sessionStorage.getItem("xuyiAdminToken") || "";
  const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
  let items = [];
  let editingId = "";
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
  function formatDateTime(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value).slice(0, 16);
    const pad = number => String(number).padStart(2, "0");
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate()) +
      "T" + pad(date.getHours()) + ":" + pad(date.getMinutes());
  }
  function resetForm() {
    editingId = "";
    $("youtube-video-url").value = "";
    $("youtube-video-title-en").value = "";
    $("youtube-video-title-es").value = "";
    $("youtube-video-published-at").value = "";
    $("youtube-video-save").textContent = "+ 增加视频";
    $("youtube-video-cancel").hidden = true;
  }
  function startEdit(item) {
    editingId = item.id;
    $("youtube-video-url").value = item.youtubeUrl || "";
    $("youtube-video-title-en").value = item.titleEn || item.title || "";
    $("youtube-video-title-es").value = item.titleEs || "";
    $("youtube-video-published-at").value = formatDateTime(item.publishedAt || item.createdAt);
    $("youtube-video-save").textContent = "保存修改";
    $("youtube-video-cancel").hidden = false;
    $("youtube-video-form")?.scrollIntoView({ behavior: "smooth", block: "center" });
    status("正在编辑：" + (item.titleEn || item.title || "视频"));
  }
  function render() {
    const root = $("youtube-video-list");
    if (!root) return;
    root.innerHTML = items.length ? items.map(item =>
      '<article class="blog-admin-row"><div><strong>' + esc(item.titleEn || item.title || "LEYA MOULD video") + '</strong><small>ES: ' + esc(item.titleEs || "回退英文") + ' · ' + esc(item.youtubeUrl) + ' · ' + esc(item.publishedAt || item.createdAt || "") + '</small></div><div class="row-actions"><button type="button" class="btn ghost" data-youtube-edit="' + esc(item.id) + '">编辑</button><button type="button" class="btn ghost" data-youtube-delete="' + esc(item.id) + '">删除</button></div></article>'
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
    const titleEn = $("youtube-video-title-en");
    const titleEs = $("youtube-video-title-es");
    const publishedAt = $("youtube-video-published-at");
    const button = $("youtube-video-save");
    const url = input.value.trim();
    if (!url || !titleEn.value.trim() || !publishedAt.value) { status("请填写 YouTube 地址、英文标题和发布时间。"); return; }
    const wasEditing = Boolean(editingId);
    button.disabled = true;
    try {
      await call({ action: "save", id: editingId || undefined, youtubeUrl: url, titleEn: titleEn.value.trim(), titleEs: titleEs.value.trim(), publishedAt: publishedAt.value });
      resetForm();
      await load();
      status(wasEditing ? "视频链接已更新。" : "视频链接已增加。");
    } catch (error) { status("保存失败：" + error.message); }
    finally { button.disabled = false; }
  });
  $("youtube-video-cancel")?.addEventListener("click", () => { resetForm(); status("已取消编辑，可继续增加视频。"); });
  $("youtube-video-refresh")?.addEventListener("click", load);
  $("youtube-video-list")?.addEventListener("click", async event => {
    const editButton = event.target.closest("[data-youtube-edit]");
    if (editButton) {
      const item = items.find(row => row.id === editButton.dataset.youtubeEdit);
      if (item) startEdit(item);
      return;
    }
    const deleteButton = event.target.closest("[data-youtube-delete]");
    if (!deleteButton) return;
    if (!confirm("确认删除这个 YouTube 视频链接？")) return;
    deleteButton.disabled = true;
    try {
      await call({ action: "delete", id: deleteButton.dataset.youtubeDelete });
      if (editingId === deleteButton.dataset.youtubeDelete) resetForm();
      await load();
      status("视频链接已删除。");
    } catch (error) { status("删除失败：" + error.message); deleteButton.disabled = false; }
  });
  document.querySelector('[data-admin-target="videos"]')?.addEventListener("click", load);
})();

