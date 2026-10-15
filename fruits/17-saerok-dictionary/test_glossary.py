import json
import shutil
import subprocess
import unittest
from pathlib import Path

from glossary import (
    CELL_MINIMUM,
    DATA_JS_PATH,
    ROOT,
    cell_counts,
    load_catalog,
    load_terms,
    render_data_js,
    validate,
)

CORE_JS = ROOT / "web" / "saerok-core.js"
NODE = shutil.which("node")


def sense(industries, roles, level="입문", importance=3, status="verified", formula=None):
    return {
        "industries": industries,
        "roles": roles,
        "level": level,
        "importance": importance,
        "definition": "시험용 뜻입니다.",
        "formula": formula,
        "examples": ["시험용 예문입니다."],
        "sources": [{"title": "시험 출처", "url": "https://example.com/doc", "kind": "official", "checked_at": "2026-10-15"}]
        if status == "verified"
        else [],
        "status": status,
    }


def term(id, name, senses, original=None, korean=None, aliases=()):
    return {
        "id": id,
        "term": name,
        "original": original,
        "korean": korean,
        "aliases": list(aliases),
        "senses": senses,
        "related": [],
        "confusable": [],
    }


E, P = ["ecommerce"], ["platform"]
FIXTURE = [
    term("ltv", "LTV", [sense(E + P, ["marketing", "data"], "실무", 5, formula="LTV = A × B")],
         "Lifetime Value", "고객 생애 가치", ["엘티브이", "CLV"]),
    term("bounce_churn", "이탈률", [
        sense(E + P, ["data", "marketing"], "입문", 4),
        sense(E + P, ["cx", "pm"], "실무", 5),
    ], "Bounce rate / Churn rate", "이탈률", ["바운스율", "churn"]),
    term("backlog", "백로그", [
        sense(E + P, ["pm"], "입문", 5),
        sense(E + P, ["cx"], "실무", 3),
        sense(P, ["data"], "심화", 2, status="needs_check"),
    ], "Backlog", "백로그"),
    term("aov", "객단가", [sense(E, ["marketing"], "입문", 5, formula="AOV = 매출 ÷ 주문 수")], "Average Order Value", "평균 주문 금액", ["AOV"]),
    term("cpc", "CPC", [sense(E + P, ["marketing"], "입문", 4)], "Cost Per Click", "클릭당 비용"),
    term("cac", "CAC", [sense(E + P, ["marketing"], "실무", 5, formula="CAC = 비용 ÷ 신규 고객 수")], "Customer Acquisition Cost", "고객 획득 비용"),
    term("mmm", "마케팅 믹스 모델링", [sense(E + P, ["marketing"], "심화", 3)], "Marketing Mix Modeling", "마케팅 믹스 모델링", ["MMM"]),
    term("roas", "ROAS", [sense(E + P, ["marketing"], "입문", 5, status="needs_check")], "Return On Ad Spend", "광고 수익률"),
]

CATALOG_FIXTURE = {
    "industries": [{"id": "ecommerce", "name": "이커머스"}, {"id": "platform", "name": "플랫폼"}],
    "roles": [{"id": r, "name": r} for r in ("pm", "data", "marketing", "cx")],
    "purposes": [
        {"id": "first_week", "name": "입사 첫 주", "keywords": ["입사", "첫 주"], "levels": ["입문", "실무"], "level_first": True},
        {"id": "interview", "name": "면접 준비", "keywords": ["면접"], "levels": ["실무", "심화"]},
        {"id": "metrics", "name": "지표 이해", "keywords": ["지표"], "levels": ["입문", "실무", "심화"], "requires_formula": True},
    ],
}


