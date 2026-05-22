"""
Юніт-тести для модуля recommender.py
Запуск: pytest recommendation_service/tests/test_recommender.py -v
"""
import numpy as np
import pytest


def minmax(arr: np.ndarray) -> np.ndarray:
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else arr


def get_content_scores(user_interests: list, mongo_events: list) -> np.ndarray:
    interests = set(user_interests)
    scores = np.zeros(len(mongo_events))
    for i, event in enumerate(mongo_events):
        tags = set(event.get("tags", []))
        overlap = interests & tags
        union = interests | tags
        if union:
            scores[i] = len(overlap) / len(union)
    return scores


def filter_own_events(user_id: str, mongo_events: list) -> list:
    return [
        e for e in mongo_events
        if e.get("userId", {}).get("_id", "") != user_id
    ]


def fallback_by_popularity(mongo_events: list, top_n: int = 10) -> list:
    return sorted(
        mongo_events,
        key=lambda e: len(e.get("participants", [])),
        reverse=True
    )[:top_n]


# ══════════════════════════════════════════════════════════════
# Тест 1 — minmax: звичайний масив нормалізується до [0, 1]
# ══════════════════════════════════════════════════════════════
def test_minmax_normal_array():
    """Мінімум стає 0, максимум стає 1."""
    arr = np.array([1.0, 2.0, 3.0, 4.0])
    result = minmax(arr)
    assert result.min() == pytest.approx(0.0)
    assert result.max() == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════
# Тест 2 — minmax: масив з однакових значень не дає ділення на нуль
# ══════════════════════════════════════════════════════════════
def test_minmax_flat_array_no_division_by_zero():
    """Якщо всі елементи однакові (rng=0) — масив повертається без змін."""
    arr = np.array([0.5, 0.5, 0.5])
    result = minmax(arr)
    assert not np.any(np.isnan(result)), "Результат містить NaN"
    assert not np.any(np.isinf(result)), "Результат містить Inf"
    np.testing.assert_array_equal(result, arr)


# ══════════════════════════════════════════════════════════════
# Тест 3 — content scores: відсутність перетину → score = 0
# ══════════════════════════════════════════════════════════════
def test_content_scores_no_overlap_returns_zero():
    """Інтереси і теги події не перетинаються — Jaccard = 0."""
    events = [
        {"tags": ["МУЗИКА", "ВЕЧІР"]},
        {"tags": ["СПОРТ", "ОФЛАЙН"]},
    ]
    scores = get_content_scores(["IT", "ІГРИ"], events)
    assert scores[0] == 0.0
    assert scores[1] == 0.0


# ══════════════════════════════════════════════════════════════
# Тест 4 — content scores: повний збіг → Jaccard = 1.0
# ══════════════════════════════════════════════════════════════
def test_content_scores_full_overlap_returns_one():
    """Інтереси повністю збігаються з тегами — Jaccard = 1.0."""
    events = [{"tags": ["IT", "ОНЛАЙН"]}]
    scores = get_content_scores(["IT", "ОНЛАЙН"], events)
    assert scores[0] == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════
# Тест 5 — content scores: часткове перетинання → 0 < score < 1
# ══════════════════════════════════════════════════════════════
def test_content_scores_partial_overlap_between_zero_and_one():
    """Часткове перетинання — score між 0 і 1 (включно)."""
    events = [{"tags": ["IT", "МУЗИКА", "ОФЛАЙН"]}]
    scores = get_content_scores(["IT", "ІГРИ"], events)
    # overlap={IT}, union={IT, МУЗИКА, ОФЛАЙН, ІГРИ} → Jaccard = 1/4 = 0.25
    assert scores[0] == pytest.approx(0.25)
    assert 0.0 < scores[0] < 1.0


# ══════════════════════════════════════════════════════════════
# Тест 6 — content scores: порожній список подій → порожній масив
# ══════════════════════════════════════════════════════════════
def test_content_scores_empty_events_returns_empty():
    """Порожній список подій — повертається порожній масив scores."""
    scores = get_content_scores(["IT", "ІГРИ"], [])
    assert len(scores) == 0


# ══════════════════════════════════════════════════════════════
# Тест 7 — фільтрація: власні події не потрапляють у результат
# ══════════════════════════════════════════════════════════════
def test_filter_own_events_excludes_authors_events():
    """Події де userId._id == user_id виключаються з вибірки."""
    user_id = "abc123"
    events = [
        {"_id": "e1", "userId": {"_id": "abc123"}, "tags": ["IT"]},
        {"_id": "e2", "userId": {"_id": "xyz999"}, "tags": ["IT"]},
        {"_id": "e3", "userId": {"_id": "abc123"}, "tags": ["МУЗИКА"]},
    ]
    result = filter_own_events(user_id, events)
    ids = [e["_id"] for e in result]
    assert "e1" not in ids
    assert "e3" not in ids
    assert "e2" in ids
    assert len(result) == 1


# ══════════════════════════════════════════════════════════════
# Тест 8 — fallback: порожні інтереси → сортування за popularity
# ══════════════════════════════════════════════════════════════
def test_fallback_sorts_by_participants_count():
    """При порожніх інтересах — перша подія має найбільше учасників."""
    events = [
        {"_id": "e1", "participants": ["u1"], "tags": []},
        {"_id": "e2", "participants": ["u1", "u2", "u3"], "tags": []},
        {"_id": "e3", "participants": [], "tags": []},
    ]
    result = fallback_by_popularity(events, top_n=3)
    assert result[0]["_id"] == "e2"
    assert result[1]["_id"] == "e1"
    assert result[2]["_id"] == "e3"