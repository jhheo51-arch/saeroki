"use strict";

const TOKEN = document.querySelector('meta[name="saerok-token"]').content;
const REFRESH_MS = 60_000;
const BUCKET_LABELS = ["10만 미만", "10~30만", "30~60만", "60만 이상"];
let data = null;

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function man(n) {
  n = Number(n) || 0;
  if (n >= 1e8) return (n / 1e8).toFixed(1) + "억";
  if (n >= 1e4) return (n / 1e4).toFixed(1) + "만";
  return n.toLocaleString("ko-KR");
}
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0) + "%";
const when = (ts) => (ts ? new Date(ts).toLocaleString("ko-KR", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "");

function levelOf(ctx) {
  if (ctx >= data.config.warn) return 2;
  if (ctx >= data.config.caution) return 1;
  return 0;
}

function toast(text) {
  const t = $("toast");
  t.textContent = text;
  t.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove("show"), 5000);
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Saerok-Token": TOKEN },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || "요청 실패");
  return json;
}

async function load() {
  $("updated").textContent = "불러오는 중…";
  try {
    const res = await fetch("/api/summary", { cache: "no-store" });
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || "집계 실패");
    data = json;
    render();
    $("updated").textContent = `${data.generated_at} 기준 · 1분마다 갱신`;
  } catch (e) {
    $("updated").textContent = "불러오기 실패: " + e.message;
  }
}

function render() {
  renderNow();
  renderTrend();
  renderAdvice();
  renderApply();
}

function renderNow() {
  const t = data.totals;
  const over = t.buckets[2] + t.buckets[3];
  const hook = data.environment.hook_installed;
  $("cards").innerHTML = [
    ["전체 처리량", man(t.processed) + " 토큰", `세션 ${t.sessions}개 · 응답 ${t.responses.toLocaleString("ko-KR")}번`],
    ["30만 이상 응답의 몫", pct(over, t.processed), "높을수록 긴 세션이 사용량을 끌어올림"],
    ["세션 기본 부담", man(t.baseline_median) + " 토큰", "세션 첫 응답 크기의 중앙값"],
    ["실시간 경고", hook ? "켜짐" : "꺼짐", hook ? `주의 ${man(data.config.caution)} · 경고 ${man(data.config.warn)}` : "적용 탭에서 훅을 설치하세요"],
  ].map(([l, v, h]) => `<div class="card"><div class="label">${l}</div><div class="value">${v}</div><div class="hint">${h}</div></div>`).join("");

  const max = 1_000_000;
  $("live").innerHTML = data.live.length ? data.live.map((s) => {
    const lv = levelOf(s.last_ctx);
    const word = ["여유", "주의", "경고"][lv];
    return `<div class="live">
      <div class="row"><span class="title">${esc(s.title || "(제목 없음)")}</span><span class="badge l${lv}">${word}</span></div>
      <div class="gauge" title="1M 창 기준">
        <div class="fill l${lv}" style="width:${Math.min(100, (s.last_ctx / max) * 100)}%"></div>
        <div class="mark" style="left:${(data.config.caution / max) * 100}%"></div>
        <div class="mark" style="left:${(data.config.warn / max) * 100}%"></div>
      </div>
      <div class="small">지금 ${man(s.last_ctx)} 토큰 · 최대 ${man(s.max_ctx)} · 응답 ${s.responses}번 · 스크린샷 ${s.images}장 · 압축 ${s.compactions}번 · ${esc(s.project || "")} · ${when(s.last_ts)}</div>
    </div>`;
  }).join("") : `<div class="empty">최근 30분 안에 움직인 세션이 없습니다.</div>`;

  $("alerts").innerHTML = data.alerts.length
    ? `<div class="table-wrap"><table><tr><th>시각</th><th>단계</th><th class="num">컨텍스트</th><th>세션</th></tr>${data.alerts.map((a) => {
        const s = data.sessions.find((x) => x.session_id === a.session_id);
        return `<tr><td>${esc(a.at)}</td><td><span class="badge l${a.level}">${a.level === 2 ? "경고" : "주의"}</span></td><td class="num">${man(a.ctx)}</td><td>${esc(s ? s.title : a.session_id.slice(0, 8))}</td></tr>`;
      }).join("")}</table></div>`
    : `<div class="empty">${data.environment.hook_installed ? "아직 기준을 넘은 세션이 없습니다." : "훅을 설치하면 기준을 넘을 때마다 여기에 남습니다."}</div>`;
}

