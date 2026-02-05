from collections import defaultdict
from csv import DictReader
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


# TODO: Polish and document tests - code quality is lacking.
# TODO: Address pytest warnings.

client = TestClient(app)
INIT_DATA_PATH = Path(__file__).parent.parent / 'app' / 'database' / 'init_data' / 'sailing_level_raw.csv'

def test_valid_range_returns_200():
    response = client.get('/capacity', params={'date_from': '2024-01-01', 'date_to': '2024-03-31'})
    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    for row in body:
        assert 'week_start_date' in row
        assert 'week_no' in row
        assert 'offered_capacity_teu' in row
    dates = [row['week_start_date'] for row in body]
    assert dates == sorted(dates)

def test_missing_params_returns_422():
    assert client.get('/capacity').status_code == 422
    assert client.get('/capacity', params={'date_from': '2024-01-01'}).status_code == 422
    assert client.get('/capacity', params={'date_to': '2024-03-31'}).status_code == 422

def test_empty_range_returns_empty():
    response = client.get('/capacity', params={'date_from': '2020-01-01', 'date_to': '2020-03-31'})
    assert response.status_code == 200
    assert response.json() == []

def test_single_week_range():
    response = client.get('/capacity', params={'date_from': '2024-02-12', 'date_to': '2024-02-18'})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1

def _compute_expected_from_csv(date_from: date, date_to: date):
    """Replicate the SQL capacity query logic in pure Python with the CSV."""

    voyage_key_to_latest = {}

    # Parse CSV and deduplicate:
    with open(INIT_DATA_PATH, mode='r', encoding='utf-8') as f:
        for row in DictReader(f):
            if row['ORIGIN'] != 'china_main' or row['DESTINATION'] != 'north_europe_main':
                continue
            key = (
                row['SERVICE_VERSION_AND_ROUNDTRIP_IDENTFIERS'],
                row['ORIGIN_SERVICE_VERSION_AND_MASTER'],
                row['DESTINATION_SERVICE_VERSION_AND_MASTER']
            )
            origin_at_utc = datetime.fromisoformat(row['ORIGIN_AT_UTC'])
            offered_capacity_teu = int(row['OFFERED_CAPACITY_TEU'])
            if key not in voyage_key_to_latest or origin_at_utc > voyage_key_to_latest[key][0]:
                voyage_key_to_latest[key] = (origin_at_utc, offered_capacity_teu)

    # Assign to weeks and sum:
    weekly_sums = defaultdict(int)
    for origin_at_utc, offered_capacity_teu in voyage_key_to_latest.values():
        origin_date = origin_at_utc.date()
        monday_date = origin_date - timedelta(days=origin_date.weekday())
        weekly_sums[monday_date] += offered_capacity_teu

    # Filter to date range:
    filtered_weeks = sorted(
        monday_date
        for monday_date in weekly_sums
        if date_from <= monday_date <= date_to
    )

    # Compute rolling average over filtered weeks:
    results = {}
    for i, week in enumerate(filtered_weeks):
        window_start = max(0, i - 3)
        window_capacities = [weekly_sums[filtered_weeks[j]] for j in range(window_start, i + 1)]
        average_offered_capacity_teu = int(sum(window_capacities) / len(window_capacities))
        week_no = i + 1
        results[week] = [week_no, average_offered_capacity_teu]

    return results

def test_spot_check_rolling_average():
    """Compare API results against an independent Python calculation from the CSV."""

    expected = _compute_expected_from_csv(date(2024, 1, 1), date(2024, 3, 31))

    response = client.get('/capacity', params={'date_from': '2024-01-01', 'date_to': '2024-03-31'})
    assert response.status_code == 200
    body = response.json()

    assert len(body) == len(expected)
    for row in body:
        week_date = date.fromisoformat(row['week_start_date'])
        assert week_date in expected, f'Unexpected week {week_date} in API response'
        exepected_week_no, expected_offered_capacity_teu = expected[week_date]
        assert row['week_no'] == exepected_week_no, (
            f'Mismatch for week {week_date}: '
            f'API={row['week_no']}, expected={exepected_week_no}'
        )
        assert row['offered_capacity_teu'] == expected_offered_capacity_teu, (
            f'Mismatch for week {week_date}: '
            f'API={row['offered_capacity_teu']}, expected={expected_offered_capacity_teu}'
        )
