"""Hepatic-impairment dosing table: live extract + one resolver.

Fills a cited per-class contract (absolute mg | fold | contra | absent)
from label / guideline HI *dosing* text. Caution-only or excerpt-less
text is not a citation. Never invents a hepatic organ-function fraction.
"""

from __future__ import annotations

import re
from typing import Any, Optional


_CLASS_ORDER = ("A", "B", "C")
_TERM = {"A": "mild", "B": "moderate", "C": "severe"}
_TERM_TO_CLASS = {v: k for k, v in _TERM.items()}

_NOT_CITATION = "not a citation"

_CAUTION_ONLY = re.compile(
    r"\buse with caution\b|\bcaution(?:\s+is)?\s+advised\b",
    re.I,
)
_NO_ADJUST = re.compile(
    r"\bno(?:\s+dosage|\s+dose)?\s+adjustment(?:\s+is)?\s+necessary\b"
    r"|\bno(?:\s+dosage|\s+dose)\s+adjustment\b"
    r"|\bno adjustment(?:\s+is)?\s+necessary\b",
    re.I,
)
_CONTRA = re.compile(
    r"\b(?:do not use|should not be used|contraindicated|must not be used"
    r"|avoid(?:\s+use)?)\b",
    re.I,
)
_FOLD_PCT = re.compile(
    r"(?:reduc(?:e|ed|tion)|decrease[d]?|adjust(?:ed)?)\s+(?:to\s+)?"
    r"(\d+(?:\.\d+)?)\s*%"
    r"|(\d+(?:\.\d+)?)\s*%\s+of\s+(?:the\s+)?(?:normal|usual|recommended|target)?",
    re.I,
)
_ABS_MG = re.compile(
    r"(?:dose|doses)\s+(?:is|are|should be|of)?\s*"
    r"(\d+(?:\.\d+)?)\s*mg"
    r"|(\d+(?:\.\d+)?)\s*mg\s*(?:once\s+)?(?:daily|per\s+day|once a day|q\.?d\.?)",
    re.I,
)
_ADULT_DOSE = re.compile(
    r"(?:typical|usual)\s+adult\s+dose(?:\s+is|\s+of)\s+(\d+(?:\.\d+)?)\s*mg"
    r"|target\s+daily\s+dose\s+is\s+(\d+(?:\.\d+)?)\s*mg",
    re.I,
)
_FOR_IND = re.compile(r"\bfor\s+([^:]{3,80}):", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|(?<=;)\s+")

# Class mention: Child-Pugh A/B/C and/or mild/moderate/severe hepatic.
_CP_LETTER = re.compile(
    r"child[-\s]?pugh(?:\s+class)?\s*([ABC])\b",
    re.I,
)
_SEVERITY = re.compile(
    r"\b(mild|moderate|severe)\b(?:\s+hepatic\s+impairment)?",
    re.I,
)


def _absent_row() -> dict[str, Any]:
    return {"kind": "absent", "value": None, "label_term": None, "mapped": False}


def _row(kind: str, value: Optional[float], label_term: Optional[str], mapped: bool) -> dict[str, Any]:
    return {"kind": kind, "value": value, "label_term": label_term, "mapped": mapped}


def _is_hepatic_span(text: str) -> bool:
    low = text.lower()
    return "hepatic" in low or "child-pugh" in low or "child pugh" in low


def _classes_in(text: str) -> list[tuple[str, str, bool]]:
    """Return (class, label_term, mapped) mentions in hepatic HI language only."""
    found: dict[str, tuple[str, bool]] = {}
    for m in _CP_LETTER.finditer(text):
        cls = m.group(1).upper()
        found[cls] = (_TERM[cls], False)
    if _is_hepatic_span(text):
        for m in _SEVERITY.finditer(text):
            term = m.group(1).lower()
            cls = _TERM_TO_CLASS[term]
            found[cls] = (term, True)
    out = []
    for cls in _CLASS_ORDER:
        if cls in found:
            term, mapped = found[cls]
            out.append((cls, term, mapped))
    return out


def _instruction(text: str) -> tuple[Optional[str], Optional[float]]:
    """Return (kind, value) for a dosing instruction span, or (None, None)."""
    if _NO_ADJUST.search(text):
        return "fold", 1.0
    if _CONTRA.search(text):
        return "contraindicated", None
    fm = _FOLD_PCT.search(text)
    if fm:
        pct = float(fm.group(1) or fm.group(2))
        return "fold", pct / 100.0
    am = _ABS_MG.search(text)
    if am:
        mg = float(am.group(1) or am.group(2))
        return "absolute_mg_per_day", mg
    return None, None


def _typical_adult_dose(text: str) -> Optional[float]:
    m = _ADULT_DOSE.search(text)
    if not m:
        return None
    return float(m.group(1) or m.group(2))


def _indication_sections(text: str) -> list[tuple[Optional[str], str]]:
    matches = list(_FOR_IND.finditer(text))
    if not matches:
        return [(None, text)]
    sections: list[tuple[Optional[str], str]] = []
    if matches[0].start() > 0:
        head = text[: matches[0].start()].strip()
        if head:
            sections.append((None, head))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end() : end].strip()
        sections.append((m.group(1).strip(), body))
    return sections