function renderTrend() {
  const days = data.daily.slice(-30);
  if (!days.length) {
    $("daily").innerHTML = `<div class="empty">기록이 없습니다.</div>`;
  } else {
    const W = 760, H = 220, pad = 34, bw = (W - pad * 2) / days.length;
    const top = Math.max(...days.map((d) => d.processed));
    const y = (v) => H - pad - (v / top) * (H - pad * 2);
    const bars = days.map((d, i) => {
      const x = pad + i * bw + 2, w = Math.max(2, bw - 4);
      const label = i % Math.ceil(days.length / 10) === 0 ? `<text x="${x + w / 2}" y="${H - 12}" text-anchor="middle">${d.date.slice(5)}</text>` : "";
      return `<g><title>${d.date} · 처리 ${man(d.processed)} · 30만 이상 ${pct(d.over300, d.processed)} · 응답 ${d.responses} · 스크린샷 ${d.images}</title>
        <rect x="${x}" y="${y(d.processed)}" width="${w}" height="${H - pad - y(d.processed)}" fill="var(--total)"/>
        <rect x="${x}" y="${y(d.over300)}" width="${w}" height="${H - pad - y(d.over300)}" fill="var(--hot)"/>${label}</g>`;
    }).join("");
    $("daily").innerHTML = `<div class="legend"><span><i style="background:var(--total)"></i>30만 미만 응답</span><span><i style="background:var(--hot)"></i>30만 이상 응답</span></div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="날짜별 처리량">
      <text x="${pad}" y="16">최대 ${man(top)}</text>
      <line x1="${pad}" x2="${W - pad}" y1="${H - pad}" y2="${H - pad}" stroke="var(--line)"/>${bars}</svg>`;
  }

  const total = data.totals.processed || 1;
  $("buckets").innerHTML = data.totals.buckets.map((b, i) =>
    `<div class="bucket"><span>${BUCKET_LABELS[i]}</span><div class="track"><div class="bar" style="width:${(b / total) * 100}%"></div></div><span class="small">${pct(b, total)}</span></div>`).join("");

  const rows = [...data.sessions].sort((a, b) => b.processed - a.processed).slice(0, 30);
  $("sessions").innerHTML = `<div class="table-wrap"><table>
    <tr><th>세션</th><th>폴더</th><th class="num">응답</th><th class="num">처리량</th><th class="num">최대</th><th class="num">스크린샷</th><th>마지막</th></tr>
    ${rows.map((s) => `<tr><td>${esc(s.title || s.session_id.slice(0, 8))}</td><td>${esc(s.project || "")}</td><td class="num">${s.responses}</td><td class="num">${man(s.processed)}</td><td class="num"><span class="badge l${levelOf(s.max_ctx)}">${man(s.max_ctx)}</span></td><td class="num">${s.images}</td><td>${when(s.last_ts)}</td></tr>`).join("")}
  </table></div>`;
}

