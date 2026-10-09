// XUYI inquiry readiness regression tests. Reuses the actual Demalong-adapted
// forms helper; only the Cloudflare SMTP socket import is stubbed for Node tests.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const source = readFileSync(new URL("../functions/_shared/forms.js", import.meta.url), "utf8");
const nodeSource = source.replace(
  'import { connect } from "cloudflare:sockets";',
  'const connect = () => { throw new Error("SMTP is not used in unit tests"); };'
);
assert.notEqual(source, nodeSource, "Workers socket dependency must be stubbed");
const { isInquiryFormReady, ensureFormSchema } = await import(
  "data:text/javascript;base64," + Buffer.from(nodeSource).toString("base64")
);
const readyRecord = {
  enabled: 1, host: "smtp.example.com", username: "sales",
  password_ciphertext: "encrypted", from_email: "sales@example.com",
  to_emails: "sales@example.com", smtp_verified_at: "2026-10-09 00:00:00"
};
const dbFor = (record) => ({
  prepare: () => ({ first: async () => record })
});
const env = { FORM_SETTINGS_KEY: "set" };
assert.equal(await isInquiryFormReady(null, env), false);
assert.equal(await isInquiryFormReady(dbFor(null), env), false);
assert.equal(await isInquiryFormReady(dbFor({...readyRecord, enabled:0}), env), false);
assert.equal(await isInquiryFormReady(dbFor({...readyRecord, smtp_verified_at:null}), env), false);
assert.equal(await isInquiryFormReady(dbFor(readyRecord), {}), false);
assert.equal(await isInquiryFormReady(dbFor({...readyRecord, host:""}), env), false);
assert.equal(await isInquiryFormReady(dbFor(readyRecord), env), true);
assert.equal(await isInquiryFormReady(dbFor({...readyRecord, username:"", password_ciphertext:""}), {}), true);
assert.equal(await isInquiryFormReady({prepare(){throw Error("D1 unavailable")}},env),false);

// Legacy D1 SMTP table receives one additive column, never replaces saved rows.
const statements=[];
const fakeDb={
  prepare(sql){
    statements.push(sql);
    return {
      run: async()=>({}),
      all:async()=>({results:sql.includes("PRAGMA table_info(form_smtp_settings)")
        ?[{name:"enabled"},{name:"host"}]
        :[{name:"region"},{name:"assigned_contact_id"},{name:"assigned_contact_name"},{name:"assigned_contact_email"}]})
    };
  }
};
await ensureFormSchema(fakeDb);
assert.equal(statements.filter(s=>s.includes("ALTER TABLE form_smtp_settings ADD COLUMN smtp_verified_at TEXT")).length,1);
// Exercise the genuine API handler's early validation and readiness gate.
const dataUrl = (text) => "data:text/javascript;base64," + Buffer.from(text).toString("base64");
const settingsSource = readFileSync(new URL("../functions/_shared/site-settings.js", import.meta.url), "utf8");
const submitSource = readFileSync(new URL("../functions/api/form-submit.js", import.meta.url), "utf8")
  .replace("../_shared/forms.js", dataUrl(nodeSource))
  .replace("../_shared/site-settings.js", dataUrl(settingsSource));
const { onRequestPost } = await import(dataUrl(submitSource));
const submit = (payload) => onRequestPost({
  env: { XUYI_DB: dbFor({...readyRecord,enabled:0}) },
  request: new Request("https://xuyibottles.com/api/form-submit", {
    method: "POST", headers: {"content-type":"application/json"},
    body: JSON.stringify(payload)
  })
});
let response = await submit({email:"buyer@example.com",requirements:"Bottles"});
assert.equal(response.status, 400, "privacy consent is mandatory");
response = await submit({consent:true,requirements:"Bottles"});
assert.equal(response.status, 400, "a working reply address is mandatory");
response = await submit({consent:true,email:"buyer@example.com",requirements:"Bottles"});
assert.equal(response.status, 503, "never accept unnoticed enquiries when SMTP is unverified");
console.log("XUYI_INQUIRY_READINESS_TESTS_PASSED", 13, "assertions");