def _norm_ind(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _pick_sections(
    sections: list[tuple[Optional[str], str]], indication: Optional[str]
) -> tuple[list[tuple[Optional[str], str]], bool]:
    named = [(n, b) for n, b in sections if n]
    stratified = len(named) >= 2
    if not stratified:
        return sections, False
    want = _norm_ind(indication)
    if not want:
        return sections, True
    picked = [(n, b) for n, b in named if want == _norm_ind(n) or want in _norm_ind(n)]
    return picked, True


def _hi_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]
    keep = [p for p in parts if _is_hepatic_span(p)]
    return keep or parts


def extract_hi_table(
    text: str,
    citation: str,
    indication: Optional[str] = None,
) -> dict[str, Any]:
    """Parse HI *dosing* text into the cited per-class table contract.

    Raises ValueError("... not a citation") when citation is empty or the
    text has no numeric / no-adjustment instruction (caution-only).
    """
    cite = (citation or "").strip()
    if not cite:
        raise ValueError(_NOT_CITATION)
    src = (text or "").strip()
    if not src:
        raise ValueError(_NOT_CITATION)

    sections, stratified = _pick_sections(_indication_sections(src), indication)
    work = " ".join(body for _n, body in sections).strip()
    sentences = _hi_sentences(work)

    classes = {c: _absent_row() for c in _CLASS_ORDER}
    mapping_flagged = False
    excerpt_bits: list[str] = []

    # Prefer per-sentence instructions so a later class is not overwritten
    # by the first fold/mg in the whole paragraph.
    spans = list(sentences) if sentences else [work]
    for span in spans:
        mentions = _classes_in(span)
        kind, value = _instruction(span)
        if kind is None or not mentions:
            continue
        excerpt_bits.append(span.strip())
        for cls, term, mapped in mentions:
            classes[cls] = _row(kind, value, term, mapped)
            if mapped:
                mapping_flagged = True
    if all(classes[c]["kind"] == "absent" for c in _CLASS_ORDER) and work not in spans:
        mentions = _classes_in(work)
        kind, value = _instruction(work)
        if kind is not None and mentions:
            excerpt_bits.append(work.strip())
            for cls, term, mapped in mentions:
                classes[cls] = _row(kind, value, term, mapped)
                if mapped:
                    mapping_flagged = True

    filled = any(classes[c]["kind"] != "absent" for c in _CLASS_ORDER)
    if not filled:
        raise ValueError(_NOT_CITATION)
    if _CAUTION_ONLY.search(src) and not any(
        classes[c]["kind"] in ("fold", "absolute_mg_per_day", "contraindicated")
        for c in _CLASS_ORDER
    ):
        raise ValueError(_NOT_CITATION)

    excerpt = " ".join(dict.fromkeys(excerpt_bits)) or work
    table_ind = indication
    if stratified and indication:
        table_ind = indication
    elif stratified:
        # Keep first named section's indication when caller did not pick.
        named = [n for n, _b in sections if n]
        table_ind = named[0] if named else indication

    return {
        "excerpt": excerpt.strip(),
        "citation": cite,
        "typical_adult_dose_mg_per_day": _typical_adult_dose(src),
        "indication": table_ind,
        "indication_stratified": stratified,
        "mapping_flagged": mapping_flagged,
        "classes": classes,
    }


def _abstain(reason: str) -> dict[str, Any]:
    return {
        "status": "abstain",
        "kind": None,
        "fold": None,
        "adult_dose_mg_per_day": None,
        "reason": reason,
    }


