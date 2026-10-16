"""태블로 프로젝트(TTJ)의 정제 CSV를 새록 SQL용 Parquet으로 바꿉니다.

python scripts/build_data.py --clean "<TTJ 정제 데이터 폴더>/clean"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

# 새록 SQL 표 이름 → 원본 CSV 파일 이름
# 지하철 시간대별(OA-12921, 공공누리 3유형 변경금지)과 보안등(이용 조건 확인 못 함)은
# 가공본을 다시 배포할 수 없거나 확인되지 않아 넣지 않습니다. data/SOURCES.md 참고.
TABLES = {
    "subway_daily": "subway_daily.csv",
    "subway_stations": "subway_station_coords_approx.csv",
    "bike_stations": "ddareungi_stations.csv",
    "bike_city_hourly": "ddareungi_city_hourly.csv",
    "bike_dong_hourly": "ddareungi_dong_quarterly_hourly.csv",
    "weather_daily": "weather_daily.csv",
    "weather_hourly": "weather_hourly.csv",
    "delivery_monthly": "delivery_dong_monthly.csv",
    "delivery_age_monthly": "delivery_dong_age_monthly.csv",
    "cafes": "cafes_quarterly.csv",
    "cafe_brand_dong": "cafe_brand_dong_quarterly.csv",
    "stores_dong": "stores_dong_quarterly.csv",
}

# 코드 성격의 컬럼은 숫자로 읽히지 않도록 문자열로 고정합니다.
TEXT_COLUMNS = {"adm_cd", "station_id", "station_no", "store_id", "snapshot_date"}


def build(clean_dir: Path, out_dir: Path = DATA_DIR) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    counts = {}
    for table, filename in TABLES.items():
        src = clean_dir / filename
        if not src.exists():
            raise FileNotFoundError(f"원본이 없습니다: {src}")
        header = con.execute("SELECT * FROM read_csv(?, header=true, sample_size=-1) LIMIT 0", [str(src)]).description
        text_cols = [name for name, *_ in header if name in TEXT_COLUMNS]
        types = ", types={" + ", ".join(f"'{c}': 'VARCHAR'" for c in text_cols) + "}" if text_cols else ""
        con.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, sample_size=-1{types})",
            [str(src)],
        )
        con.execute(f"COPY {table} TO '{(out_dir / (table + '.parquet')).as_posix()}' (FORMAT parquet, COMPRESSION zstd)")
        counts[table] = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]

    # 행정동 목록: 여러 표에 흩어진 행정동 코드·구·동 이름을 하나로 모읍니다.
    con.execute(
        """
        CREATE OR REPLACE TABLE dong AS
        SELECT adm_cd, any_value(gu) AS gu, any_value(dong) AS dong
        FROM (
            SELECT adm_cd, gu, dong FROM delivery_monthly
            UNION ALL SELECT adm_cd, gu, dong FROM stores_dong
        )
        WHERE adm_cd IS NOT NULL
        GROUP BY adm_cd
        ORDER BY adm_cd
        """
    )
    con.execute(f"COPY dong TO '{(out_dir / 'dong.parquet').as_posix()}' (FORMAT parquet, COMPRESSION zstd)")
    counts["dong"] = con.execute("SELECT count(*) FROM dong").fetchone()[0]
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", required=True, type=Path, help="TTJ 정제 CSV 폴더")
    args = parser.parse_args()
    for name, n in build(args.clean).items():
        print(f"{name}: {n:,}행")
