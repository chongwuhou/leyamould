(() => {
  const TOKEN_KEY = "xuyiAdminToken";
  const FORMS_API = "/api/admin/forms";
  const SMTP_API = "/api/admin/smtp";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" })[ch]);
  let loadedOnce = false;
  let searchTimer;

  const token = () => sessionStorage.getItem(TOKEN_KEY) || "";
  async function api(url, method = "GET", body = null) {
    const response = await fetch(url, {
      method,
      headers: {
        ...(body ? { "content-type": "application/json" } : {}),
        authorization: "Bearer " + token()
      },
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store"
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || ("HTTP " + response.status));
    return data;
  }

  async function loadForms() {
    if (!token() || !$("#forms-body")) return;
    const statusEl = $("#forms-status");
    const params = new URLSearchParams();
    const q = $("#form-search")?.value.trim() || "";
    const status = $("#form-status-filter")?.value || "";
    if (q) params.set("q", q);
    if (status) params.set("status", status);
    params.set("limit", "100");
    try {
      const state = await api(FORMS_API + "?" + params.toString());
      renderStats(state.stats || {});
      renderForms(state.submissions || []);
      if (statusEl) statusEl.textContent = "已显示 " + (state.submissions?.length || 0) + " 条最近询盘。";
    } catch (error) {
      if (statusEl) statusEl.textContent = "询盘读取失败：" + error.message;
    }
  }

  function renderStats(stats) {
    const el = $("#form-stats");
    if (!el) return;
    const items = [
      ["Total", stats.total || 0],
      ["New", stats.new_count || 0],
      ["Read", stats.read_count || 0],
      ["Replied", stats.replied_count || 0],
      ["Spam", stats.spam_count || 0]
    ];
    el.innerHTML = items.map(([label, value]) =>
      '<div><span>' + esc(label) + '</span><strong>' + Number(value || 0) + '</strong></div>'
    ).join("");
  }

  function renderForms(rows) {
    const body = $("#forms-body");
    if (!body) return;
    body.innerHTML = rows.length ? rows.map((item) => {
      const who = [item.name, item.company].filter(Boolean).join(" · ");
      const contact = [item.email, item.phone].filter(Boolean).join(" / ");
      const model = [item.brand, item.reference].filter(Boolean).join(" ");
      const mail = item.smtp_status || "pending";
      const error = item.smtp_error ? '<br><span class="muted" title="' + esc(item.smtp_error) + '">有错误</span>' : "";
      return '<tr>' +
        '<td>' + esc(item.created_at || "") + '<br><span class="muted">' + esc(item.locale || "") + ' · ' + esc(item.source || "") + '</span></td>' +
        '<td><strong>' + esc(who || "—") + '</strong><br><span class="muted">' + esc(contact || "—") + '</span></td>' +
        '<td><strong>' + esc(model || "—") + '</strong></td>' +
        '<td><div class="lead-preview">' + esc(item.requirements || "—") + '</div></td>' +
        '<td><span class="status ' + esc(item.status || "new") + '">' + esc(item.status || "new") + '</span></td>' +
        '<td><span class="mail-state ' + esc(mail) + '">' + esc(mail) + '</span>' + error + '</td>' +
        '<td><button class="btn small ghost open-submission" data-id="' + esc(item.id) + '">查看</button></td>' +
      '</tr>';
    }).join("") : '<tr><td colspan="7">暂无询盘。</td></tr>';
    $$(".open-submission").forEach((button) => button.addEventListener("click", () => openSubmission(button.dataset.id)));
  }

  async function openSubmission(id) {
    const status = $("#forms-status");
    try {
      const editor = $("#submission-editor");
      const title = $("#submission-editor-title");
      const content = $("#submission-editor-content");
      if (!editor || !title || !content || typeof editor.showModal !== "function") {
        throw new Error("询盘详情窗口未加载，请刷新后台页面后重试。");
      }
      const data = await api(FORMS_API + "?id=" + encodeURIComponent(id));
      const s = data.submission || {};
      let extra = {};
      try { extra = JSON.parse(s.fields_json || "{}"); } catch {}
      title.textContent = [s.brand, s.reference].filter(Boolean).join(" ") || s.name || "Inquiry";
      content.innerHTML =
        '<div class="submission-grid">' +
          detail("ID", s.id) +
          detail("时间", s.created_at) +
          detail("姓名 / 公司", [s.name,s.company].filter(Boolean).join(" · ") || "—") +
          detail("邮箱 / 电话", [s.email,s.phone].filter(Boolean).join(" / ") || "—") +
          detail("品牌 / 型号", [s.brand,s.reference].filter(Boolean).join(" ") || "—") +
          detail("应用", s.equipment || "—") +
          detail("页面", s.page_url || "—") +
          detail("来源 / 语言", (s.source || "—") + " / " + (s.locale || "—")) +
          detail("询盘内容", s.requirements || "—", true) +
          detail("其他字段", JSON.stringify(extra, null, 2), true) +
          detail("SMTP", s.smtp_status || "pending") +
          detail("SMTP 错误", s.smtp_error || "—") +
          detail("IP", s.ip || "—") +
          detail("User Agent", s.user_agent || "—") +
        '</div>' +
        '<div class="submission-actions">' +
          ["new","read","replied","spam"].map((value) =>
            '<button class="btn ' + (value === s.status ? "primary" : "ghost") + ' submission-status-btn" data-status="' + value + '">' + value + '</button>'
          ).join("") +
          ((s.smtp_status !== "sent" && s.status !== "spam") ?
            '<button class="btn ghost submission-retry-email-btn" type="button">补发邮件通知</button>' : '') +
          '<button class="btn ghost submission-delete-btn">删除</button>' +
          '<span id="submission-action-status" class="muted"></span>' +
        '</div>';
      $(".submission-retry-email-btn")?.addEventListener("click", async (event) => {
        const button = event.currentTarget;
        const msg = $("#submission-action-status");
        button.disabled = true;
        if (msg) msg.textContent = "正在发送通知…";
        try {
          await api(FORMS_API, "POST", { action: "retry_notification", id: s.id });
          if (msg) msg.textContent = "SMTP 已接受该邮件。请检查收件箱。";
          button.remove();
          await loadForms();
        } catch (error) {
          if (msg) msg.textContent = "补发失败：" + error.message;
          button.disabled = false;
        }
      });
      $$(".submission-status-btn").forEach((button) => button.addEventListener("click", async () => {
        const msg = $("#submission-action-status");
        try {
          await api(FORMS_API, "POST", { action: "set_status", id: s.id, status: button.dataset.status });
          if (msg) msg.textContent = "状态已更新。";
          $("#submission-editor").close();
          await loadForms();
        } catch (error) {
          if (msg) msg.textContent = "更新失败：" + error.message;
        }
      }));
      $(".submission-delete-btn")?.addEventListener("click", async () => {
        if (!confirm("确认删除这条询盘？此操作不可恢复。")) return;
        const msg = $("#submission-action-status");
        try {
          await api(FORMS_API + "?id=" + encodeURIComponent(s.id), "DELETE");
          $("#submission-editor").close();
          await loadForms();
        } catch (error) {
          if (msg) msg.textContent = "删除失败：" + error.message;
        }
      });
      editor.showModal();
    } catch (error) {
      if (status) status.textContent = "询盘详情读取失败：" + error.message;
    }
  }

  function detail(label, value, wide = false) {
    return '<div class="' + (wide ? "submission-message" : "") + '"><span>' + esc(label) + '</span><pre>' + esc(value || "—") + '</pre></div>';
  }

  async function loadSmtp() {
    if (!token() || !$("#smtp-host")) return;
    const status = $("#smtp-status");
    try {
      const data = await api(SMTP_API);
      const s = data.settings || {};
      $("#smtp-enabled").checked = Boolean(s.enabled);
      $("#smtp-host").value = s.host || "";
      $("#smtp-port").value = Number(s.port || 465);
      $("#smtp-security").value = s.security || "ssl";
      $("#smtp-username").value = s.username || "";
      $("#smtp-password").value = "";
      $("#smtp-password").placeholder = s.passwordConfigured ? "已保存密码；留空 = 不修改" : "尚未保存密码";
      $("#smtp-from-name").value = s.fromName || "XUYI Bottles Website";
      let defaultEmail = "Janey@xuyibottles.com";
      try {
        const publicResponse = await fetch("/api/site-settings", { cache: "no-store" });
        if (publicResponse.ok) {
          const site = await publicResponse.json();
          const contact = (site.contacts || []).find((c) => c.enabled && c.isDefault) ||
                          (site.contacts || []).find((c) => c.enabled);
          if (contact?.email) defaultEmail = contact.email;
        }
      } catch { /* A missing public setting must never block admin SMTP management. */ }
      $("#smtp-from-email").value = s.fromEmail || defaultEmail;
      $("#smtp-to-emails").value = s.toEmails || defaultEmail;
      $("#smtp-reply-to").value = s.replyToMode || "visitor";
      $("#smtp-subject").value = s.subjectTemplate || "Website inquiry: {{reference}} {{name}}";
      $("#smtp-state-badge").textContent = !s.enabled ? "SMTP 未启用" : s.verifiedAt ? "SMTP 已测试" : "SMTP 待测试";
      if (status) status.textContent = !s.enabled
        ? "在线询盘表单暂不接收提交。请配置 SMTP 并实际发送测试邮件；客户仍可通过邮箱或 WhatsApp 联系。"
        : s.verifiedAt ? "SMTP 已通过发送测试；在线询盘表单已具备接收条件。请确认测试邮件确实进入收件箱。"
        : "SMTP 尚未通过发送测试；在线询盘表单仍关闭。保存后点击发送测试邮件。";
    } catch (error) {
      if (status) status.textContent = "SMTP 设置读取失败：" + error.message;
      $("#smtp-state-badge").textContent = "读取失败";
    }
  }

  function smtpSettings() {
    return {
      enabled: $("#smtp-enabled").checked,
      host: $("#smtp-host").value.trim(),
      port: Number($("#smtp-port").value || 465),
      security: $("#smtp-security").value,
      username: $("#smtp-username").value.trim(),
      password: $("#smtp-password").value,
      fromName: $("#smtp-from-name").value.trim(),
      fromEmail: $("#smtp-from-email").value.trim(),
      toEmails: $("#smtp-to-emails").value.trim(),
      replyToMode: $("#smtp-reply-to").value,
      subjectTemplate: $("#smtp-subject").value.trim()
    };
  }

  async function saveSmtp() {
    const button = $("#smtp-save");
    const status = $("#smtp-status");
    button.disabled = true;
    try {
      await api(SMTP_API, "POST", { action: "save", settings: smtpSettings() });
      status.textContent = "SMTP 设置已保存。";
      await loadSmtp();
    } catch (error) {
      status.textContent = "保存失败：" + error.message;
    } finally {
      button.disabled = false;
    }
  }

  async function testSmtp() {
    const button = $("#smtp-test");
    const status = $("#smtp-status");
    button.disabled = true;
    status.textContent = "正在连接 SMTP 并发送测试邮件…";
    try {
      await api(SMTP_API, "POST", { action: "test" });
      await loadSmtp();
      status.textContent = "测试邮件已由 SMTP 服务器接受，在线询盘表单可启用。请检查实际收件箱。";
    } catch (error) {
      status.textContent = "SMTP 测试失败：" + error.message;
    } finally {
      button.disabled = false;
    }
  }

  async function loadAll() {
    if (!token()) return;
    await Promise.all([loadForms(), loadSmtp()]);
    loadedOnce = true;
  }

  $("#forms-refresh")?.addEventListener("click", loadForms);
  $("#form-status-filter")?.addEventListener("change", loadForms);
  $("#form-search")?.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadForms, 350);
  });
  $("#smtp-save")?.addEventListener("click", saveSmtp);
  $("#smtp-test")?.addEventListener("click", testSmtp);
  $("#token-form")?.addEventListener("submit", () => setTimeout(loadAll, 1200));
  $("#refresh-btn")?.addEventListener("click", () => setTimeout(loadAll, 50));
  $("#logout-btn")?.addEventListener("click", () => { loadedOnce = false; });

  const app = $("#admin-app");
  if (app) {
    new MutationObserver(() => {
      if (!app.classList.contains("hidden") && token() && !loadedOnce) loadAll();
    }).observe(app, { attributes: true, attributeFilter: ["class"] });
  }
  if (token()) setTimeout(loadAll, 250);
})();
