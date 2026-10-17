"""가격·비용으로 월 손익분기 고객 수를 계산합니다. 사용자 값이나 출처 있는 값만 씁니다(PRD 4장 12번)."""

import math
from fractions import Fraction

NAMES = {
    "price": "고객 한 명의 월 매출(원)",
    "unit_cost": "고객 한 명에 드는 월 비용(원)",
    "fixed_cost": "고객 수와 상관없는 월 고정비(원)",
}
CALC_SOURCES = ["사용자 입력", "확인됨"]


def _value(name: str, item) -> Fraction | None:
    if item is None:
        return None
    if not isinstance(item, dict):
        raise ValueError(f"{name}: {{\"value\": 숫자, \"source\": 출처}} 꼴이어야 합니다.")
    if item.get("source") not in CALC_SOURCES:
        raise ValueError(f"{name}: 출처는 {'·'.join(CALC_SOURCES)}만 계산에 씁니다(받은 값 {item.get('source')!r}). "
                         "AI 추정 값으로는 계산하지 않습니다.")
    if item["source"] == "확인됨" and not (item.get("url") and item.get("checked")):
        raise ValueError(f"{name}: '확인됨' 값에는 url과 확인 날짜(checked)가 필요합니다.")
    value = item.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name}: 0 이상의 숫자여야 합니다(받은 값 {value!r}).")
    return Fraction(str(value))


def breakeven(money: dict) -> dict:
    """값이 모자라면 계산하지 않고 필요한 값을 알려 줍니다."""
    values = {k: _value(k, money.get(k)) for k in NAMES}
    needed = [NAMES[k] for k, v in values.items() if v is None]
    if needed:
        return {"computed": False, "needed": needed}
    margin = values["price"] - values["unit_cost"]
    out = {"computed": True, "margin": _num(margin)}
    if margin <= 0:
        out.update(customers=None, note="월 매출이 고객당 비용보다 크지 않아 고객이 늘어도 손익분기에 닿지 않습니다.")
    else:
        out.update(customers=math.ceil(values["fixed_cost"] / margin),
                   note="고정비를 고객당 남는 돈으로 나눈 뒤 올림한 월 고객 수입니다.")
    return out


def _num(value: Fraction):
    return int(value) if value.denominator == 1 else float(value)