def resolve_hi_dose(
    table: dict,
    child_pugh_class: str,
    user_adult_dose_mg_per_day: Optional[float] = None,
    indication: Optional[str] = None,
) -> dict[str, Any]:
    """Resolve one Child-Pugh class against a cited HI table.

    Missing A/mild → fold 1.0. Missing B → C if present else abstain.
    Missing C → moderate/B else abstain. Fold-only with no adult dose → abstain.
    User adult dose overrides the label typical dose. Indication-stratified
    tables must match the case indication or abstain.
    """
    if not table or not table.get("classes"):
        return _abstain("no HI table")
    if table.get("indication_stratified"):
        want = _norm_ind(indication)
        have = _norm_ind(table.get("indication"))
        if not want or not have or not (want == have or want in have or have in want):
            return _abstain("indication-stratified table does not match case indication")

    cls = str(child_pugh_class or "").strip().upper()
    if cls not in _CLASS_ORDER:
        return _abstain(f"unknown Child-Pugh class {child_pugh_class!r}")

    classes = table["classes"]
    row = dict(classes.get(cls) or _absent_row())

    if row["kind"] == "absent":
        if cls == "A":
            row = _row("fold", 1.0, "mild", False)
        elif cls == "B":
            c_row = classes.get("C") or _absent_row()
            if c_row["kind"] == "absent":
                return _abstain("missing B/moderate row and no C/severe fallback")
            row = dict(c_row)
        else:  # C
            b_row = classes.get("B") or _absent_row()
            if b_row["kind"] == "absent":
                return _abstain("missing C/severe row and no B/moderate fallback")
            row = dict(b_row)

    adult = user_adult_dose_mg_per_day
    if adult is None:
        adult = table.get("typical_adult_dose_mg_per_day")
    try:
        adult_f = float(adult) if adult is not None else None
    except (TypeError, ValueError):
        adult_f = None

    if row["kind"] == "contraindicated":
        return {
            "status": "ok",
            "kind": "contraindicated",
            "fold": None,
            "adult_dose_mg_per_day": None,
            "reason": "label contraindicated in this class",
        }
    if row["kind"] == "absolute_mg_per_day":
        return {
            "status": "ok",
            "kind": "absolute_mg_per_day",
            "fold": (float(row["value"]) / adult_f) if adult_f else None,
            "adult_dose_mg_per_day": float(row["value"]),
            "reason": "absolute class dose from label",
        }
    if row["kind"] == "fold":
        if adult_f is None:
            return _abstain("fold-only HI instruction with no adult dose")
        fold = float(row["value"])
        return {
            "status": "ok",
            "kind": "fold",
            "fold": fold,
            "adult_dose_mg_per_day": adult_f * fold,
            "reason": f"label fold {fold} × adult dose {adult_f}",
        }
    return _abstain("no usable class instruction")


def apply_hi_resolution(case: dict, table: Optional[dict]) -> dict[str, Any]:
    """Facade-agnostic HI resolve: both adult HI and pediatric use this."""
    from engine.child_pugh import resolve_child_pugh

    patch = resolve_child_pugh(case)
    cls = patch.get("child_pugh") or case.get("child_pugh")
    user_dose = case.get("user_adult_dose_mg_per_day")
    if user_dose is None:
        user_dose = case.get("adult_dose_mg_per_day")
    return resolve_hi_dose(
        table or {},
        cls,
        user_adult_dose_mg_per_day=user_dose,
        indication=case.get("indication"),
    )


_LABEL_HI_FIELDS = (
    "dosage_and_administration",
    "warnings",
    "warnings_and_cautions",
    "use_in_specific_populations",
    "clinical_pharmacology",
)


def maybe_extract_hi_table(
    label: dict,
    *,
    drug: str = "",
    indication: Optional[str] = None,
) -> Optional[dict]:
    """Live-extract a cited HI table from an openFDA-style label dict.

    Returns the table or None when the label has no HI *dosing* citation.
    """
    if not label:
        return None
    chunks = []
    for key in _LABEL_HI_FIELDS:
        val = label.get(key)
        if val:
            chunks.append(str(val))
    if not chunks:
        return None
    text = " ".join(chunks)
    name = (drug or label.get("drug") or "drug").strip() or "drug"
    citation = f"openFDA drug label ({name}): dosage and administration / hepatic-impairment section"
    try:
        return extract_hi_table(text=text, citation=citation, indication=indication)
    except ValueError:
        return None
