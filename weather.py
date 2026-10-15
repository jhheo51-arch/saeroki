"""서울 날씨를 아침 추천에 전달하는 최소 수집기."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SEOUL = {"latitude": 37.5665, "longitude": 126.9780}


@dataclass(frozen=True)
class WeatherObservation:
    city: str
    condition: str
    temperature_c: float | None
    observed_at: str


def weather_code_label(code: int) -> str:
    if code == 0:
        return "맑음"
    if code in {1, 2, 3}:
        return "구름"
    if code in {45, 48}:
        return "안개"
    if code in {51, 53, 55, 56, 57}:
        return "이슬비"
    if code in {61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}:
        return "비"
    if code in {71, 73, 75, 77, 85, 86}:
        return "눈"
    return "알 수 없음"


def parse_weather_payload(payload: dict[str, object]) -> WeatherObservation:
    current = payload.get("current")
    if not isinstance(current, dict):
        raise ValueError("날씨 응답에 current가 없습니다")
    code = current.get("weather_code")
    if not isinstance(code, int):
        raise ValueError("날씨 응답에 weather_code가 없습니다")
    temperature = current.get("temperature_2m")
    return WeatherObservation(
        city="서울",
        condition=weather_code_label(code),
        temperature_c=float(temperature) if isinstance(temperature, (int, float)) else None,
        observed_at=str(current.get("time") or datetime.now(timezone.utc).isoformat()),
    )


def fetch_seoul_weather(timeout: int = 10) -> WeatherObservation:
    params = {
        **SEOUL,
        "current": "temperature_2m,weather_code",
        "timezone": "Asia/Seoul",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "Saeroki/0.1 Seoul weather check"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode(response.headers.get_content_charset() or "utf-8"))
    return parse_weather_payload(payload)
