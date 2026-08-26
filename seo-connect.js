/**
 * seo-connect.js — wires Saturnalia AI SEO Suite to the real Ollama backend.
 * Place next to saturnalia.html and add just before </body>:
 *   <script src="seo-connect.js"></script>
 */

const SEO_API = "http://localhost:8000";

// ─── Theme tokens (match saturnalia CSS) ─────────────────────────────────────
const T = {
  accent:   "#6BBAB5",
  text:     "#F7F7F5",
  muted:    "#8896AB",
  subtle:   "#B8C4D0",
  border:   "rgba(255,255,255,0.09)",
  card:     "rgba(255,255,255,0.05)",
  high:     "#FF4B2B",
  highBg:   "rgba(255,75,43,0.12)",
  medium:   "#F59E0B",
  medBg:    "rgba(245,158,11,0.12)",
  low:      "#6BBAB5",
  lowBg:    "rgba(107,186,181,0.12)",
  font:     "'Inter', sans-serif",
  heading:  "'Outfit', sans-serif",
};

// ─── Utilities ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function apiPost(path, body) {
  const res = await fetch(SEO_API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Server error ${res.status}`);
  }
  return res.json();
}

function setStep(n) {
  [1, 2, 3].forEach(i => {
    const el = $(`audit-step-${i}`);
    if (el) el.style.display = i === n ? "block" : "none";
  });
  document.querySelectorAll("#audit-steps .step-circle").forEach(c => {
    const s = parseInt(c.dataset.step);
    c.classList.toggle("active", s === n);
    c.classList.toggle("done",   s < n);
  });
}

function addLog(msg) {
  const box = $("audit-log");
  if (!box) return;
  const p = document.createElement("p");
  p.style.margin = "4px 0";
  p.textContent = `> ${msg}`;
  box.appendChild(p);
  box.scrollTop = box.scrollHeight;
}

function animateScore(target) {
  const sv = $("score-value");
  const sr = $("score-ring");
  if (!sv || !sr) return;
  let c = 0;
  const iv = setInterval(() => {
    sv.textContent = c;
    sr.style.strokeDashoffset = 283 - (283 * c / 100);
    if (++c > target) clearInterval(iv);
  }, 18);
}

// ─── Themed timer bar (uses site's .seo-generating + .seo-loader classes) ────
function createTimerBar() {
  const bar = document.createElement("div");
  bar.id = "seo-audit-timer";
  bar.className = "seo-generating";          // native site class — teal pill row
  bar.style.marginTop = "14px";
  bar.innerHTML = `
    <div class="seo-loader"></div>
    <span style="font-family:${T.font};font-size:13px;color:${T.accent};">
      AI is analysing — <span id="seo-timer-secs" style="font-weight:700;">0</span>s elapsed
    </span>`;
  return bar;
}

function removeTimerBar() {
  const bar = $("seo-audit-timer");
  if (bar) bar.remove();
}

// ─── Findings renderer — exact card style, fully visible text ─────────────────
function renderFindings(data) {
  const list = $("findings-list");
  if (!list) return;

  const COLORS = {
    high:   { border: T.high,   bg: T.highBg,  label: "High Priority"   },
    medium: { border: T.medium, bg: T.medBg,   label: "Medium Priority" },
    low:    { border: T.low,    bg: T.lowBg,   label: "Low Priority"    },
  };

  // ── Priority action cards ────────────────────────────────────────────────
  const actionCards = (data.priority_actions || []).map(a => {
    const c = COLORS[a.priority] || COLORS.low;
    return `
      <div class="finding-card" style="border-left:4px solid ${c.border};margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <h4 style="font-family:${T.heading};color:${c.border};font-size:14px;font-weight:700;margin:0;">
            ${a.action}
          </h4>
          <span style="font-size:11px;font-weight:600;background:${c.bg};color:${c.border};
                       padding:3px 10px;border-radius:20px;white-space:nowrap;margin-left:10px;">
            ${c.label}
          </span>
        </div>
        ${a.expected_impact ? `
        <p style="font-family:${T.font};font-size:13px;color:${T.subtle};margin:0;line-height:1.5;">
          ${a.expected_impact}
        </p>` : ""}
      </div>`;
  }).join("");

  // ── Section score summary cards ──────────────────────────────────────────
  const sections = [
    ["keyword_analysis",   "Keyword Analysis"],
    ["backlinks",          "Backlinks"],
    ["technical_seo",      "Technical SEO"],
    ["competitor_analysis","Competitor Analysis"],
  ];

  const sectionCards = sections.map(([key, label]) => {
    const sec = data[key];
    if (!sec || sec.score == null) return "";
    const score = sec.score;
    const c     = COLORS[score >= 75 ? "low" : score >= 50 ? "medium" : "high"];
    const recs  = (sec.recommendations || []);

    return `
      <div class="finding-card" style="border-left:4px solid ${c.border};margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h4 style="font-family:${T.heading};color:${T.text};font-size:14px;font-weight:700;margin:0;">
            ${label}
          </h4>
          <span style="font-size:18px;font-weight:800;color:${c.border};">${score}<span style="font-size:12px;opacity:0.6;">/100</span></span>
        </div>
        ${recs.map(r => `
          <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;">
            <span style="color:${c.border};font-size:12px;margin-top:2px;flex-shrink:0;">●</span>
            <p style="font-family:${T.font};font-size:13px;color:${T.subtle};margin:0;line-height:1.5;">${r}</p>
          </div>`).join("")}
      </div>`;
  }).join("");

  list.innerHTML = actionCards + `
    <div style="font-family:${T.heading};font-size:12px;font-weight:600;
                color:${T.muted};letter-spacing:1px;text-transform:uppercase;
                margin:20px 0 12px;">Section Breakdown</div>
    ${sectionCards}`;
}

// ─── Site Audit ────────────────────────────────────────────────────────────────
function wireAudit() {
  const orig = $("start-audit-btn");
  if (!orig) return;
  const btn = orig.cloneNode(true);
  orig.parentNode.replaceChild(btn, orig);

  btn.addEventListener("click", async () => {
    const url = ($("audit-url") || {}).value?.trim();
    if (!url) { alert("Please enter a URL first."); return; }

    btn.disabled = true;
    setStep(2);

    // Clear terminal
    const logBox = $("audit-log");
    if (logBox) logBox.innerHTML = "";

    // Inject themed timer bar below the terminal
    const timerBar = createTimerBar();
    if (logBox && logBox.parentNode) {
      logBox.parentNode.insertBefore(timerBar, logBox.nextSibling);
    }

    // Live elapsed counter
    const startTime = Date.now();
    const secsEl    = $("seo-timer-secs");
    const clockIv   = setInterval(() => {
      if (secsEl) secsEl.textContent = Math.floor((Date.now() - startTime) / 1000);
    }, 1000);

    // Stream log lines into the terminal
    const logs = [
      `Fetching page: ${url}`,
      "Parsing HTML — title, meta, headings, body text...",
      "Measuring keyword density and placement...",
      "Searching for backlink signals...",
      "Researching competitors via DuckDuckGo...",
      "Scoring technical SEO signals...",
      "Sending data to local AI model (Ollama)...",
      "AI is generating your personalised report...",
    ];
    let li = 0;
    const logIv = setInterval(() => {
      if (li < logs.length) addLog(logs[li++]);
    }, 4500);

    try {
      const data = await apiPost("/audit", { url });

      clearInterval(logIv);
      clearInterval(clockIv);

      const total = ((Date.now() - startTime) / 1000).toFixed(1);

      // Update timer bar to "done" state
      if (timerBar) {
        timerBar.innerHTML = `
          <span style="font-size:16px;">✓</span>
          <span style="font-family:${T.font};font-size:13px;color:${T.accent};font-weight:600;">
            Audit complete — analysed in <strong>${total}s</strong>
          </span>`;
        timerBar.style.background = "rgba(107,186,181,0.08)";
      }

      addLog(`✓ Done in ${total}s — loading results...`);
      await sleep(600);

      removeTimerBar();
      setStep(3);
      animateScore(data.overall_score || 0);
      renderFindings(data);

    } catch (err) {
      clearInterval(logIv);
      clearInterval(clockIv);

      if (timerBar) {
        timerBar.innerHTML = `
          <span style="font-size:16px;">✗</span>
          <span style="font-family:${T.font};font-size:13px;color:${T.high};">
            ${err.message}
          </span>`;
        timerBar.style.background = "rgba(255,75,43,0.08)";
        timerBar.style.borderColor = "rgba(255,75,43,0.2)";
      }

      addLog("✗ Error: " + err.message);
      addLog("Is 2_start_server.bat running? Check the black window.");
    } finally {
      btn.disabled = false;
    }
  });
}

// ─── Blog Topics ───────────────────────────────────────────────────────────────
function wireBlogTopics() {
  const orig = $("suggest-topics-btn");
  if (!orig) return;
  const btn = orig.cloneNode(true);
  orig.parentNode.replaceChild(btn, orig);

  btn.addEventListener("click", async () => {
    const industry = ($("blog-industry") || {}).value?.trim() || "";
    const audience = ($("blog-audience") || {}).value?.trim() || "";
    const tone     = ($("blog-tone")     || {}).value?.trim() || "professional";
    const goal     = ($("blog-goal")     || {}).value?.trim() || "educate";
    if (!industry) { alert("Please enter your industry."); return; }

    const orig2 = btn.textContent;
    btn.disabled = true; btn.textContent = "Researching…";

    try {
      const data   = await apiPost("/blog/topics", { industry, audience, tone, goal });
      const topics = data.topics || data;
      window._blogTopics = topics;

      const list = $("topics-list");
      if (list) {
        list.innerHTML = topics.map((t, i) => `
          <div class="topic-card" style="margin-bottom:12px;padding:16px;
               background:${T.card};border:1px solid ${T.border};border-radius:12px;">
            <h4 style="font-family:${T.heading};font-size:15px;font-weight:700;
                       color:${T.text};margin:0 0 6px;">${t.title}</h4>
            <p style="font-family:${T.font};font-size:13px;color:${T.subtle};
                      margin:0 0 10px;line-height:1.5;">${t.hook}</p>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
              <span style="font-size:11px;font-weight:600;background:${T.lowBg};
                           color:${T.accent};padding:3px 10px;border-radius:20px;">
                ${t.primary_keyword}
              </span>
              <span style="font-size:11px;background:rgba(255,255,255,0.07);
                           color:${T.subtle};padding:3px 10px;border-radius:20px;">
                ${t.estimated_monthly_searches}
              </span>
              <span style="font-size:11px;background:rgba(255,255,255,0.07);
                           color:${T.subtle};padding:3px 10px;border-radius:20px;">
                ${t.difficulty}
              </span>
            </div>
            <p style="font-family:${T.font};font-size:12px;color:${T.muted};
                      margin:0 0 12px;font-style:italic;">${t.content_angle}</p>
            <button class="btn btn-primary btn-sm" onclick="window.selectBlogTopic(${i})"
                    style="font-family:${T.font};">Use this topic</button>
          </div>`).join("");
      }
    } catch (err) {
      alert("Topic generation failed: " + err.message);
    } finally {
      btn.disabled = false; btn.textContent = orig2;
    }
  });
}

window.selectBlogTopic = function(i) {
  const t = (window._blogTopics || [])[i];
  if (!t) return;
  window._selectedTopic = t.title;
  const inp = $("selected-topic-title") || $("blog-topic");
  if (inp) inp.value = t.title;
};

// ─── Blog Generate ─────────────────────────────────────────────────────────────
function wireBlogGenerate() {
  const orig = $("generate-blog-btn");
  if (!orig) return;
  const btn = orig.cloneNode(true);
  orig.parentNode.replaceChild(btn, orig);

  btn.addEventListener("click", async () => {
    const topic    = window._selectedTopic || ($("blog-topic") || {}).value?.trim() || "";
    const industry = ($("blog-industry") || {}).value?.trim() || "";
    const audience = ($("blog-audience") || {}).value?.trim() || "";
    const tone     = ($("blog-tone")     || {}).value?.trim() || "professional";
    if (!topic) { alert("Please select a topic first."); return; }

    const orig2 = btn.textContent;
    btn.disabled = true; btn.textContent = "Writing…";

    try {
      const post  = await apiPost("/blog/generate", { topic, industry, audience, tone });
      const panel = $("blog-output");
      if (panel) {
        panel.style.display = "";
        panel.innerHTML = `
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
            ${[
              [post.word_count + " words", T.accent],
              [post.reading_time,           T.subtle],
              ["SEO " + post.seo_score + "/100", post.seo_score >= 70 ? T.low : T.medium],
              [post.readability_grade,      T.subtle],
            ].map(([val, col]) => `
              <span style="font-family:${T.font};font-size:12px;font-weight:600;
                           color:${col};background:rgba(255,255,255,0.05);
                           padding:4px 12px;border-radius:20px;
                           border:1px solid ${T.border};">${val}</span>`).join("")}
          </div>
          <div style="margin-bottom:14px;padding:14px;background:${T.card};
                      border-radius:10px;border:1px solid ${T.border};">
            <p style="font-family:${T.font};font-size:12px;color:${T.muted};margin:0 0 4px;">
              META TITLE</p>
            <p style="font-family:${T.heading};font-size:15px;color:${T.text};margin:0 0 10px;">
              ${post.meta_title}</p>
            <p style="font-family:${T.font};font-size:12px;color:${T.muted};margin:0 0 4px;">
              META DESCRIPTION</p>
            <p style="font-family:${T.font};font-size:13px;color:${T.subtle};margin:0;">
              ${post.meta_description}</p>
          </div>
          <div style="font-family:${T.font};font-size:14px;color:${T.text};
                      line-height:1.75;padding:4px 0;">
            ${post.html_body}
          </div>`;
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (err) {
      alert("Blog generation failed: " + err.message);
    } finally {
      btn.disabled = false; btn.textContent = orig2;
    }
  });
}

// ─── Backlinks ─────────────────────────────────────────────────────────────────
function wireBacklinks() {
  const orig = $("find-backlinks-btn");
  if (!orig) return;
  const btn = orig.cloneNode(true);
  orig.parentNode.replaceChild(btn, orig);

  btn.addEventListener("click", async () => {
    const domain  = ($("backlink-domain")   || {}).value?.trim() || "";
    const kwRaw   = ($("backlink-keywords") || {}).value?.trim() || "";
    const keywords = kwRaw ? kwRaw.split(/[\n,]+/).map(k => k.trim()).filter(Boolean) : [];
    if (!domain) { alert("Please enter your domain."); return; }

    const orig2 = btn.textContent;
    btn.disabled = true; btn.textContent = "Searching…";

    try {
      const data = await apiPost("/backlinks", { domain, keywords });
      const opps = data.opportunities || data;
      const list = $("backlink-list");
      if (list) {
        list.innerHTML = opps.map(o => {
          const daColor = o.domain_authority >= 60 ? T.low :
                          o.domain_authority >= 30 ? T.medium : T.muted;
          return `
            <div class="backlink-card" style="margin-bottom:12px;padding:16px;
                 background:${T.card};border:1px solid ${T.border};border-radius:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-family:${T.heading};font-weight:700;font-size:15px;
                             color:${T.text};">${o.source_domain}</span>
                <div style="display:flex;gap:6px;align-items:center;">
                  <span style="font-size:12px;font-weight:700;color:${daColor};">
                    DA ${o.domain_authority}</span>
                  <span style="font-size:11px;background:rgba(255,255,255,0.07);
                               color:${T.subtle};padding:2px 8px;border-radius:20px;">
                    ${o.link_type}</span>
                </div>
              </div>
              <p style="font-family:${T.font};font-size:13px;color:${T.subtle};
                        margin:0 0 6px;line-height:1.5;">${o.pitch_angle}</p>
              <p style="font-family:${T.font};font-size:12px;color:${T.muted};margin:0 0 10px;">
                <strong style="color:${T.subtle};">Contact:</strong> ${o.contact_hint}</p>
              <a href="${o.page_url}" target="_blank" rel="noopener"
                 style="font-family:${T.font};font-size:13px;font-weight:600;
                        color:${T.accent};text-decoration:none;">View page ↗</a>
            </div>`;
        }).join("");
      }
    } catch (err) {
      alert("Backlink search failed: " + err.message);
    } finally {
      btn.disabled = false; btn.textContent = orig2;
    }
  });
}

// ─── Boot ──────────────────────────────────────────────────────────────────────
function init() {
  wireAudit();
  wireBlogTopics();
  wireBlogGenerate();
  wireBacklinks();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
