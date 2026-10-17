/* 새록 면접관 결정적 계층의 브라우저판. saerok_interview/(rubric·session·store·compare·terms)와 같은 규칙·같은 결과를 냅니다.
   test_saerok_interview.py가 node로 이 파일을 돌려 Python 결과와 같은지 검사합니다. AI는 쓰지 않습니다.
   세션 하나는 {meta, score, inputs: {종류: 본문}} 꼴이고, Python의 세션 폴더(session.json·score.json·inputs/)와 같은 내용입니다. */
(function (root) {
  "use strict";

  // ---------- rubric.py ----------
  const INTERVIEWERS = {
    pressure: {
      name: "압박",
      looks_at: "과장·모순·빈틈",
      items: [
        { key: "evidence", name: "주장과 근거 일치", max: 3 },
        { key: "role", name: "역할 범위가 분명함", max: 3 },
        { key: "consistency", name: "앞뒤 일관성", max: 2 },
        { key: "composure", name: "흔들림 없는 답", max: 2, answer_only: true },
      ],
    },
    hr: {
      name: "인사",
      looks_at: "지원 동기·협업·태도",
      items: [
        { key: "motivation", name: "지원 동기의 구체성", max: 3 },
        { key: "collaboration", name: "협업·갈등 해결 사례", max: 3 },
        { key: "fit", name: "조직 적합성", max: 2 },
        { key: "tenure", name: "오래 다닐 근거", max: 2 },
      ],
    },
    practitioner: {
      name: "실무",
      looks_at: "바로 투입 가능한지",
      items: [
        { key: "judgment", name: "상황 판단", max: 3 },
        { key: "execution", name: "실행 순서", max: 3 },
        { key: "terms", name: "직무 용어를 바르게 씀", max: 2 },
        { key: "posting", name: "공고 요건과 연결", max: 2, needs_posting: true },
      ],
    },
    executive: {
      name: "임원",
      looks_at: "회사 방향과 장기 포부",
      items: [
        { key: "company", name: "회사·산업 이해", max: 3, needs_posting: true },
        { key: "why_us", name: "'왜 우리 회사'", max: 3 },
        { key: "vision", name: "3~5년 포부의 현실성", max: 2 },
        { key: "summary", name: "한 문장 요약력", max: 2, answer_only: true },
      ],
    },
    numbers: {
      name: "숫자 검증",
      looks_at: "성과 수치의 출처와 계산",
      items: [
        { key: "source", name: "수치의 출처", max: 3 },
        { key: "calculation", name: "계산 과정", max: 3 },
        { key: "definition", name: "지표 정의", max: 2 },
        { key: "baseline", name: "비교 기준(이전·대조군)", max: 2 },
      ],
    },
  };
  const ORDER = Object.keys(INTERVIEWERS);
  const LEVELS = ["순한맛", "보통", "매운맛"];
  const NOTICE = "연습용 판정입니다. 실제 면접 방식·합격 여부와 다를 수 있습니다.";
  const DOCS = ["resume_letter", "posting", "resume", "portfolio"];
  const DOC_NAMES = { resume_letter: "자기소개서", posting: "채용 공고", resume: "이력서", portfolio: "포트폴리오" };
  const QUESTIONS_PER_INTERVIEWER = 2;
  const GOAL_RISE = 2.0;
  const LOW_RATIO = 0.5;
  const RETEST_LIMIT = 2.0;
  const INTERVIEW_LEVELS = ["실무", "심화", "입문"];

  // ---------- Python과 같은 결과를 내기 위한 작은 도구 ----------
  // Python round(x, n)과 같게: 정확히 반 올림 자리일 때만 짝수로, 나머지는 x의 정확한 값으로 반올림합니다(n은 0 또는 1).
  function pyRound(x, n) {
    const scale = 2 ** (n + 1);
    const tie = Number.isInteger(x * scale) && !Number.isInteger(x * scale / 2);
    if (tie) {
      const y = x * 10 ** n;
      const f = Math.floor(y);
      return (f % 2 === 0 ? f : f + 1) / 10 ** n;
    }
    return parseFloat(x.toFixed(n));
  }
  // Python f"{v:g}" (이 열매의 값은 소수 한 자리 이하라 이걸로 충분합니다)
  const fmtG = (v) => (Object.is(v, -0) ? "-0" : String(v));
  const fmtSigned = (v) => (v < 0 || Object.is(v, -0) ? "-" : "+") + String(Math.abs(v));
  const fmt = (v) => (v === null || v === undefined ? "-" : fmtG(v));
  // Python str()·repr() 꼴
  const pyStr = (v) => (v === null || v === undefined ? "None" : v === true ? "True" : v === false ? "False" : String(v));
  const pyRepr = (v) => (typeof v === "string" ? `'${v}'` : pyStr(v));
  const isInt = (v) => typeof v === "number" && Number.isInteger(v);
  const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
  const strip = (s) => String(s ?? "").trim();
  const truthy = (v) => !(v === null || v === undefined || v === false || v === 0 || v === "" ||
    (Array.isArray(v) && !v.length) || (isObj(v) && !Object.keys(v).length));

  // Python str.splitlines()
  function splitlines(text) {
    const parts = String(text).split(/\r\n|[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]/);
    if (parts.length && parts[parts.length - 1] === "") parts.pop();
    return parts;
  }
  const squash = (s) => String(s).replace(/[\s\x1c-\x1f\x85]/g, "");

  // ---------- rubric.py ----------
  function item(who, key) {
    return INTERVIEWERS[who].items.find((i) => i.key === key) || null;
  }

  function autoNa(who, key, stage, posting) {
    const spec = item(who, key);
    if (stage === "document" && spec.answer_only) return "답변에서만 봄";
    if (spec.needs_posting && !posting) return "공고 없음";
    return null;
  }

  function total10(who, items) {
    let got = 0, top = 0;
    for (const spec of INTERVIEWERS[who].items) {
      const value = items[spec.key];
      if (value === null || value === undefined) continue;
      got += value;
      top += spec.max;
    }
    return top ? pyRound(got / top * 10, 1) : null;
  }

  function verdict(score) {
    if (score === null || score === undefined) return "판단 보류";
    if (score >= 7) return "합격권";
    if (score >= 5) return "보류";
    return "부족";
  }

  // ---------- session.py ----------
  const PATTERNS = [
    ["주민등록번호", /(?<!\d)\d{6}\s?-\s?[1-4]\d{6}(?!\d)/g],
    ["전화번호", /(?<!\d)01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)/g],
    ["이메일", /[\p{L}\p{N}\p{M}_.+-]+@[\p{L}\p{N}\p{M}_-]+(?:\.[\p{L}\p{N}\p{M}_-]+)+/gu],
  ];

  const mask = (text) => { const c = Array.from(text); return c.slice(0, 3).join("") + "*".repeat(Math.max(c.length - 3, 0)); };

  function scan(text) {
    const found = [];
    splitlines(text).forEach((line, i) => {
      for (const [kind, pattern] of PATTERNS) {
        for (const m of line.matchAll(pattern)) found.push({ line: i + 1, kind, masked: mask(m[0]) });
      }
    });
    return found;
  }

  function slug(name) {
    const s = String(name || "").trim().replace(/[\\/:*?"<>|\s]+/g, "-").replace(/^[-.]+|[-.]+$/g, "");
    return Array.from(s).slice(0, 30).join("") || "이름-없음";
  }

  async function sha256(text) {
    const bytes = new TextEncoder().encode(text);
    if (root.crypto && root.crypto.subtle) {
      const hash = await root.crypto.subtle.digest("SHA-256", bytes);
      return Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, "0")).join("");
    }
    return require("crypto").createHash("sha256").update(bytes).digest("hex");
  }

  // session.create_texts와 같은 세션을 만듭니다. names는 이미 있는 세션 이름(겹치면 -2, -3…).
  async function createSession(texts, opts, names) {
    opts = opts || {};
    const company = opts.company || "", industry = opts.industry || "", role = opts.role || "";
    for (const key of Object.keys(texts)) if (!DOCS.includes(key)) throw new Error(`모르는 입력입니다: ${key}`);
    if (!strip(texts.resume_letter)) throw new Error("자기소개서는 꼭 필요합니다.");
    const date = opts.date;
    const stem = `${date}-${slug(company)}`;
    const taken = new Set(names || []);
    let name = stem, n = 2;
    while (taken.has(name)) name = `${stem}-${n++}`;
    const inputs = {}, kept = {};
    for (const key of DOCS) {
      if (!strip(texts[key])) continue;
      kept[key] = texts[key];
      inputs[key] = { file: `inputs/${DOC_NAMES[key]}.md`, sha256: await sha256(texts[key]) };
    }
    const meta = { version: 1, session: name, date, company, industry, role, posting: "posting" in kept, inputs };
    const privacy = {};
    for (const [key, text] of Object.entries(kept)) {
      const hits = scan(text);
      if (hits.length) privacy[key] = hits;
    }
    return { meta, score: { version: 1, document: {}, answers: [], real: [] }, inputs: kept, privacy };
  }

  // ---------- store.py ----------
  function checkItems(who, items, na, stage, posting) {
    if (!isObj(items)) throw new Error(`${who}: items는 항목별 점수 객체여야 합니다.`);
    const keys = new Set(INTERVIEWERS[who].items.map((i) => i.key));
    const unknown = Object.keys(items).filter((k) => !keys.has(k)).sort();
    if (unknown.length) throw new Error(`${who}: 모르는 기준 항목입니다: ${unknown.join(", ")}`);
    const outItems = {}, outNa = {};
    na = isObj(na) ? na : {};
    for (const spec of INTERVIEWERS[who].items) {
      const key = spec.key;
      const auto = autoNa(who, key, stage, posting);
      const reason = auto || (key in na ? na[key] : null);
      const value = key in items ? items[key] : null;
      if (auto || (truthy(reason) && value === null)) {
        outItems[key] = null;
        outNa[key] = reason;
        continue;
      }
      if (value === null) throw new Error(`${who}.${key}: 점수가 없습니다. 볼 수 없으면 na에 이유를 적어 주세요.`);
      if (!isInt(value) || value < 0 || value > spec.max) {
        throw new Error(`${who}.${key}: 0~${spec.max} 사이 정수여야 합니다(받은 값 ${pyRepr(value)}).`);
      }
      outItems[key] = value;
    }
    return [outItems, outNa];
  }

  function verifyEvidence(session, evidence) {
    const checked = [];
    for (const ev of evidence || []) {
      const doc = ev.doc ?? null, line = ev.line ?? null, quote = strip(ev.quote);
      let status = "확인 안 됨";
      const text = session.meta.inputs[doc] ? session.inputs[doc] : null;
      if (text !== null && text !== undefined && isInt(line) && quote) {
        const lines = splitlines(text);
        const near = lines.slice(Math.max(line - 2, 0), line + 1);
        if (near.some((row) => squash(row).includes(squash(quote)))) status = "확인";
      }
      checked.push({ doc, line, quote, status });
    }
    return checked;
  }

  function recordDocument(session, result) {
    const { meta, score } = session;
    const who = result.interviewer;
    if (!(who in INTERVIEWERS)) throw new Error(`모르는 면접관입니다: ${pyRepr(who ?? null)}. 가능한 값: ${ORDER.join(", ")}`);
    const questions = result.questions || [];
    if (questions.length !== QUESTIONS_PER_INTERVIEWER) {
      throw new Error(`${who}: 질문은 ${QUESTIONS_PER_INTERVIEWER}개여야 합니다(받은 수 ${questions.length}).`);
    }
    const [items, na] = checkItems(who, result.items || {}, result.na || {}, "document", meta.posting);
    const clean = [];
    for (const q of questions) {
      if (!strip(q.question)) throw new Error(`${who}: 빈 질문이 있습니다.`);
      if (!(q.item in items)) throw new Error(`${who}: 질문의 item은 이 면접관의 기준 항목이어야 합니다(받은 값 ${pyRepr(q.item ?? null)}).`);
      const evidence = verifyEvidence(session, q.evidence);
      clean.push({
        question: strip(q.question),
        item: q.item,
        direction: strip(q.direction),
        evidence,
        grounded: evidence.some((e) => e.status === "확인"),
      });
    }
    score.document[who] = {
      items,
      na,
      total: total10(who, items),
      comment: strip(result.comment),
      fixes: (result.fixes || []).map(strip).filter(Boolean),
      questions: clean,
    };
    return score.document[who];
  }

  function questionList(score) {
    const out = [];
    let no = 0;
    for (const who of ORDER) {
      for (const q of ((score.document[who] || {}).questions || [])) {
        no += 1;
        out.push({ no, interviewer: who, ...q });
      }
    }
    return out;
  }

  function nextQuestion(session, who) {
    const score = session.score;
    const done = new Set(score.answers.filter((a) => a.no).map((a) => a.no));
    const totals = {};
    for (const w of ORDER) totals[w] = (score.document[w] || {}).total ?? null;
    for (const w of who || []) {
      if (!(w in INTERVIEWERS)) throw new Error(`모르는 면접관입니다: ${pyRepr(w)}. 가능한 값: ${ORDER.join(", ")}`);
    }
    const pick = who && who.length ? who : null;
    const rest = questionList(score).filter((q) => !done.has(q.no) && (!pick || pick.includes(q.interviewer)));
    const key = (q) => (totals[q.interviewer] !== null ? totals[q.interviewer] : 99);
    rest.sort((a, b) => key(a) - key(b) || a.no - b.no);
    return rest.length ? rest[0] : null;
  }

  function recordAnswer(session, answer, today) {
    const { meta, score } = session;
    const who = answer.interviewer;
    if (!(who in INTERVIEWERS)) throw new Error(`모르는 면접관입니다: ${pyRepr(who ?? null)}`);
    const level = "level" in answer ? answer.level : "보통";
    if (!LEVELS.includes(level)) throw new Error(`강도는 ${LEVELS.join(", ")} 중 하나여야 합니다.`);
    const followups = answer.followups || [];
    if (followups.length > 2) throw new Error("꼬리 질문은 질문당 2번까지입니다.");
    if (!strip(answer.question) || !strip(answer.answer)) throw new Error("질문과 답이 모두 있어야 합니다.");
    const [items, na] = checkItems(who, answer.items || {}, answer.na || {}, "answer", meta.posting);
    const row = {
      no: answer.no ?? null,
      date: answer.date || today,
      interviewer: who,
      level,
      question: strip(answer.question),
      answer: strip(answer.answer),
      followups: followups.map((f) => ({ question: strip(f.question), answer: strip(f.answer) })),
      items,
      na,
      total: total10(who, items),
      missing: (answer.missing || []).filter(truthy),
      better: strip(answer.better),
    };
    score.answers.push(row);
    return row;
  }

  function recordReal(session, real, today) {
    const { meta, score } = session;
    const numbers = new Set(questionList(score).map((q) => q.no));
    const rows = [];
    for (const q of real.questions || []) {
      const text = strip(q.question);
      if (!text) continue;
      const matched = q.matched ?? null;
      if (matched !== null && !numbers.has(matched)) throw new Error(`모의 질문 Q${matched}가 이 세션에 없습니다.`);
      rows.push({ question: text, matched, confirmed: truthy(q.confirmed) && matched !== null });
    }
    if (!rows.length) throw new Error("실제 면접 질문이 없습니다.");
    const entry = { date: real.date || today, company: "company" in real ? real.company : (meta.company || ""), questions: rows };
    score.real.push(entry);
    return entry;
  }

  function itemsText(who, items, na) {
    return INTERVIEWERS[who].items.map((spec) => {
      const value = items[spec.key];
      const shown = value === null || value === undefined ? `해당 없음(${na[spec.key] ?? ""})` : `${value}/${spec.max}`;
      return `${spec.name} ${shown}`;
    }).join(" · ");
  }

  const done = (lines) => lines.join("\n").replace(/\s+$/, "") + "\n";

  function renderReport(session) {
    const { meta, score } = session;
    const lines = [
      `# 새록 면접관 판정: ${meta.company || "회사 미지정"} (${meta.date})`,
      "",
      `> ${NOTICE}`,
      "",
      "입력: " + Object.keys(meta.inputs).map((k) => DOC_NAMES[k]).join(", ") + (meta.posting ? "" : " (공고 없음: 공고 관련 항목은 해당 없음)"),
    ];
    if (meta.industry || meta.role) lines.push(`산업·직무: ${meta.industry || "-"} / ${meta.role || "-"}`);
    lines.push("", "## 판정표", "", "| 면접관 | 서류 점수 | 판정 | 한 줄 평 |", "|---|---:|---|---|");
    const missing = [];
    for (const who of ORDER) {
      const doc = score.document[who];
      const name = INTERVIEWERS[who].name;
      if (!doc) {
        missing.push(name);
        lines.push(`| ${name} | - | 결과 없음 | |`);
        continue;
      }
      lines.push(`| ${name} | ${fmt(doc.total)}/10 | ${verdict(doc.total)} | ${doc.comment} |`);
    }
    if (missing.length) lines.push("", `아직 결과가 없는 면접관: ${missing.join(", ")}`);
    lines.push("", "## 기준 항목", "");
    for (const who of ORDER) {
      const doc = score.document[who];
      if (doc) lines.push(`- **${INTERVIEWERS[who].name}**: ${itemsText(who, doc.items, doc.na)}`);
    }
    const list = questionList(score);
    lines.push("", `## 질문 ${list.length}개`, "");
    for (const q of list) {
      const spec = item(q.interviewer, q.item);
      lines.push(`### Q${q.no}. [${INTERVIEWERS[q.interviewer].name} · ${spec.name}] ${q.question}`, "");
      for (const e of q.evidence) lines.push(`- 근거(${e.status}): ${DOC_NAMES[e.doc] ?? pyStr(e.doc)} ${pyStr(e.line)}줄 "${e.quote}"`);
      if (!q.grounded) lines.push(q.evidence.length ? "- 근거 원문을 입력 파일에서 찾지 못했습니다. 일반 질문으로 봅니다." : "- 근거 없음(일반 질문)");
      if (q.direction) lines.push(`- 좋은 답의 방향: ${q.direction}`);
      lines.push("");
    }
    lines.push("## 고칠 점", "");
    for (const who of ORDER) {
      for (const fix of ((score.document[who] || {}).fixes || [])) lines.push(`- [${INTERVIEWERS[who].name}] ${fix}`);
    }
    return done(lines);
  }

  function renderPractice(meta, score) {
    const lines = [`# 실전 연습 기록: ${meta.company || "회사 미지정"} (${meta.date})`, "", `> ${NOTICE}`, ""];
    score.answers.forEach((a, i) => {
      const who = INTERVIEWERS[a.interviewer].name;
      const tag = a.no ? `Q${a.no}` : "추가 질문";
      lines.push(`## ${i + 1}. ${tag} [${who} · ${a.level}] ${a.question}`, "", `**내 답**: ${a.answer}`, "");
      for (const f of a.followups) lines.push(`- 꼬리 질문: ${f.question}`, `  - 내 답: ${f.answer}`);
      lines.push("", `**답변 점수**: ${fmt(a.total)}/10 (${verdict(a.total)}) · ${itemsText(a.interviewer, a.items, a.na)}`);
      if (a.missing.length) lines.push(`**빠진 항목**: ${a.missing.join(", ")}`);
      if (a.better) lines.push(`**더 좋은 답의 뼈대**: ${a.better}`);
      lines.push("");
    });
    return done(lines);
  }

  // ---------- compare.py ----------
  function avg(values) {
    const v = Array.from(values).filter((x) => x !== null && x !== undefined);
    return v.length ? pyRound(v.reduce((s, x) => s + x, 0) / v.length, 1) : null;
  }

  function row(meta, score) {
    const byWho = {};
    for (const a of score.answers) (byWho[a.interviewer] = byWho[a.interviewer] || []).push(a.total);
    const document = {}, answers = {};
    for (const who of ORDER) {
      document[who] = (score.document[who] || {}).total ?? null;
      answers[who] = avg(byWho[who] || []);
    }
    return {
      session: meta.session, date: meta.date, company: meta.company || "",
      document, answers, answer_avg: avg(score.answers.map((a) => a.total)), answered: score.answers.length,
    };
  }

  function weakItems(pairs) {
    const low = new Map();
    for (const [meta, score] of pairs) {
      const ratios = new Map();
      for (const a of score.answers) {
        for (const [key, value] of Object.entries(a.items)) {
          if (value === null) continue;
          const k = `${a.interviewer}\u0000${key}`;
          if (!ratios.has(k)) ratios.set(k, []);
          ratios.get(k).push(value / item(a.interviewer, key).max);
        }
      }
      for (const [k, values] of ratios) {
        if (values.reduce((s, x) => s + x, 0) / values.length < LOW_RATIO) {
          if (!low.has(k)) low.set(k, []);
          low.get(k).push(meta.session);
        }
      }
    }
    const out = [];
    for (const [k, names] of low) {
      if (names.length < 2) continue;
      const [who, key] = k.split("\u0000");
      out.push({ interviewer: who, item: key, name: item(who, key).name, sessions: names });
    }
    out.sort((a, b) => b.sessions.length - a.sessions.length || ORDER.indexOf(a.interviewer) - ORDER.indexOf(b.interviewer) ||
      (a.item < b.item ? -1 : a.item > b.item ? 1 : 0));
    return out;
  }

  function retest(pairs) {
    const groups = new Map();
    for (const [meta, score] of pairs) {
      const key = JSON.stringify(["resume_letter", "posting"].map((k) => (meta.inputs[k] || {}).sha256 ?? null));
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push([meta, score]);
    }
    const out = [];
    for (const same of groups.values()) {
      if (same.length < 2) continue;
      for (const who of ORDER) {
        const totals = same.map(([, s]) => (s.document[who] || {}).total ?? null).filter((t) => t !== null);
        if (totals.length >= 2) {
          const diff = pyRound(Math.max(...totals) - Math.min(...totals), 1);
          out.push({ sessions: same.map(([m]) => m.session), interviewer: who, diff, over: diff > RETEST_LIMIT });
        }
      }
    }
    return out;
  }

  function compare(pairs) {
    const rows = pairs.map(([m, s]) => row(m, s));
    const withAnswers = rows.filter((r) => r.answer_avg !== null);
    let change = null;
    if (withAnswers.length >= 2) {
      const first = withAnswers[0], last = withAnswers[withAnswers.length - 1];
      const diff = pyRound(last.answer_avg - first.answer_avg, 1);
      change = {
        first: first.session, last: last.session, first_avg: first.answer_avg, last_avg: last.answer_avg, diff,
        sessions: withAnswers.length, goal: withAnswers.length < 3 ? null : diff >= GOAL_RISE,
      };
    }
    const real = pairs.flatMap(([, s]) => s.real.flatMap((r) => r.questions));
    const hits = real.filter((q) => q.confirmed).length;
    return {
      sessions: rows,
      change,
      weak_items: weakItems(pairs),
      hit: { real_questions: real.length, confirmed: hits, rate: real.length ? pyRound(hits / real.length * 100, 0) : null },
      retest: retest(pairs),
    };
  }

  function renderCompare(result) {
    const names = ORDER.map((w) => INTERVIEWERS[w].name);
    const lines = [`# 새록 면접관 회차 비교 (${result.sessions.length}회)`, "", "## 답변 점수(10점, 면접관별 평균)", ""];
    lines.push("| 세션 | " + names.join(" | ") + " | 평균 | 답한 수 |", "|---|" + "---:|".repeat(names.length + 2));
    for (const r of result.sessions) {
      lines.push(`| ${r.session} | ` + ORDER.map((w) => fmt(r.answers[w])).join(" | ") + ` | ${fmt(r.answer_avg)} | ${r.answered} |`);
    }
    lines.push("", "## 서류 점수(10점)", "", "| 세션 | " + names.join(" | ") + " |", "|---|" + "---:|".repeat(names.length));
    for (const r of result.sessions) lines.push(`| ${r.session} | ` + ORDER.map((w) => fmt(r.document[w])).join(" | ") + " |");

    lines.push("", "## 변화", "");
    const c = result.change;
    if (!c) {
      lines.push("- 답변 기록이 있는 세션이 2개 이상이어야 변화를 셉니다.");
    } else {
      lines.push(`- 첫 세션 ${fmt(c.first_avg)}점 → 마지막 세션 ${fmt(c.last_avg)}점 (${fmtSigned(c.diff)}점, ${c.sessions}회)`);
      if (c.goal === null) lines.push(`- 목표(+${fmtG(GOAL_RISE)}점)는 세션 3회부터 판단합니다.`);
      else lines.push(`- 목표(+${fmtG(GOAL_RISE)}점): ${c.goal ? "달성" : "아직"}`);
    }

    lines.push("", "## 반복해서 낮은 항목", "");
    if (result.weak_items.length) {
      for (const w of result.weak_items) {
        lines.push(`- ${INTERVIEWERS[w.interviewer].name} · ${w.name}: ${w.sessions.length}회 (${w.sessions.join(", ")})`);
      }
    } else {
      lines.push("- 2회 이상 낮았던 항목이 없습니다.");
    }

    const h = result.hit;
    lines.push("", "## 실제 면접 적중률", "");
    if (h.rate === null) lines.push("- 실제 면접 질문 기록이 없습니다.");
    else lines.push(`- 실제 질문 ${h.real_questions}개 중 모의 질문과 비슷했다고 확인한 것 ${h.confirmed}개 (${h.rate}%)`);

    if (result.retest.length) {
      lines.push("", "## 같은 문서 재심사 차이", "");
      for (const r of result.retest) {
        const mark = r.over ? ` (허용 ${fmtG(RETEST_LIMIT)}점 넘음, 기준 설명을 다듬을 때)` : "";
        lines.push(`- ${INTERVIEWERS[r.interviewer].name}: ${fmtG(r.diff)}점${mark}`);
      }
    }
    return lines.join("\n") + "\n";
  }

  // ---------- terms.py ----------
  function pickTerms(data, industry, role, limit) {
    limit = limit || 20;
    const ind = data.industries.map((i) => i.id), rol = data.roles.map((r) => r.id);
    if (!ind.includes(industry)) throw new Error(`모르는 산업입니다: ${industry}. 가능한 값: ${ind.slice().sort().join(", ")}`);
    if (!rol.includes(role)) throw new Error(`모르는 직무입니다: ${role}. 가능한 값: ${rol.slice().sort().join(", ")}`);
    const lv = (t) => (INTERVIEW_LEVELS.includes(t.level) ? INTERVIEW_LEVELS.indexOf(t.level) : 9);
    const found = data.terms.filter((t) => t.industries.includes(industry) && t.roles.includes(role));
    found.sort((a, b) => b.importance - a.importance || lv(a) - lv(b) || (a.term < b.term ? -1 : a.term > b.term ? 1 : 0));
    const seen = new Set(), out = [];
    for (const t of found) {
      if (seen.has(t.term)) continue;
      seen.add(t.term);
      out.push({ term: t.term, original: t.original, level: t.level, importance: t.importance, definition: t.definition });
      if (out.length >= limit) break;
    }
    return { industry, role, terms: out };
  }

  const api = {
    INTERVIEWERS, ORDER, LEVELS, NOTICE, DOCS, DOC_NAMES, QUESTIONS_PER_INTERVIEWER, GOAL_RISE, LOW_RATIO, RETEST_LIMIT,
    pyRound, splitlines, item, autoNa, total10, verdict, scan, slug, sha256, createSession, checkItems, verifyEvidence,
    recordDocument, questionList, nextQuestion, recordAnswer, recordReal, renderReport, renderPractice,
    compare, renderCompare, pickTerms,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SaerokInterview = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
