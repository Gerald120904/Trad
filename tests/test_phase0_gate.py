from datetime import date

import pytest

from phase0.config import GateConfig
from phase0.download import dates
from phase0.audit import audit
from phase0.database import connect, views


def test_gate_is_spot_only(tmp_path):
    with pytest.raises(ValueError):
        GateConfig(market="um", symbol="BTCUSDT", start_date=date(2026, 7, 18),
                   end_date=date(2026, 7, 24), project_root=tmp_path)


def test_seven_inclusive_days():
    assert len(list(dates(date(2026, 7, 18), date(2026, 7, 24)))) == 7


def test_distinct_rows_are_not_reported_as_duplicates(tmp_path):
    config = GateConfig(
        market="spot", symbol="BTCUSDT", start_date=date(2026, 7, 18),
        end_date=date(2026, 7, 18), project_root=tmp_path
    )
    con = connect(config)
    con.execute("""INSERT INTO aggtrades VALUES
      ('spot','BTCUSDT','2026-07-18',1,1,100,1,10,10,1784332800000,
       1784332800000,'2026-07-18',false,true),
      ('spot','BTCUSDT','2026-07-18',2,2,101,1,11,11,1784332800001,
       1784332800001,'2026-07-18',false,true)""")
    views(con)
    result = audit(
        con, config,
        [{"date": "2026-07-18", "ok": True, "error": None}], []
    )
    duplicate_test = next(t for t in result["tests"] if t["name"] == "duplicate_rows")
    assert duplicate_test["observed"] == 0
