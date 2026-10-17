/* 새록 심사단 결정적 계층의 브라우저판. saerok_idea/(rubric·verdict·money·store)와 같은 규칙·같은 결과를 냅니다.
   test_saerok_idea.py가 node로 이 파일을 돌려 Python 결과와 같은지 검사합니다. AI는 쓰지 않습니다. */
(function (root) {
  "use strict";

  const ORDER = ["user_value", "business", "feasibility"];
  const JUDGES = {
    user_value: {
      name: "사용자 가치",
      question: "진짜 문제인가",
      criteria: ["문제를 겪는 사람이 구체적이다", "문제가 자주 생기거나 아프다", "지금 쓰는 방법보다 나은 점이 분명하다"],
    },
    business: {
      name: "사업성",
      question: "돈과 시장이 되는가",
      criteria: ["누가 돈이나 시간을 내는지 분명하다", "대체재와 경쟁 서비스보다 고를 이유가 있다", "가격이 비용을 넘을 수 있다"],
    },
    feasibility: {
      name: "실행 가능성",
      question: "혼자 만들 수 있는가",
      criteria: ["첫 버전을 혼자 몇 주 안에 만들 수 있다", "필요한 데이터·권한·제휴를 혼자 얻을 수 있다", "법·개인정보·안전 위험을 감당할 수 있다"],
    },
  };
  const SCORES = {
    1: "기준을 거의 못 채움",
    2: "기준 일부만 채우고 큰 빈틈이 있음",
    3: "기준을 채우지만 확인 안 된 가정에 기댐",
    4: "기준을 채우고 빈틈이 작음",
    5: "기준을 모두 채우고 근거가 있음",
  };
  const VOTES = ["진행", "조건부", "보류"];
  const ASSUMPTIONS = {
    problem: "문제가 실제로 있다",
    alternative: "사람들이 지금 다른 방법으로 해결한다",
    pay: "돈이나 시간을 낼 것이다",
  };
  const STATUSES = ["받침", "반박", "확인 못 함"];
  const EVIDENCE_KINDS = ["받침", "반박"];
  const FIELDS = { line: "아이디어 한 줄", what: "무엇을", who: "누구에게", money: "어떻게 돈을 버는지", why_now: "왜 지금" };
  const CORE_FIELDS = ["what", "who"];
  const UNKNOWN = "미정";
  const PANEL_SIZES = { "기본": 20, full: 100 };
  const NOTICE = "심사위원과 가상 패널은 AI 시뮬레이션입니다. 실제 수요나 구매 비율이 아니며, " +
    "만들지 말지의 최종 판단은 사용자가 합니다.";
  const INSUFFICIENT = "판단 보류(정보 부족)";
  const MONEY_NAMES = {
    price: "고객 한 명의 월 매출(원)",
    unit_cost: "고객 한 명에 드는 월 비용(원)",
    fixed_cost: "고객 수와 상관없는 월 고정비(원)",
  };
  const CALC_SOURCES = ["사용자 입력", "확인됨"];
  const PARTS = ["judge", "assumptions", "competitors", "panel", "money", "directions"];
  const DATE = /^\d{4}-\d{2}-\d{2}$/;

  const keys = (o) => Object.keys(o);
  const str = (v) => (typeof v === "string" ? v : "");
  const isInt = (v) => typeof v === "number" && Number.isInteger(v);

  // ---------- verdict.py ----------
  function unknown(value) {
    const v = str(value).trim();
    return !v || v === UNKNOWN;
  }

  function decide(idea, judges, assumptions) {
    const steps = [];
    const missing = CORE_FIELDS.filter((k) => unknown(idea[k])).map((k) => FIELDS[k]);
    if (missing.length) {
      steps.push(`핵심 칸이 미정: ${missing.join(", ")}`);
      return { verdict: INSUFFICIENT, steps };
    }
    const status = {};
    for (const a of assumptions) status[a.key] = a.status;
    if (Object.values(status).every((s) => s === "확인 못 함")) {
      steps.push("가정 3개를 모두 확인하지 못함");
      return { verdict: INSUFFICIENT, steps };
    }
    const votes = ORDER.map((k) => judges[k].vote);
    const count = {};
    for (const v of VOTES) count[v] = votes.filter((x) => x === v).length;
    const shown = VOTES.map((v) => `${v} ${count[v]}`).join(" · ");
    let verdict;
    if (count["보류"] >= 2) {
      verdict = "보류";
      steps.push(`투표 ${shown}: 보류 2표 이상이라 보류`);
    } else if (count["진행"] >= 2 && count["보류"] === 0) {
      verdict = "진행";
      steps.push(`투표 ${shown}: 진행 2표 이상, 보류 0표라 진행`);
    } else {
      verdict = "조건부";
      steps.push(`투표 ${shown}: 진행·보류 조건에 들지 않아 조건부`);
    }
    if (status.problem === "반박") {
      if (verdict !== "보류") steps.push(`'${ASSUMPTIONS.problem}' 가정이 반박되어 보류`);
      verdict = "보류";
    } else if (verdict === "진행") {
      const refuted = keys(ASSUMPTIONS).filter((k) => status[k] === "반박").map((k) => ASSUMPTIONS[k]);
      if (refuted.length) {
        verdict = "조건부";
        steps.push(`반박된 가정(${refuted.join(", ")})이 있어 진행을 조건부로 낮춤`);
      }
    }
    return { verdict, steps };
  }

  // ---------- money.py (Fraction 대신 BigInt 분수로 같은 값을 냅니다) ----------
  function frac(value) {
    let s = String(value).toLowerCase();
    let exp = 0;
    if (s.includes("e")) {
      const [m, e] = s.split("e");
      s = m;
      exp = Number(e);
    }
    const [whole, part = ""] = s.split(".");
    let n = BigInt(whole + part);
    let d = 10n ** BigInt(part.length);
    if (exp > 0) n *= 10n ** BigInt(exp);
    if (exp < 0) d *= 10n ** BigInt(-exp);
    return reduce(n, d);
  }
  function gcd(a, b) {
    a = a < 0n ? -a : a;
    while (b) [a, b] = [b, a % b];
    return a || 1n;
  }
  function reduce(n, d) {
    const g = gcd(n, d);
    return { n: n / g, d: d / g };
  }
  function num(f) {
    return f.d === 1n ? Number(f.n) : Number(f.n) / Number(f.d);
  }

  function moneyValue(name, item) {
    if (item === undefined || item === null) return null;
    if (typeof item !== "object" || Array.isArray(item)) throw new Error(`${name}: {"value": 숫자, "source": 출처} 꼴이어야 합니다.`);
    if (!CALC_SOURCES.includes(item.source)) {
      throw new Error(`${name}: 출처는 ${CALC_SOURCES.join("·")}만 계산에 씁니다(받은 값 ${JSON.stringify(item.source)}). ` +
        "AI 추정 값으로는 계산하지 않습니다.");
    }
    if (item.source === "확인됨" && !(item.url && item.checked)) throw new Error(`${name}: '확인됨' 값에는 url과 확인 날짜(checked)가 필요합니다.`);
    const v = item.value;
    if (typeof v !== "number" || !Number.isFinite(v) || v < 0) throw new Error(`${name}: 0 이상의 숫자여야 합니다(받은 값 ${JSON.stringify(v)}).`);
    return frac(v);
  }

  function breakeven(money) {
    const values = {};
    for (const k of keys(MONEY_NAMES)) values[k] = moneyValue(k, money[k]);
    const needed = keys(MONEY_NAMES).filter((k) => values[k] === null).map((k) => MONEY_NAMES[k]);
    if (needed.length) return { computed: false, needed };
    const p = values.price, u = values.unit_cost, f = values.fixed_cost;
    const margin = reduce(p.n * u.d - u.n * p.d, p.d * u.d);
    const out = { computed: true, margin: num(margin) };
    if (margin.n <= 0n) {
      out.customers = null;
      out.note = "월 매출이 고객당 비용보다 크지 않아 고객이 늘어도 손익분기에 닿지 않습니다.";
    } else {
      const top = f.n * margin.d, bottom = f.d * margin.n;
      out.customers = Number((top + bottom - 1n) / bottom);
      out.note = "고정비를 고객당 남는 돈으로 나눈 뒤 올림한 월 고객 수입니다.";
    }
    return out;
  }

  // ---------- store.py 검사 ----------
  function slug(text) {
    let t = String(text).trim().replace(/[\\/:*?"<>|\s]+/g, "-").replace(/^[-.]+|[-.]+$/g, "");
    t = Array.from(t).slice(0, 30).join("").replace(/^[-.]+|[-.]+$/g, "");
    return t || "이름-없음";
  }

  function cleanIdea(idea) {
    idea = idea || {};
    const line = str(idea.line).trim();
    if (!line) throw new Error("아이디어 한 줄이 필요합니다.");
    const out = { line };
    for (const k of ["what", "who", "money", "why_now"]) out[k] = str(idea[k]).trim() || UNKNOWN;
    return out;
  }

  function text(value, what) {
    if (typeof value !== "string" || !value.trim()) throw new Error(`${what}이(가) 비어 있습니다.`);
    return value.trim();
  }

  function texts(values, what, low, high) {
    const items = (values || []).filter((v) => typeof v === "string" && v.trim()).map((v) => v.trim());
    if (items.length < low || items.length > high) throw new Error(`${what}은(는) ${low}~${high}개여야 합니다(받은 수 ${items.length}).`);
    return items;
  }

  function link(item, what) {
    const url = str(item.url).trim(), checked = str(item.checked).trim();
    if (!/^https?:\/\//.test(url)) throw new Error(`${what}: 링크(url)가 http로 시작해야 합니다. 링크가 없으면 근거로 쓰지 않습니다.`);
    if (!DATE.test(checked)) throw new Error(`${what}: 확인 날짜(checked)가 YYYY-MM-DD 꼴이어야 합니다.`);
    return { url, checked };
  }

  function checkJudge(data) {
    const who = data.judge;
    if (!ORDER.includes(who)) throw new Error(`모르는 심사위원입니다: ${JSON.stringify(who)}. 가능한 값: ${ORDER.join(", ")}`);
    const score = data.score;
    if (!isInt(score) || score < 1 || score > 5) throw new Error(`${who}: 점수는 1~5 정수여야 합니다(받은 값 ${JSON.stringify(score)}).`);
    if (!VOTES.includes(data.vote)) throw new Error(`${who}: 투표는 ${VOTES.join("·")} 중 하나여야 합니다.`);
    return {
      judge: who,
      score,
      vote: data.vote,
      reasons: texts(data.reasons, `${who} 이유`, 1, 3),
      concerns: texts(data.concerns, `${who} 걸리는 점`, 1, 3),
    };
  }

  function checkAssumptions(data) {
    const items = Array.isArray(data) ? data : data && data.assumptions;
    const want = keys(ASSUMPTIONS).slice().sort();
    if (!Array.isArray(items) || JSON.stringify(items.map((a) => a && a.key).sort()) !== JSON.stringify(want)) {
      throw new Error(`가정은 ${keys(ASSUMPTIONS).join(", ")} 세 개가 하나씩 있어야 합니다.`);
    }
    return keys(ASSUMPTIONS).map((key) => {
      const a = items.find((x) => x.key === key);
      const status = a.status;
      if (!STATUSES.includes(status)) throw new Error(`${key}: 결과는 ${STATUSES.join("·")} 중 하나여야 합니다.`);
      const evidence = (a.evidence || []).map((e, i) => {
        const n = i + 1;
        if (!EVIDENCE_KINDS.includes(e.kind)) throw new Error(`${key} 근거 ${n}: kind는 받침·반박 중 하나여야 합니다.`);
        return { kind: e.kind, title: text(e.title, `${key} 근거 ${n} 제목`), ...link(e, `${key} 근거 ${n}`), note: str(e.note).trim() };
      });
      if (EVIDENCE_KINDS.includes(status) && !evidence.some((e) => e.kind === status)) {
        throw new Error(`${key}: '${status}'이면 그 쪽 근거가 하나 이상 있어야 합니다. 없으면 '확인 못 함'입니다.`);
      }
      return {
        key,
        statement: text(a.statement, `${key} 가정 문장`),
        status,
        evidence,
        counter_query: text(a.counter_query, `${key} 반박 검색어(counter_query)`),
        user_check: str(a.user_check).trim(),
      };
    });
  }

  function checkCompetitors(data) {
    const queries = texts(data.queries, "검색어", 1, 10);
    if (!DATE.test(str(data.checked))) throw new Error("경쟁 조사 날짜(checked)가 YYYY-MM-DD 꼴이어야 합니다.");
    const items = (data.items || []).map((c, i) => {
      const n = i + 1;
      return { name: text(c.name, `경쟁 ${n} 이름`), ...link(c, `경쟁 ${n}`), diff: text(c.diff, `경쟁 ${n} 차이`),
        source: c.user_added ? "사용자 입력" : "확인됨" };
    });
    return { queries, checked: data.checked, items };
  }

  function checkPanel(data) {
    const size = data.size;
    if (!Object.values(PANEL_SIZES).includes(size)) throw new Error(`패널은 ${Object.values(PANEL_SIZES).join(" 또는 ")}명이어야 합니다.`);
    const personas = data.personas || [];
    if (personas.length < 3 || personas.length > 4) throw new Error("페르소나 유형은 3~4개여야 합니다.");
    let total = 0;
    for (const p of personas) {
      text(p.type, "페르소나 유형");
      if (!isInt(p.count) || p.count < 1) throw new Error("페르소나 count는 1 이상의 정수여야 합니다.");
      total += p.count;
    }
    if (total !== size) throw new Error(`페르소나 count 합(${total})이 패널 규모(${size})와 같아야 합니다.`);
    const against = (data.against || []).map((r) => ({ reason: text(r.reason, "반대 이유"), types: (r.types || []).filter((t) => t) }));
    return {
      size,
      personas: personas.map((p) => ({ type: p.type.trim(), count: p.count })),
      against,
      for: (data.for || []).map((f) => f.trim()).filter((f) => f),
    };
  }

  function checkDirections(data) {
    const items = data.directions || [];
    if (items.length < 2 || items.length > 3) throw new Error(`방향은 2~3개여야 합니다(받은 수 ${items.length}).`);
    const out = items.map((d, i) => {
      const n = i + 1;
      return {
        title: text(d.title, `방향 ${n} 이름`),
        idea: cleanIdea(d.idea || {}),
        changed: text(d.changed, `방향 ${n}에서 바꾼 것`),
        addresses: texts(d.addresses, `방향 ${n}이 해결하는 지적`, 1, 5),
        user_checks: (d.user_checks || []).map((c) => c.trim()).filter((c) => c),
      };
    });
    const pick = data.recommended;
    if (!isInt(pick) || pick < 1 || pick > out.length) throw new Error(`추천(recommended)은 1~${out.length} 중 하나여야 합니다.`);
    return { items: out, recommended: pick, why: text(data.why, "추천 이유") };
  }

  function newResult(idea, date, origin) {
    return { version: 1, date, idea: cleanIdea(idea), from: origin || null, judges: {}, assumptions: null,
      competitors: null, panel: null, money: null, directions: null, replaced: [] };
  }

  // store.origin과 같습니다. prev는 이전 기록(result), verdictPath는 그 verdict.md 경로입니다.
  function originOf(prev, verdictPath, number) {
    const out = { verdict: verdictPath, direction: number || null, before: prev.idea };
    if (number) {
      const items = (prev.directions && prev.directions.items) || [];
      if (!(number >= 1 && number <= items.length)) throw new Error(`방향 ${number}이(가) 없습니다. 이 기록의 방향 수: ${items.length}`);
      const item = items[number - 1];
      Object.assign(out, { title: item.title, changed: item.changed, addresses: item.addresses });
    }
    return out;
  }

  // store.record와 같습니다. result를 바꾸고 검사한 값을 돌려줍니다.
  function record(result, part, data, now) {
    let clean, old, label;
    if (part === "judge") {
      clean = checkJudge(data);
      old = result.judges[clean.judge];
      result.judges[clean.judge] = clean;
      label = `judge:${clean.judge}`;
    } else if (part === "money") {
      clean = { values: data, breakeven: breakeven(data) };
      old = result.money;
      result.money = clean;
      label = "money";
    } else if (["assumptions", "competitors", "panel", "directions"].includes(part)) {
      clean = { assumptions: checkAssumptions, competitors: checkCompetitors, panel: checkPanel, directions: checkDirections }[part](data);
      old = result[part];
      result[part] = clean;
      label = part;
    } else {
      throw new Error(`모르는 단계입니다: ${part}. 가능한 값: ${PARTS.join(", ")}`);
    }
    if (old !== undefined && old !== null) result.replaced.push({ part: label, at: now || "", old });
    return clean;
  }

  function decideResult(result) {
    const missing = ORDER.filter((k) => !result.judges[k]).map((k) => JUDGES[k].name);
    if (missing.length) throw new Error(`심사위원 결과가 모자랍니다: ${missing.join(", ")}`);
    if (!result.assumptions) throw new Error("가정 검증 결과가 없습니다.");
    return decide(result.idea, result.judges, result.assumptions);
  }

  function compare(runs) {
    return runs.map(({ run, result }) => {
      let decided;
      try {
        decided = decideResult(result).verdict;
      } catch (e) {
        decided = "미완료";
      }
      const scores = {};
      for (const k of ORDER) scores[k] = result.judges[k] ? result.judges[k].score : null;
      const assumptions = {};
      for (const a of result.assumptions || []) assumptions[a.key] = a.status;
      return { run, line: result.idea.line, verdict: decided, scores, assumptions, from: result.from || null };
    });
  }

  // Python의 f"{값:,}"와 같게 세 자리마다 쉼표를 넣습니다.
  function comma(v) {
    const [whole, part] = String(v).split(".");
    const sign = whole.startsWith("-") ? "-" : "";
    const digits = whole.replace("-", "").replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return sign + digits + (part !== undefined ? "." + part : "");
  }

  function ideaRows(idea, other) {
    return keys(FIELDS).map((k) => (other ? `| ${FIELDS[k]} | ${other[k]} | ${idea[k]} |` : `| ${FIELDS[k]} | ${idea[k]} |`));
  }

  function changeRows(before, after) {
    return keys(FIELDS).filter((k) => before[k] !== after[k]).map((k) => `| ${FIELDS[k]} | ${before[k]} | ${after[k]} |`);
  }

  // store._growth와 같습니다. 바뀐 칸만 보여 줍니다.
  function growth(result) {
    const idea = result.idea, f = result.from || {}, d = result.directions;
    if (!f.before && !d) return [];
    const lines = ["## 아이디어가 이렇게 바뀌었어요", ""];
    if (f.before) {
      lines.push("### 이전 심사에서 이번 입력으로", "");
      if (f.direction) {
        lines.push(`- 고른 방향: 방향 ${f.direction}. ${f.title}`, `- 바꾼 것: ${f.changed}`, `- 해결하려던 지적: ${f.addresses.join(" / ")}`);
      }
      const rows = changeRows(f.before, idea);
      if (rows.length) lines.push("", "| 칸 | 이전 | 이번 |", "|---|---|---|", ...rows);
      else lines.push("- 입력은 이전과 같습니다.");
      lines.push("");
    }
    if (d) {
      const n = d.recommended, item = d.items[n - 1];
      lines.push(`### 이번 입력에서 추천 방향으로(방향 ${n}. ${item.title})`, "",
        `- 바꾼 것: ${item.changed}`, `- 왜: ${item.addresses.join(" / ")}`, `- 추천 이유: ${d.why}`);
      const rows = changeRows(idea, item.idea);
      const same = keys(FIELDS).filter((k) => idea[k] === item.idea[k]).map((k) => FIELDS[k]);
      if (rows.length) lines.push("", "| 칸 | 지금 | 추천 방향 |", "|---|---|---|", ...rows);
      else lines.push("- 입력 칸은 바꾸지 않았습니다.");
      if (rows.length && same.length) lines.push("", `그대로 둔 칸: ${same.join(", ")}`);
      lines.push("");
    }
    return lines;
  }

  // store.render와 같습니다. run은 기록 폴더 이름(날짜), verdictPath는 다음 단계 명령에 넣을 verdict.md 경로입니다.
  function render(result, run, verdictPath) {
    const decided = decideResult(result);
    const idea = result.idea;
    const lines = [`# 새록 심사단 판정: ${idea.line} (${run})`, "", `> ${NOTICE}`, ""];
    if (result.from) {
      const f = result.from;
      lines.push(`다시 심사: ${f.verdict}` + (f.direction ? `의 방향 ${f.direction}` : ""), "");
    }
    lines.push("## 판정", "", `**${decided.verdict}**`, "", ...decided.steps.map((s) => `- ${s}`), "");
    lines.push(...growth(result));
    lines.push("## 입력(사용자 입력)", "", "| 칸 | 내용 |", "|---|---|", ...ideaRows(idea));

    lines.push("", "## 심사위원(AI 시뮬레이션)", "", "| 심사위원 | 점수 | 투표 | 이유 | 걸리는 점 |", "|---|---:|---|---|---|");
    for (const k of ORDER) {
      const j = result.judges[k];
      lines.push(`| ${JUDGES[k].name} | ${j.score}/5 | ${j.vote} | ${j.reasons.join(" / ")} | ${j.concerns.join(" / ")} |`);
    }

    lines.push("", "## 핵심 가정 검증", "");
    for (const a of result.assumptions) {
      lines.push(`### ${ASSUMPTIONS[a.key]}: ${a.status}`, "", `- 가정: ${a.statement}`, `- 반박 근거를 먼저 찾은 검색어: ${a.counter_query}`);
      for (const e of a.evidence) {
        const note = e.note ? `: ${e.note}` : "";
        lines.push(`- ${e.kind}(확인됨, ${e.checked}): [${e.title}](${e.url})${note}`);
      }
      if (!a.evidence.length) lines.push("- 근거를 찾지 못했습니다(확인 못 함). 지어내지 않았습니다.");
      if (a.user_check) lines.push(`- 사용자가 직접 확인할 일: ${a.user_check}`);
      lines.push("");
    }

    const c = result.competitors;
    lines.push("## 경쟁 서비스", "");
    if (c) {
      lines.push(`찾은 범위: 검색어 ${c.queries.join(", ")} (${c.checked})`, "");
      if (c.items.length) {
        lines.push("| 이름 | 출처 | 차이 |", "|---|---|---|");
        for (const i of c.items) lines.push(`| [${i.name}](${i.url}) | ${i.source}, ${i.checked} | ${i.diff} |`);
      } else {
        lines.push("이 범위에서는 경쟁 서비스를 찾지 못했습니다. 없다는 뜻은 아닙니다.");
      }
    } else {
      lines.push("아직 조사하지 않았습니다.");
    }

    const p = result.panel;
    lines.push("", "## 가상 사용자 패널(AI 시뮬레이션)", "");
    if (p) {
      const types = p.personas.map((x) => `${x.type} ${x.count}명`).join(", ");
      lines.push(`패널 ${p.size}명: ${types}. 수요 예측이 아니라 반대 이유 모음이며 판정에 쓰지 않습니다.`, "");
      for (const r of p.against) lines.push(`- 반대: ${r.reason}` + (r.types.length ? ` (${r.types.join(", ")})` : ""));
      if (!p.against.length) lines.push("- 반대 이유가 하나도 나오지 않았습니다. 패널이 한쪽으로 쏠렸을 수 있습니다.");
      for (const x of p.for) lines.push(`- 찬성: ${x}`);
    } else {
      lines.push("아직 돌리지 않았습니다.");
    }

    const m = result.money;
    lines.push("", "## 손익분기", "");
    if (m && m.breakeven.computed) {
      const b = m.breakeven;
      for (const [key, name] of Object.entries(MONEY_NAMES)) {
        const v = m.values[key];
        lines.push(`- ${name}: ${comma(v.value)} (${v.source}${v.url ? ", " + v.url : ""})`);
      }
      lines.push(`- 고객당 남는 돈: ${comma(b.margin)}원`);
      lines.push(b.customers !== null ? `- 손익분기 월 고객 수: ${comma(b.customers)}명. ${b.note}` : `- ${b.note}`);
    } else if (m) {
      lines.push(`계산하지 않았습니다. 필요한 값: ${m.breakeven.needed.join(", ")}`);
    } else {
      lines.push("가격·비용 값이 없어 계산하지 않았습니다.");
    }

    const d = result.directions;
    lines.push("", "## 다듬은 방향(AI 제안)", "");
    if (d) {
      d.items.forEach((item, i) => {
        const n = i + 1;
        const mark = n === d.recommended ? " (추천)" : "";
        lines.push(`### 방향 ${n}. ${item.title}${mark}`, "", `- 바꾼 것: ${item.changed}`, `- 해결하는 지적: ${item.addresses.join(" / ")}`);
        for (const x of item.user_checks) lines.push(`- 직접 확인할 일: ${x}`);
        lines.push("", "| 칸 | 원래 입력 | 이 방향 |", "|---|---|---|", ...ideaRows(item.idea, idea), "");
      });
      lines.push(`추천 이유: ${d.why}`, "", "방향은 제안입니다. 원래 입력은 위 표에 그대로 남아 있습니다.", "");
    } else {
      lines.push("아직 만들지 않았습니다.", "");
    }

    lines.push("## 다음 단계", "");
    if (d) lines.push(`- 방향 하나를 다시 심사: \`/saerok-idea:judge --from "${verdictPath}" --direction <번호>\``);
    if (decided.verdict === "진행" || decided.verdict === "조건부") {
      lines.push(`- 기획으로 넘기기: \`/saerok-prd:design --from "${verdictPath}"\``);
    } else if (decided.verdict === INSUFFICIENT) {
      lines.push("- 미정 칸을 채우거나, 가정을 확인할 검색어를 바꿔 다시 심사하세요.");
    }
    return lines.join("\n").replace(/\s+$/, "") + "\n";
  }

  const api = {
    ORDER, JUDGES, SCORES, VOTES, ASSUMPTIONS, STATUSES, EVIDENCE_KINDS, FIELDS, CORE_FIELDS, UNKNOWN, PANEL_SIZES,
    NOTICE, INSUFFICIENT, MONEY_NAMES, PARTS, DATE,
    decide, breakeven, slug, cleanIdea, checkJudge, checkAssumptions, checkCompetitors, checkPanel, checkDirections,
    newResult, originOf, growth, record, decideResult, compare, render, comma,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SaerokIdea = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