def run_core(script: str, data):
    """saerok-core.js를 Node로 불러 `core`, `data`로 script를 실행하고 JSON 결과를 돌려줍니다."""
    program = (
        "const core = require(process.argv[1]);"
        "const data = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
        f"const out = (() => {{ {script} }})();"
        "process.stdout.write(JSON.stringify(out));"
    )
    done = subprocess.run(
        [NODE, "-e", program, str(CORE_JS)],
        input=json.dumps(data, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(done.stdout)


class GlossaryDataTest(unittest.TestCase):
    """실제 용어집이 PRD v1.7 9장 형식과 11장 완료 기준을 지키는지 확인합니다."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.terms = load_terms()

    def test_catalog_lists_first_industries_and_roles(self):
        self.assertEqual([x["id"] for x in self.catalog["industries"]], ["ecommerce", "platform", "finance"])
        self.assertEqual([x["id"] for x in self.catalog["roles"]], ["pm", "data", "marketing", "cx"])
        self.assertEqual({p["id"] for p in self.catalog["purposes"]}, {"first_week", "interview", "metrics"})

    def test_terms_have_no_format_errors(self):
        self.assertEqual(validate(self.catalog, self.terms), [])

    def test_every_cell_has_enough_terms_with_all_levels(self):
        for (industry, role), count in cell_counts(self.catalog, self.terms).items():
            self.assertGreaterEqual(count, CELL_MINIMUM, f"{industry}×{role}")
            levels = {
                s["level"]
                for t in self.terms
                for s in t["senses"]
                if industry in s["industries"] and role in s["roles"]
            }
            self.assertEqual(levels, {"입문", "실무", "심화"}, f"{industry}×{role}")

    def test_unchecked_senses_never_claim_sources_as_verified(self):
        for t in self.terms:
            for s in t["senses"]:
                if s["status"] == "verified":
                    self.assertTrue(s["sources"], t["id"])
                    for src in s["sources"]:
                        self.assertTrue(src["url"].startswith("https://"), t["id"])
                        self.assertNotIn("example.com", src["url"], t["id"])

    def test_formula_only_on_metric_like_terms(self):
        for t in self.terms:
            for s in t["senses"]:
                if s.get("formula"):
                    self.assertIn("=", s["formula"], t["id"])

    def test_data_js_matches_json_files(self):
        self.assertTrue(DATA_JS_PATH.exists(), "python glossary.py build를 실행해 주세요")
        self.assertEqual(
            DATA_JS_PATH.read_text(encoding="utf-8"),
            render_data_js(self.catalog, self.terms),
            "data.js가 JSON과 다릅니다. python glossary.py build를 실행해 주세요",
        )


class GlossaryValidateTest(unittest.TestCase):
    def test_verified_sense_without_source_is_rejected(self):
        bad = sense(E, ["pm"])
        bad["sources"] = []
        errors = validate(CATALOG_FIXTURE, [term("x", "X", [bad])])
        self.assertTrue(any("verified" in e for e in errors))

    def test_unknown_role_level_and_duplicate_term_are_rejected(self):
        odd = sense(E, ["sales"], level="고급")
        errors = validate(CATALOG_FIXTURE, [term("a", "같은말", [odd]), term("b", "같은말", [sense(E, ["pm"])])])
        joined = "\n".join(errors)
        self.assertIn("직무", joined)
        self.assertIn("난이도", joined)
        self.assertIn("같은 표제어", joined)

    def test_non_https_source_is_rejected(self):
        s = sense(E, ["pm"])
        s["sources"][0]["url"] = "http://example.com"
        errors = validate(CATALOG_FIXTURE, [term("x", "X", [s])])
        self.assertTrue(any("https" in e for e in errors))


@unittest.skipUnless(NODE, "Node.js가 없어 saerok-core.js 검사를 건너뜁니다")
class GlossaryCoreTest(unittest.TestCase):
    def test_search_by_term_original_korean_alias_and_spacing(self):
        script = (
            "return ['LTV', 'ltv', 'Lifetime Value', '고객 생애 가치', '고객생애가치', '엘티브이', 'clv', 'AOV', '바운스율']"
            ".map(q => core.search(data, q).exact.map(t => t.id));"
        )
        found = run_core(script, FIXTURE)
        self.assertEqual(found, [["ltv"]] * 7 + [["aov"], ["bounce_churn"]])

    def test_partial_search_and_empty_result(self):
        out = run_core(
            "return [core.search(data, '생애').partial.map(t => t.id), core.search(data, '없는말').exact.length, core.search(data, '없는말').partial.length];",
            FIXTURE,
        )
        self.assertEqual(out, [["ltv"], 0, 0])

    def test_selected_cell_sense_comes_first_as_circled_one(self):
        script = (
            "const t = data.find(x => x.id === 'backlog');"
            "return [['ecommerce','pm'], ['ecommerce','cx'], ['platform','data'], ['ecommerce','data']]"
            ".map(([i, r]) => core.orderSenses(t, i, r).map(o => [o.number, o.sense.level, o.matched]));"
        )
        pm, cx, pdata, edata = run_core(script, FIXTURE)
        self.assertEqual(pm, [["①", "입문", True], ["②", "실무", False], ["③", "심화", False]])
        self.assertEqual(cx, [["①", "실무", True], ["②", "입문", False], ["③", "심화", False]])
        self.assertEqual(pdata[0], ["①", "심화", True])
        # 고른 칸에 맞는 뜻이 없으면 직무가 맞는 뜻을 먼저, 그다음 원래 순서를 지킵니다.
        self.assertEqual(edata[0], ["①", "심화", False])

    def test_today_term_prefers_unseen_beginner_and_stays_for_the_day(self):
        script = (
            "const a = core.pickToday(data, 'ecommerce', 'marketing', [], null, '2026-10-15');"
            "const b = core.pickToday(data, 'ecommerce', 'marketing', ['aov'], null, '2026-10-15');"
            "const kept = core.pickToday(data, 'ecommerce', 'marketing', ['aov'],"
            "  {date: '2026-10-15', industry: 'ecommerce', role: 'marketing', id: 'aov'}, '2026-10-15');"
            "const next = core.pickToday(data, 'ecommerce', 'marketing', ['aov'],"
            "  {date: '2026-10-14', industry: 'ecommerce', role: 'marketing', id: 'aov'}, '2026-10-15');"
            "const seenBeginners = ['aov', 'roas', 'cpc', 'bounce_churn'];"
            "const practice = core.pickToday(data, 'ecommerce', 'marketing', seenBeginners, null, '2026-10-15');"
            "const all = data.map(t => t.id);"
            "const none = core.pickToday(data, 'ecommerce', 'marketing', all, null, '2026-10-15');"
            "return [a.term.id, b.term.id, kept.term.id, kept.kept, next.term.id, practice.term.id, practice.sense.level, none];"
        )
        a, b, kept, kept_flag, nxt, practice, level, none = run_core(script, FIXTURE)
        # 입문·중요도 5 중 확인된 뜻(aov)이 확인 필요 뜻(roas)보다 먼저입니다.
        self.assertEqual(a, "aov")
        self.assertEqual(b, "roas")
        self.assertEqual((kept, kept_flag), ("aov", True))
        self.assertEqual(nxt, "roas")
        self.assertEqual((practice, level), ("cac", "실무"))
        self.assertIsNone(none)

    def test_today_term_prefers_industry_specific_term_within_level(self):
        terms = FIXTURE + [term("cpm", "CPM", [sense(E, ["marketing"], "입문", 3)], "Cost Per Mille", "노출당 비용")]
        script = (
            "return core.todayCandidates(data, 'ecommerce', 'marketing', ['aov']).map(x => x.term.id).slice(0, 3);"
        )
        # 입문 중 이커머스 전용인 cpm(중요도 3)이 공통 용어 roas(중요도 5)보다 먼저입니다.
        self.assertEqual(run_core(script, terms), ["cpm", "roas", "bounce_churn"])

    def test_purpose_lists_are_ordered_and_paged_by_ten(self):
        catalog = CATALOG_FIXTURE
        script = (
            "const [terms, catalog] = data;"
            "const p = id => catalog.purposes.find(x => x.id === id);"
            "const ids = list => list.map(x => x.term.id);"
            "const many = Array.from({length: 23}, (_, i) => ({id: 't' + i, term: 'T' + i, senses: [{industries: ['ecommerce'], roles: ['marketing'], level: '실무', importance: 1 + (i % 5), status: 'verified'}]}));"
            "const paged = core.page(core.purposeList(many, p('interview'), 'ecommerce', 'marketing'), 2, 10);"
            "return {"
            " first: ids(core.purposeList(terms, p('first_week'), 'ecommerce', 'marketing')),"
            " interview: ids(core.purposeList(terms, p('interview'), 'ecommerce', 'marketing')),"
            " metrics: ids(core.purposeList(terms, p('metrics'), 'ecommerce', 'marketing')),"
            " match: [core.matchPurpose(catalog, '입사 첫 주에 알아야 할 용어').id, core.matchPurpose(catalog, '면접 전에 볼 지표').id, core.matchPurpose(catalog, 'LTV')],"
            " page0: core.page(core.purposeList(many, p('interview'), 'ecommerce', 'marketing'), 0, 10).items.length,"
            " paged: [paged.items.length, paged.hasMore, paged.total]"
            "};"
        )
        out = run_core(script, [FIXTURE, catalog])
        self.assertEqual(out["first"], ["aov", "roas", "bounce_churn", "cpc", "cac", "ltv"])
        self.assertEqual(out["interview"], ["cac", "ltv", "mmm"])
        self.assertEqual(out["metrics"], ["aov", "cac", "ltv"])
        self.assertEqual(out["match"], ["first_week", "interview", None])
        self.assertEqual(out["page0"], 10)
        self.assertEqual(out["paged"], [3, False, 23])

    def test_missing_terms_are_merged_and_exported(self):
        script = (
            "let list = core.addMissing([], '리드 스코어링', '2026-10-14');"
            "list = core.addMissing(list, '리드스코어링', '2026-10-15');"
            "list = core.addMissing(list, '  ', '2026-10-15');"
            "list = core.addMissing(list, 'say \"hi\"', '2026-10-15');"
            "return [list, core.missingCsv(list)];"
        )
        items, csv = run_core(script, None)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0], {"query": "리드 스코어링", "first_seen": "2026-10-14", "last_seen": "2026-10-15", "count": 2})
        self.assertEqual(csv.splitlines()[0], "query,count,first_seen,last_seen")
        self.assertIn('"say ""hi"""', csv)


if __name__ == "__main__":
    unittest.main()
