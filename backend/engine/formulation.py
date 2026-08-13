"""
Administerable rounding for a computed starting dose.

Pure functions — no I/O, no LLM. Does not change engine math. The raw
final_dose_* on the recommendation stays the estimate; this layer only
adds a labelled `administration` object the UI can show as "give".
"""

from __future__ import annotations

import re
from typing import Any, Optional


ROUNDING_FLAG_PCT = 10.0

# named frequencies (doses per day)
_NAMED_PER_DAY = {
    "od": 1.0,
    "qd": 1.0,
    "once": 1.0,
    "daily": 1.0,
    "qhs": 1.0,
    "nocte": 1.0,
    "bid": 2.0,
    "bd": 2.0,
    "tid": 3.0,
    "tds": 3.0,
    "qid": 4.0,
    "qds": 4.0,
}


def increment_mg(dose_mg: float) -> float:
    """Practical mg increment for a dose of this size (not drug-specific)."""
    mag = abs(float(dose_mg))
    if mag < 1:
        return 0.05
    if mag < 5:
        return 0.1
    if mag < 20:
        return 0.5
    if mag < 100:
        return 1.0
    if mag < 500:
        return 5.0
    return 10.0


def round_to_increment(value: float, increment: float) -> float:
    if increment <= 0:
        return value
    return round(value / increment) * increment


def parse_doses_per_day(
    interval: Optional[str] = None,
    suggested_interval_h: Optional[float] = None,
) -> Optional[float]:
    """How many administrations per 24 h, or None if unknown."""
    if suggested_interval_h is not None:
        try:
            h = float(suggested_interval_h)
        except (TypeError, ValueError):
            h = 0.0
        if h > 0:
            n = 24.0 / h
            if 0.5 <= n <= 24:
                return n
    if not interval:
        return None
    s = str(interval).strip().lower()
    compact = re.sub(r"[\s.]", "", s)

    m = re.search(r"(?:q|every|q\.?)(\d+(?:\.\d+)?)(h|hr|hrs|hour|hours)", compact)
    if m:
        hours = float(m.group(1))
        if hours > 0:
            n = 24.0 / hours
            if 0.5 <= n <= 24:
                return n

    for token, n in _NAMED_PER_DAY.items():
        if re.search(rf"\b{token}\b", s) or compact == token:
            return n
    return None


def _positive_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def build_administration(
    *,
    dose_mg_per_day: Optional[float],
    weight_kg: Optional[float],
    interval: Optional[str] = None,
    suggested_interval_h: Optional[float] = None,
    formulation_mg_per_ml: Optional[float] = None,
) -> Optional[dict[str, Any]]:
    """Return an administration dict, or None when there is no dose to round."""
    daily = _positive_float(dose_mg_per_day)
    if daily is None:
        return None

    inc_day = increment_mg(daily)
    rounded_day = round_to_increment(daily, inc_day)
    if rounded_day <= 0:
        rounded_day = inc_day

    wt = _positive_float(weight_kg)
    engine_mg_per_kg = (daily / wt) if wt else None
    rounded_mg_per_kg = (rounded_day / wt) if wt else None

    per_day = parse_doses_per_day(interval, suggested_interval_h)
    per_dose = None
    inc_dose = None
    rounded_per_dose = None
    if per_day:
        per_dose = daily / per_day
        inc_dose = increment_mg(per_dose)
        rounded_per_dose = round_to_increment(per_dose, inc_dose)
        if rounded_per_dose <= 0:
            rounded_per_dose = inc_dose
        # Keep daily consistent with rounded per-dose when we have a schedule.
        rounded_day = round(rounded_per_dose * per_day, 4)
        if wt:
            rounded_mg_per_kg = rounded_day / wt

    strength = _positive_float(formulation_mg_per_ml)
    volume = None
    if strength is not None:
        give_mg = rounded_per_dose if rounded_per_dose is not None else rounded_day
        volume = round(give_mg / strength, 3)

    delta_pct = abs(rounded_day - daily) / daily * 100.0
    flag = None
    if delta_pct > ROUNDING_FLAG_PCT:
        flag = (
            f"Rounding changes the daily dose by {delta_pct:.0f}% "
            f"({daily:.2f} → {rounded_day:g} mg/day). Check the increment against the formulation."
        )

    return {
        "engine_dose_mg_per_day": round(daily, 2),
        "engine_dose_mg_per_kg_per_day": (
            round(engine_mg_per_kg, 3) if engine_mg_per_kg is not None else None
        ),
        "rounded_dose_mg_per_day": round(rounded_day, 2),
        "rounded_dose_mg_per_kg_per_day": (
            round(rounded_mg_per_kg, 3) if rounded_mg_per_kg is not None else None
        ),
        "increment_mg": inc_day,
        "doses_per_day": round(per_day, 3) if per_day else None,
        "engine_dose_mg_per_dose": round(per_dose, 3) if per_dose is not None else None,
        "rounded_dose_mg_per_dose": (
            round(rounded_per_dose, 3) if rounded_per_dose is not None else None
        ),
        "increment_per_dose_mg": inc_dose,
        "formulation_mg_per_ml": strength,
        "volume_ml_per_dose": volume,
        "rounding_delta_pct": round(delta_pct, 1),
        "flag": flag,
    }


def attach_administration(rec: dict, case: Optional[dict] = None) -> dict:
    """Mutate `rec` with an `administration` object. Safe on blocked / null doses."""
    case = case or {}
    if rec.get("blocked"):
        rec["administration"] = None
        return rec
    daily = rec.get("final_dose_mg_per_day")
    admin = build_administration(
        dose_mg_per_day=daily,
        weight_kg=case.get("weight_kg"),
        interval=rec.get("interval"),
        suggested_interval_h=None,
        formulation_mg_per_ml=case.get("formulation_mg_per_ml"),
    )
    rec["administration"] = admin
    if admin and admin.get("flag"):
        flags = list(rec.get("flags") or [])
        if not any("Rounding changes" in str(f) for f in flags):
            flags.append(admin["flag"])
        rec["flags"] = flags
    return rec