function renderAdvice() {
  $("advice-count").textContent = data.suggestions.length || "";
  $("advice").innerHTML = data.suggestions.length ? data.suggestions.map((s) => `<article class="advice">
    <h3><span class="badge size-${s.size}">효과 ${s.size}</span>${esc(s.title)}</h3>
    <dl>
      <dt>측정</dt><dd>${esc(s.measured)}</dd>
      <dt>추정</dt><dd>${esc(s.estimate)}</dd>
      <dt>방법</dt><dd>${esc(s.how)}</dd>
      <dt>잃는 것</dt><dd>${esc(s.loss)}</dd>
      ${s.status ? `<dt>상태</dt><dd>${esc(s.status)}</dd>` : ""}
      <dt>할 일</dt><dd>${s.action ? `적용 탭에서 <b>${esc(s.action_label)}</b>` : esc(s.manual || "직접 확인")}</dd>
    </dl></article>`).join("") : `<div class="empty">지금은 제안할 것이 없습니다. 잘 아끼고 있어요.</div>`;
}

function renderApply() {
  const actions = data.suggestions.filter((s) => s.action);
  $("actions").innerHTML = actions.length ? actions.map((s) => `<div class="action">
    <div><b>${esc(s.action_label)}</b><div class="small">${esc(s.title)} · ${esc(s.measured)}</div></div>
    <button data-apply="${esc(s.action)}" data-label="${esc(s.action_label)}" data-loss="${esc(s.loss)}">적용</button></div>`).join("")
    : `<div class="empty">지금 바로 적용할 조치가 없습니다.</div>`;

  const form = $("config");
  if (document.activeElement?.form !== form) {
    form.caution.value = data.config.caution;
    form.warn.value = data.config.warn;
    form.toast.checked = data.config.toast !== false;
  }

  $("log").innerHTML = data.apply_log.length ? `<div class="table-wrap"><table>
    <tr><th>시각</th><th>조치</th><th>바뀐 키</th><th></th></tr>
    ${data.apply_log.map((e) => `<tr><td>${esc(e.at)}</td><td>${esc(e.label)}</td><td class="small">${e.changes.map((c) => esc(c.path.slice(-2).join(" › "))).join("<br>")}</td>
      <td>${e.undone_at ? `<span class="small">${esc(e.undone_at)} 되돌림</span>` : `<button class="ghost" data-undo="${esc(e.id)}" data-label="${esc(e.label)}">되돌리기</button>`}</td></tr>`).join("")}
  </table></div>` : `<div class="empty">아직 적용한 조치가 없습니다.</div>`;
}

document.addEventListener("click", async (ev) => {
  const tab = ev.target.closest("[data-tab]");
  if (tab) {
    document.querySelectorAll("[data-tab]").forEach((b) => b.setAttribute("aria-selected", String(b === tab)));
    document.querySelectorAll(".tab").forEach((s) => (s.hidden = s.id !== "tab-" + tab.dataset.tab));
    return;
  }
  const btn = ev.target.closest("[data-apply],[data-undo]");
  if (!btn) return;
  const applying = !!btn.dataset.apply;
  const question = applying
    ? `${btn.dataset.label}\n\n잃는 것: ${btn.dataset.loss}\n\n파일을 백업한 뒤 적용합니다. 계속할까요?`
    : `${btn.dataset.label}을(를) 되돌릴까요?`;
  if (!confirm(question)) return;
  btn.disabled = true;
  try {
    const res = applying ? await post("/api/apply", { action: btn.dataset.apply }) : await post("/api/undo", { id: btn.dataset.undo });
    toast(res.message);
    await load();
  } catch (e) {
    toast("실패: " + e.message);
    btn.disabled = false;
  }
});

$("config").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const f = ev.target;
  try {
    await post("/api/config", { caution: Number(f.caution.value), warn: Number(f.warn.value), toast: f.toast.checked });
    toast("경고 기준을 저장했습니다. 다음 응답부터 적용됩니다.");
    await load();
  } catch (e) {
    toast("실패: " + e.message);
  }
});

$("test-toast").addEventListener("click", async () => {
  try {
    toast((await post("/api/test-toast", {})).message);
  } catch (e) {
    toast("알림 실패: " + e.message);
  }
});

$("refresh").addEventListener("click", load);
load();
setInterval(() => { if (!document.hidden) load(); }, REFRESH_MS);
