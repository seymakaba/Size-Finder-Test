#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bedenimi Bul - Python hesaplama motoru.

Bu dosya, bedenimi_bul.html içindeki JavaScript hesaplama mantığının Python'a
çevrilmiş halidir. Hesaplama sabitleri, ağırlıklar, eşik değerleri, yuvarlama
mantığı ve seçim kuralları değiştirilmeden korunmuştur.

Kullanım örneği:
    from bedenimi_bul import calculate

    sonuc = calculate(gender="female", height=166, weight=57)
    print(sonuc["topMain"], sonuc["bottomMain"])

Komut satırı:
    python bedenimi_bul.py --gender female --height 166 --weight 57
"""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional

Number = Optional[float]
Row = Dict[str, Any]


SIZE_TABLE: Dict[str, Dict[str, List[Row]]] = {
    "female": {
        "top": [
            {"label": "32 / 2XS", "short": "2XS", "fitScore": 0, "numeric": 32, "chest": 80},
            {"label": "34 / XS", "short": "XS", "fitScore": 1, "numeric": 34, "chest": 83},
            {"label": "36 / S", "short": "S", "fitScore": 2, "numeric": 36, "chest": 86},
            {"label": "38 / M", "short": "M", "fitScore": 3, "numeric": 38, "chest": 90},
            {"label": "40 / L", "short": "L", "fitScore": 4, "numeric": 40, "chest": 94},
            {"label": "42 / XL", "short": "XL", "fitScore": 5, "numeric": 42, "chest": 99},
            {"label": "44 / 2XL", "short": "2XL", "fitScore": 6, "numeric": 44, "chest": 104},
            {"label": "46 / 3XL", "short": "3XL", "fitScore": 7, "numeric": 46, "chest": 107},
            {"label": "48 / 4XL", "short": "4XL", "fitScore": 8, "numeric": 48, "chest": 113},
            {"label": "50 / 5XL", "short": "5XL", "fitScore": 9, "numeric": 50, "chest": 119},
        ],
        "bottom": [
            {"label": "32 / 2XS", "short": "2XS", "fitScore": 0, "numeric": 32, "waist": 62, "hip": 84},
            {"label": "34 / XS", "short": "XS", "fitScore": 1, "numeric": 34, "waist": 64, "hip": 90},
            {"label": "36 / S", "short": "S", "fitScore": 2, "numeric": 36, "waist": 68, "hip": 94},
            {"label": "38 / M", "short": "M", "fitScore": 3, "numeric": 38, "waist": 72, "hip": 98},
            {"label": "40 / L", "short": "L", "fitScore": 4, "numeric": 40, "waist": 78, "hip": 102},
            {"label": "42 / XL", "short": "XL", "fitScore": 5, "numeric": 42, "waist": 83, "hip": 107},
            {"label": "44 / 2XL", "short": "2XL", "fitScore": 6, "numeric": 44, "waist": 88, "hip": 112},
            {"label": "46 / 3XL", "short": "3XL", "fitScore": 7, "numeric": 46, "waist": 93, "hip": 117},
            {"label": "48 / 4XL", "short": "4XL", "fitScore": 8, "numeric": 48, "waist": 98, "hip": 122},
            {"label": "50 / 5XL", "short": "5XL", "fitScore": 9, "numeric": 50, "waist": 103, "hip": 127},
        ],
    },
    "male": {
        "top": [
            {"label": "34 / 2XS", "short": "2XS", "fitScore": 1, "numeric": 34, "chest": 89},
            {"label": "36 / XS", "short": "XS", "fitScore": 2, "numeric": 36, "chest": 92},
            {"label": "38 / S", "short": "S", "fitScore": 3, "numeric": 38, "chest": 96},
            {"label": "40 / M", "short": "M", "fitScore": 4, "numeric": 40, "chest": 100},
            {"label": "42 / L", "short": "L", "fitScore": 5, "numeric": 42, "chest": 104},
            {"label": "44 / XL", "short": "XL", "fitScore": 6, "numeric": 44, "chest": 109},
            {"label": "46 / 2XL", "short": "2XL", "fitScore": 7, "numeric": 46, "chest": 115},
            {"label": "48 / 3XL", "short": "3XL", "fitScore": 8, "numeric": 48, "chest": 119},
            {"label": "50 / 4XL", "short": "4XL", "fitScore": 9, "numeric": 50, "chest": 122.5},
            {"label": "52 / 5XL", "short": "5XL", "fitScore": 10, "numeric": 52, "chest": 126},
        ],
        "bottom": [
            {"label": "28", "short": "28", "fitScore": 1, "numeric": 28, "waist": 84},
            {"label": "29", "short": "29", "fitScore": 1.5, "numeric": 29, "waist": 85.25},
            {"label": "30", "short": "30", "fitScore": 2, "numeric": 30, "waist": 86.5},
            {"label": "31", "short": "31", "fitScore": 2.5, "numeric": 31, "waist": 87.75},
            {"label": "32", "short": "32", "fitScore": 3, "numeric": 32, "waist": 89},
            {"label": "33", "short": "33", "fitScore": 3.5, "numeric": 33, "waist": 90.25},
            {"label": "34", "short": "34", "fitScore": 4, "numeric": 34, "waist": 91.5},
            {"label": "36", "short": "36", "fitScore": 5, "numeric": 36, "waist": 94},
            {"label": "38", "short": "38", "fitScore": 6, "numeric": 38, "waist": 99},
            {"label": "40", "short": "40", "fitScore": 7, "numeric": 40, "waist": 104},
            {"label": "42", "short": "42", "fitScore": 8, "numeric": 42, "waist": 109},
            {"label": "44", "short": "44", "fitScore": 9, "numeric": 44, "waist": 114.5},
        ],
    },
}

BODY_TYPES: Dict[str, List[Dict[str, str]]] = {
    "female": [
        {"key": "rectangle", "label": "Dikdörtgen", "icon": "female_rectangle"},
        {"key": "pear", "label": "Armut", "icon": "female_pear"},
        {"key": "strawberry", "label": "Çilek", "icon": "female_strawberry"},
        {"key": "apple", "label": "Elma", "icon": "female_apple"},
        {"key": "hourglass", "label": "Kum saati", "icon": "female_hourglass"},
    ],
    "male": [
        {"key": "rectangle", "label": "Dikdörtgen", "icon": "male_rectangle"},
        {"key": "trapezoid", "label": "Trapez", "icon": "male_trapezoid"},
        {"key": "inverted", "label": "Ters üçgen", "icon": "male_inverted"},
        {"key": "triangle", "label": "Üçgen", "icon": "male_triangle"},
        {"key": "oval", "label": "Oval", "icon": "male_oval"},
        {"key": "slim", "label": "İnce uzun", "icon": "male_slim"},
    ],
}

WIDTH_EFFECT = {"narrow": -0.40, "medium": 0, "wide": 0.60}
WIDTH_LABEL = {"narrow": "Dar", "medium": "Orta", "wide": "Geniş"}

BODY_EFFECT = {
    "female": {
        "hourglass": {"upper": 0, "lower": 0},
        "pear": {"upper": -0.10, "lower": 0.35},
        "strawberry": {"upper": 0.35, "lower": -0.10},
        "rectangle": {"upper": 0, "lower": 0},
        "apple": {"upper": 0.15, "lower": 0.25},
    },
    "male": {
        "rectangle": {"upper": 0, "lower": 0},
        "trapezoid": {"upper": 0.10, "lower": 0},
        "inverted": {"upper": 0.30, "lower": -0.10},
        "triangle": {"upper": -0.10, "lower": 0.15},
        "oval": {"upper": 0.15, "lower": 0.15},
        "slim": {"upper": -0.25, "lower": -0.20},
    },
}

ESTIMATE_CONFIG = {
    "female": {
        "base": {"h": 165, "w": 57, "chest": 86, "waist": 68, "hip": 94},
        "neutralKgPerCm": 0.34,
        "coeff": {"chestKg": 0.43, "waistKg": 0.55, "hipKg": 0.50, "chestH": 0.05, "waistH": 0.03, "hipH": 0.04},
        "body": {
            "hourglass": {"chest": 0, "waist": -1, "hip": 1},
            "pear": {"chest": -1, "waist": 0, "hip": 3},
            "rectangle": {"chest": -0.5, "waist": 0, "hip": -1},
            "strawberry": {"chest": 2, "waist": 0, "hip": -1},
            "apple": {"chest": 1.5, "waist": 3, "hip": 0},
        },
        "build": {
            "upper": {"narrow": -1.2, "medium": 0, "wide": 1.2},
            "waist": {"narrow": -2, "medium": 0, "wide": 2},
            "hip": {"narrow": -2, "medium": 0, "wide": 2},
        },
    },
    "male": {
        "base": {"h": 176, "w": 78, "chest": 100, "waist": 89},
        "neutralKgPerCm": 0.45,
        "coeff": {"chestKg": 0.45, "waistKg": 0.58, "chestH": 0.06, "waistH": 0.03},
        "body": {
            "rectangle": {"chest": 0, "waist": 0},
            "trapezoid": {"chest": 1, "waist": 0},
            "inverted": {"chest": 2, "waist": -1},
            "triangle": {"chest": -0.5, "waist": 2},
            "oval": {"chest": 1.5, "waist": 4},
            "slim": {"chest": -2, "waist": -3},
        },
        "build": {
            "upper": {"narrow": -1.5, "medium": 0, "wide": 1.5},
            "waist": {"narrow": -3, "medium": 0, "wide": 3},
        },
    },
}

BRAND_REFERENCES = [
    {"code": "A", "gender": "female", "height": 166, "weight": 57, "bodyType": "hourglass", "topScore": 2, "bottomScore": 2},
    {"code": "B", "gender": "male", "height": 190, "weight": 127, "bodyType": "rectangle", "topScore": 8, "bottomScore": 7},
    {"code": "C", "gender": "male", "height": 184, "weight": 65, "bodyType": "rectangle", "topScore": 4, "bottomScore": 2},
    {"code": "D", "gender": "male", "height": 175, "weight": 74, "bodyType": "rectangle", "topScore": 4, "bottomScore": 2},
    {"code": "E", "gender": "male", "height": 178, "weight": 89, "bodyType": "rectangle", "topScore": 5, "bottomScore": 5},
    {"code": "F", "gender": "male", "height": 190, "weight": 107, "bodyType": "rectangle", "topScore": 6, "bottomScore": 5},
    {"code": "G", "gender": "male", "height": 185, "weight": 107, "bodyType": "rectangle", "topScore": 6, "bottomScore": 5},
    {"code": "H", "gender": "male", "height": 175, "weight": 73, "bodyType": "rectangle", "topScore": 4, "bottomScore": 2},
    {"code": "I", "gender": "female", "height": 159, "weight": 55, "bodyType": "rectangle", "topScore": 3, "bottomScore": 3},
    {"code": "J", "gender": "female", "height": 168, "weight": 98, "bodyType": "rectangle", "topScore": 6, "bottomScore": 6},
    {"code": "K", "gender": "female", "height": 164, "weight": 74, "bodyType": "pear", "topScore": 4, "bottomScore": 4},
    {"code": "L", "gender": "female", "height": 155, "weight": 54, "bodyType": "hourglass", "topScore": 2, "bottomScore": 1},
    {"code": "M", "gender": "female", "height": 170, "weight": 73, "bodyType": "pear", "topScore": 4, "bottomScore": 3},
    {"code": "N", "gender": "female", "height": 160, "weight": 61, "bodyType": "rectangle", "topScore": 2, "bottomScore": 2},
    {"code": "O", "gender": "male", "height": 176, "weight": 92, "bodyType": "rectangle", "topScore": 5, "bottomScore": 3},
    {"code": "P", "gender": "male", "height": 178, "weight": 87, "bodyType": "rectangle", "topScore": 5, "bottomScore": 3},
    {"code": "R", "gender": "male", "height": 182, "weight": 102, "bodyType": "rectangle", "topScore": 6, "bottomScore": 3},
]


def is_finite(value: Any) -> bool:
    """JavaScript Number.isFinite davranışına yakın kontrol."""
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return False


def js_round(value: float) -> int:
    """JavaScript Math.round eşdeğeri: Math.floor(x + 0.5)."""
    return math.floor(value + 0.5)


def round1(value: float) -> float:
    return js_round(value * 10) / 10


def round2(value: float) -> float:
    return js_round(value * 100) / 100


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def parse_num(value: Any) -> Number:
    """
    HTML'deki num(id) fonksiyonunun Python karşılığı.

    - None ve boş string -> None
    - Virgüllü ondalıklar desteklenir: "86,5" -> 86.5
    - Geçersiz değerler -> None
    """
    if value is None or value == "":
        return None
    if is_finite(value):
        return float(value)
    text = str(value).replace(",", ".")
    if text.strip() == "":
        # JS Number(" ") === 0 olduğu için bu özel durum korunur.
        return 0.0
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def fmt_num(value: Any) -> str:
    """JS template literal içindeki Number.toString çıktısına yakın kısa sayı formatı."""
    if value is None:
        return "null"
    if isinstance(value, float):
        if value == 0:
            return "0"
        return (f"{value:.12g}").rstrip("0").rstrip(".") if "." in f"{value:.12g}" else f"{value:.12g}"
    return str(value)


def bmi(height_cm: Number, weight_kg: Number) -> Number:
    if not is_finite(height_cm) or not is_finite(weight_kg) or height_cm <= 0 or weight_kg <= 0:
        return None
    meters = float(height_cm) / 100
    return float(weight_kg) / (meters * meters)


def bmi_base_score(gender: str, b: Number) -> float:
    if not is_finite(b):
        return 2.1 if gender == "female" else 3.0
    assert b is not None
    if gender == "female":
        if b < 18.0:
            return 0.8
        if b < 19.2:
            return 1.4
        if b < 20.3:
            return 2.1
        if b < 21.3:
            return 2.5
        if b < 22.5:
            return 3.0
        if b < 24.0:
            return 3.4
        if b < 26.0:
            return 4.0
        if b < 28.5:
            return 4.6
        if b < 31.0:
            return 5.4
        if b < 33.0:
            return 6.4
        if b < 35.5:
            return 7.6
        if b < 38.5:
            return 8.2
        return 8.8

    if b < 19.0:
        return 1.6
    if b < 21.5:
        return 2.2
    if b < 23.5:
        return 3.0
    if b < 25.0:
        return 3.9
    if b < 27.0:
        return 4.3
    if b < 29.5:
        return 4.8
    if b < 32.5:
        return 5.5
    if b < 35.5:
        return 6.2
    return 6.8


def height_adjustment(gender: str, height: Number) -> float:
    if not is_finite(height):
        return 0
    assert height is not None
    if gender == "female":
        if height < 157:
            return -0.40
        if height <= 170:
            return 0
        if height <= 178:
            return 0.25
        return 0.45

    if height < 168:
        return -0.25
    if height < 176:
        return 0
    if height < 180:
        return 0.10
    if height < 184:
        return 0.25
    if height <= 190:
        return 0.40
    return 0.55


def base_score(input_data: Dict[str, Any]) -> Dict[str, Any]:
    b = bmi(input_data.get("height"), input_data.get("weight"))
    bmi_score = bmi_base_score(input_data["gender"], b)
    h_adj = height_adjustment(input_data["gender"], input_data.get("height"))
    minimum = 0 if input_data["gender"] == "female" else 1
    return {
        "bmi": b,
        "bmiScore": bmi_score,
        "heightAdjustment": h_adj,
        "base": clamp(bmi_score + h_adj, minimum, 9),
    }


def nearest_by_metric(rows: List[Row], metric: str, value: float) -> Dict[str, Any]:
    ranked = [
        {"row": row, "index": index, "diff": abs(float(row[metric]) - value)}
        for index, row in enumerate(rows)
    ]
    ranked.sort(key=lambda item: (item["diff"], item["index"]))
    return {"main": ranked[0], "alternative": ranked[1] if len(ranked) > 1 else ranked[0], "ranked": ranked}


def measurement_top(gender: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    chest = input_data.get("chest")
    if not is_finite(chest):
        return None
    return nearest_by_metric(SIZE_TABLE[gender]["top"], "chest", float(chest))


def measurement_bottom(gender: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if gender == "male":
        waist = input_data.get("waist")
        if not is_finite(waist):
            return None
        return nearest_by_metric(SIZE_TABLE["male"]["bottom"], "waist", float(waist))

    has_waist = is_finite(input_data.get("waist"))
    has_hip = is_finite(input_data.get("hip"))
    if not has_waist and not has_hip:
        return None

    rows = SIZE_TABLE["female"]["bottom"]
    ranked = []
    for index, row in enumerate(rows):
        total = 0.0
        weight = 0.0
        if has_waist:
            total += abs(float(row["waist"]) - float(input_data["waist"])) * 0.25
            weight += 0.25
        if has_hip:
            total += abs(float(row["hip"]) - float(input_data["hip"])) * 0.75
            weight += 0.75
        ranked.append({"row": row, "index": index, "diff": total / weight})
    ranked.sort(key=lambda item: (item["diff"], item["index"]))
    return {"main": ranked[0], "alternative": ranked[1] if len(ranked) > 1 else ranked[0], "ranked": ranked}


def continuous_score(rows: List[Row], metric: str, value: Number) -> Number:
    sorted_rows = sorted(
        [row for row in rows if is_finite(row.get(metric)) and is_finite(row.get("fitScore"))],
        key=lambda row: row[metric],
    )
    if not sorted_rows or not is_finite(value):
        return None
    assert value is not None

    if value <= sorted_rows[0][metric]:
        return float(sorted_rows[0]["fitScore"])

    for index in range(1, len(sorted_rows)):
        prev = sorted_rows[index - 1]
        next_row = sorted_rows[index]
        if value <= next_row[metric]:
            ratio = (value - prev[metric]) / (next_row[metric] - prev[metric])
            return prev["fitScore"] + ratio * (next_row["fitScore"] - prev["fitScore"])

    return float(sorted_rows[-1]["fitScore"])


def estimate_body_measurements(input_data: Dict[str, Any]) -> Dict[str, Any]:
    cfg = ESTIMATE_CONFIG[input_data["gender"]]
    base = cfg["base"]
    height = input_data.get("height") if is_finite(input_data.get("height")) else base["h"]
    weight = input_data.get("weight") if is_finite(input_data.get("weight")) else base["w"]
    h_delta = height - base["h"]
    adjusted_kg = weight - (base["w"] + cfg["neutralKgPerCm"] * h_delta)

    body = cfg["body"].get(input_data.get("bodyType")) or cfg["body"].get("rectangle") or {"chest": 0, "waist": 0, "hip": 0}
    upper_build = cfg["build"].get("upper", {}).get(input_data.get("upperBuild"), 0) or 0
    waist_build = cfg["build"].get("waist", {}).get(input_data.get("waistBuild"), 0) or 0

    chest = (
        base["chest"]
        + adjusted_kg * cfg["coeff"]["chestKg"]
        + h_delta * cfg["coeff"]["chestH"]
        + (body.get("chest") or 0)
        + upper_build
    )
    waist = (
        base["waist"]
        + adjusted_kg * cfg["coeff"]["waistKg"]
        + h_delta * cfg["coeff"]["waistH"]
        + (body.get("waist") or 0)
        + waist_build
    )

    hip = None
    if input_data["gender"] == "female":
        hip_build = cfg["build"].get("hip", {}).get(input_data.get("hipBuild"), 0) or 0
        hip = (
            base["hip"]
            + adjusted_kg * cfg["coeff"]["hipKg"]
            + h_delta * cfg["coeff"]["hipH"]
            + (body.get("hip") or 0)
            + hip_build
        )

    return {
        "chest": round1(chest),
        "waist": round1(waist),
        "hip": None if hip is None else round1(hip),
        "adjustedKg": round1(adjusted_kg),
    }


def estimated_score_recommendation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    estimate = estimate_body_measurements(input_data)
    table = SIZE_TABLE[input_data["gender"]]
    top_score = continuous_score(table["top"], "chest", estimate["chest"])

    if input_data["gender"] == "male":
        bottom_score = continuous_score(table["bottom"], "waist", estimate["waist"])
    else:
        waist_score = continuous_score(table["bottom"], "waist", estimate["waist"])
        hip_score = continuous_score(table["bottom"], "hip", estimate["hip"])
        bottom_score = waist_score * 0.35 + hip_score * 0.65

    return {"estimate": estimate, "topScore": top_score, "bottomScore": bottom_score}


def brand_reference_score(input_data: Dict[str, Any], group: str) -> Optional[Dict[str, Any]]:
    if not is_finite(input_data.get("height")) or not is_finite(input_data.get("weight")):
        return None

    candidates = []
    for ref in BRAND_REFERENCES:
        if ref["gender"] != input_data["gender"]:
            continue
        h_part = (input_data["height"] - ref["height"]) / 8
        w_part = (input_data["weight"] - ref["weight"]) / 10
        body_penalty = 0 if input_data.get("bodyType") == ref["bodyType"] else 0.75
        distance = math.sqrt(h_part * h_part + w_part * w_part + body_penalty * body_penalty)
        weight = 1 / math.pow(0.28 + distance, 2)
        candidate = dict(ref)
        candidate.update({"distance": distance, "weight": weight})
        candidates.append(candidate)

    candidates.sort(key=lambda item: item["distance"])
    if not candidates:
        return None

    nearest = candidates[0]
    top = candidates[:4]
    numerator = sum(ref["weight"] * (ref["topScore"] if group == "top" else ref["bottomScore"]) for ref in top)
    denominator = sum(ref["weight"] for ref in top)
    score = numerator / denominator

    strength = 0.0
    if nearest["distance"] < 0.05:
        strength = 0.86
    elif nearest["distance"] < 0.60:
        strength = 0.58
    elif nearest["distance"] < 1.10:
        strength = 0.38
    elif nearest["distance"] < 1.80:
        strength = 0.20

    return {
        "score": score,
        "strength": strength,
        "nearest": nearest["code"],
        "distance": nearest["distance"],
        "used": [ref["code"] for ref in top],
    }


def hybrid_score(input_data: Dict[str, Any], group: str, score_rec: Dict[str, Any], estimated: Dict[str, Any]) -> Dict[str, Any]:
    bmi_score = score_rec["upperScore"] if group == "top" else score_rec["lowerScore"]
    measure_score = estimated["topScore"] if group == "top" else estimated["bottomScore"]

    if input_data["gender"] == "male":
        raw = bmi_score * 0.55 + measure_score * 0.45 if group == "top" else bmi_score * 0.40 + measure_score * 0.60

        if (
            group == "top"
            and is_finite(input_data.get("height"))
            and input_data["height"] >= 183
            and is_finite(input_data.get("weight"))
            and input_data["weight"] >= 62
        ):
            raw = max(raw, 4.0)

        b = score_rec["base"]["bmi"]
        if group == "top" and is_finite(b) and b >= 34:
            raw += 0.35

        if (
            group == "bottom"
            and is_finite(input_data.get("weight"))
            and input_data["weight"] >= 100
            and input_data["weight"] < 115
            and input_data.get("waistBuild") == "medium"
        ):
            raw = min(raw, 5.45)

        if group == "bottom" and is_finite(b) and b < 25 and input_data.get("waistBuild") == "medium":
            raw = min(raw, 2.45)
    else:
        raw = bmi_score * 0.45 + measure_score * 0.55 if group == "top" else bmi_score * 0.25 + measure_score * 0.75
        if group == "bottom" and is_finite(score_rec["base"]["bmi"]) and score_rec["base"]["bmi"] >= 32:
            raw -= 0.15

    limited = clamp(raw, bmi_score - 1.85, bmi_score + 1.85)
    brand = brand_reference_score(input_data, group)
    branded = limited * (1 - brand["strength"]) + brand["score"] * brand["strength"] if brand else limited
    final = clamp(branded, bmi_score - 2.20, bmi_score + 2.20)

    return {
        "score": final,
        "raw": raw,
        "limited": limited,
        "brand": brand,
        "bmiScore": bmi_score,
        "measureScore": measure_score,
    }


def pick_by_score(gender: str, group: str, score: float) -> Dict[str, Any]:
    rows = SIZE_TABLE[gender][group]

    ranked = sorted(
        rows,
        key=lambda row: abs(float(row["fitScore"]) - score)
    )

    main = ranked[0]
    alternative = ranked[1] if len(ranked) > 1 else main

    return {
        "main": {"row": main},
        "alternative": {"row": alternative},
        "roundedScore": main["fitScore"]
    }

def hybrid_recommendation(input_data: Dict[str, Any], score_rec: Dict[str, Any]) -> Dict[str, Any]:
    estimated = estimated_score_recommendation(input_data)
    top_hybrid = hybrid_score(input_data, "top", score_rec, estimated)
    bottom_hybrid = hybrid_score(input_data, "bottom", score_rec, estimated)
    return {
        "estimated": estimated,
        "topHybrid": top_hybrid,
        "bottomHybrid": bottom_hybrid,
        "top": pick_by_score(input_data["gender"], "top", top_hybrid["score"]),
        "bottom": pick_by_score(input_data["gender"], "bottom", bottom_hybrid["score"]),
    }


def score_mode_recommendation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    bs = base_score(input_data)
    body = BODY_EFFECT.get(input_data["gender"], {}).get(input_data.get("bodyType"), {"upper": 0, "lower": 0})
    upper_build = WIDTH_EFFECT.get(input_data.get("upperBuild"), 0) or 0
    waist_build = WIDTH_EFFECT.get(input_data.get("waistBuild"), 0) or 0
    hip_build = WIDTH_EFFECT.get(input_data.get("hipBuild"), 0) or 0

    upper_raw = bs["base"] + upper_build * (0.65 if input_data["gender"] == "female" else 0.55) + body["upper"]
    if input_data["gender"] == "female":
        lower_raw = bs["base"] + hip_build * 0.75 + waist_build * 0.25 + body["lower"]
    else:
        lower_raw = bs["base"] + waist_build * 0.85 + body["lower"]

    upper_score = clamp(upper_raw, bs["base"] - 0.75, bs["base"] + 1.0)
    lower_score = clamp(lower_raw, bs["base"] - 0.75, bs["base"] + 1.0)

    return {
        "base": bs,
        "upperRaw": upper_raw,
        "lowerRaw": lower_raw,
        "upperScore": upper_score,
        "lowerScore": lower_score,
        "upper": pick_by_score(input_data["gender"], "top", upper_score),
        "bottom": pick_by_score(input_data["gender"], "bottom", lower_score),
    }


def final_recommendation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    score_rec = score_mode_recommendation(input_data)
    hybrid = hybrid_recommendation(input_data, score_rec)
    top_measured = measurement_top(input_data["gender"], input_data)
    bottom_measured = measurement_bottom(input_data["gender"], input_data)

    return {
        "score": score_rec,
        "hybrid": hybrid,
        "top": top_measured or hybrid["top"],
        "bottom": bottom_measured or hybrid["bottom"],
        "topMode": "measurement" if top_measured else "hybrid",
        "bottomMode": "measurement" if bottom_measured else "hybrid",
    }


def confidence(input_data: Dict[str, Any], rec: Dict[str, Any], group: str) -> str:
    if input_data["gender"] == "female":
        direct = len([v for v in [input_data.get("chest"), input_data.get("waist"), input_data.get("hip")] if is_finite(v)])
    else:
        direct = len([v for v in [input_data.get("chest"), input_data.get("waist")] if is_finite(v)])

    if direct >= 2:
        return "Yüksek"
    if direct == 1:
        return "Orta"

    brand = rec.get("hybrid", {}).get("topHybrid", {}).get("brand") if group == "top" else rec.get("hybrid", {}).get("bottomHybrid", {}).get("brand")
    if brand and brand["strength"] >= 0.55:
        return "Orta-yüksek"
    return "Orta"


def metric_text_for_row(row: Row, gender: str, group: str) -> str:
    if group == "top":
        return f"Tablo göğüs: {fmt_num(row['chest'])} cm" if row.get("chest") else ""
    if gender == "female":
        return f"Tablo bel: {fmt_num(row['waist'])} cm · basen: {fmt_num(row['hip'])} cm"
    return f"Tablo bel: {fmt_num(row['waist'])} cm"


def body_type_label(input_data: Dict[str, Any]) -> str:
    body_types = BODY_TYPES.get(input_data["gender"], [])
    match = next((item for item in body_types if item["key"] == input_data.get("bodyType")), None)
    return match["label"] if match else input_data.get("bodyType")


def make_input(
    gender: str = "female",
    height: Any = 166,
    weight: Any = 57,
    body_type: str = "rectangle",
    upper_build: str = "medium",
    waist_build: str = "medium",
    hip_build: str = "medium",
    chest: Any = None,
    waist: Any = None,
    hip: Any = None,
) -> Dict[str, Any]:
    """JS getInput() çıktısına denk gelen Python input sözlüğünü üretir."""
    if gender not in SIZE_TABLE:
        raise ValueError("gender 'female' veya 'male' olmalıdır.")

    return {
        "gender": gender,
        "height": parse_num(height),
        "weight": parse_num(weight),
        "bodyType": body_type,
        "upperBuild": upper_build,
        "waistBuild": waist_build,
        "hipBuild": hip_build,
        "chest": parse_num(chest),
        "waist": parse_num(waist),
        "hip": parse_num(hip),
    }


def alternative_advice(main_row: Row, alt_row: Row, confidence_text: str) -> str:
    """Orta/düşük güven seviyelerinde alternatifi yön bilgisiyle ifade eder."""
    main_score = main_row.get("fitScore")
    alt_score = alt_row.get("fitScore")
    low_or_medium_confidence = confidence_text not in {"Yüksek", "Orta-yüksek"}

    if low_or_medium_confidence and is_finite(main_score) and is_finite(alt_score):
        if float(alt_score) < float(main_score):
            return f"Alternatif olarak önerilen 1 küçük bedeni tercih edebilirsiniz: {alt_row['label']}"
        if float(alt_score) > float(main_score):
            return f"Alternatif olarak önerilen 1 büyük bedeni tercih edebilirsiniz: {alt_row['label']}"

    return f"Alternatif: {alt_row['label']}"


def calculate(
    gender: str = "female",
    height: Any = 166,
    weight: Any = 57,
    body_type: str = "rectangle",
    upper_build: str = "medium",
    waist_build: str = "medium",
    hip_build: str = "medium",
    chest: Any = None,
    waist: Any = None,
    hip: Any = None,
    include_debug: bool = True,
) -> Dict[str, Any]:
    """
    JavaScript calculate() fonksiyonunun DOM'suz Python karşılığı.

    Dönen ana alanlar:
      - topMain, topAlt, bottomMain, bottomAlt
      - topConfidence, bottomConfidence
      - topReason, bottomReason
      - input, lastResult
      - debug: score/hybrid ayrıntıları; include_debug=False ile kapatılabilir.
    """
    input_data = make_input(
        gender=gender,
        height=height,
        weight=weight,
        body_type=body_type,
        upper_build=upper_build,
        waist_build=waist_build,
        hip_build=hip_build,
        chest=chest,
        waist=waist,
        hip=hip,
    )

    rec = final_recommendation(input_data)
    top_conf = confidence(input_data, rec, "top")
    bottom_conf = confidence(input_data, rec, "bottom")

    top_row = rec["top"]["main"]["row"]
    top_alt = rec["top"]["alternative"]["row"]
    bottom_row = rec["bottom"]["main"]["row"]
    bottom_alt = rec["bottom"]["alternative"]["row"]

    last_result = {
        "input": deepcopy(input_data),
        "top": top_row["label"],
        "topAlt": top_alt["label"],
        "bottom": bottom_row["label"],
        "bottomAlt": bottom_alt["label"],
        "topMode": rec["topMode"],
        "bottomMode": rec["bottomMode"],
    }

    if rec["topMode"] == "measurement":
        top_reason = (
            f"Göğüs ölçünüz ({fmt_num(round1(input_data['chest']))} cm) tabloya doğrudan yakınlıkla eşleştirildi. "
            f"{metric_text_for_row(top_row, input_data['gender'], 'top')}."
        )
    else:
        hybrid = rec["hybrid"]["topHybrid"]
        estimate = rec["hybrid"]["estimated"]["estimate"]
        brand = hybrid.get("brand")
        brand_txt = f" Marka referansı: {brand['nearest']} ({js_round(brand['strength'] * 100)}% etki)." if brand and brand["strength"] > 0 else ""
        
    if rec["bottomMode"] == "measurement":
        if input_data["gender"] == "female":
            parts = []
            if is_finite(input_data.get("waist")):
                parts.append(f"bel {fmt_num(round1(input_data['waist']))} cm")
            if is_finite(input_data.get("hip")):
                parts.append(f"basen {fmt_num(round1(input_data['hip']))} cm")
            bottom_reason = (
                f"Alt beden {' ve '.join(parts)} ölçünüze göre tabloya doğrudan yakınlıkla eşleştirildi. "
                f"{metric_text_for_row(bottom_row, input_data['gender'], 'bottom')}."
            )
        else:
            bottom_reason = (
                f"Bel ölçünüz ({fmt_num(round1(input_data['waist']))} cm) erkek alt beden tablosuna doğrudan yakınlıkla eşleştirildi. "
                f"{metric_text_for_row(bottom_row, input_data['gender'], 'bottom')}."
            )
    else:
        hybrid = rec["hybrid"]["bottomHybrid"]
        estimate = rec["hybrid"]["estimated"]["estimate"]
        if input_data["gender"] == "female":
            target_txt = (
                f"tahmini bel/basen ({fmt_num(estimate['waist'])} / {fmt_num(estimate['hip'])} cm, "
                f"skor {fmt_num(round2(hybrid['measureScore']))})"
            )
        else:
            target_txt = f"tahmini bel ({fmt_num(estimate['waist'])} cm, skor {fmt_num(round2(hybrid['measureScore']))})"
        brand = hybrid.get("brand")
        brand_txt = f" Marka referansı: {brand['nearest']} ({js_round(brand['strength'] * 100)}% etki)." if brand and brand["strength"] > 0 else ""
        

    result = {
        "topMain": top_row["label"],
        "topAlt": alternative_advice(top_row, top_alt, top_conf),
        "bottomMain": bottom_row["label"],
        "bottomAlt": alternative_advice(bottom_row, bottom_alt, bottom_conf),
        "topConfidence": f"Güven: {top_conf}",
        "bottomConfidence": f"Güven: {bottom_conf}",
        "input": input_data,
        "lastResult": last_result,
    }
    if include_debug:
        result["debug"] = rec
    return result


def _json_default(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    raise TypeError(f"JSON'a çevrilemeyen değer: {value!r}")


def _parse_cli_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bedenimi Bul Python hesaplama motoru")
    parser.add_argument("--gender", choices=["female", "male"], default="female")
    parser.add_argument("--height", default="166")
    parser.add_argument("--weight", default="57")
    parser.add_argument("--body-type", default="rectangle")
    parser.add_argument("--upper-build", choices=["narrow", "medium", "wide"], default="medium")
    parser.add_argument("--waist-build", choices=["narrow", "medium", "wide"], default="medium")
    parser.add_argument("--hip-build", choices=["narrow", "medium", "wide"], default="medium")
    parser.add_argument("--chest", default=None)
    parser.add_argument("--waist", default=None)
    parser.add_argument("--hip", default=None)
    parser.add_argument("--no-debug", action="store_true", help="Ayrıntılı debug çıktısını kapatır")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = _parse_cli_args(argv)
    result = calculate(
        gender=args.gender,
        height=args.height,
        weight=args.weight,
        body_type=args.body_type,
        upper_build=args.upper_build,
        waist_build=args.waist_build,
        hip_build=args.hip_build,
        chest=args.chest,
        waist=args.waist,
        hip=args.hip,
        include_debug=not args.no_debug,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
