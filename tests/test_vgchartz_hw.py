from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd
import pytest
from pandas.api.types import is_dict_like
from pandas.testing import assert_frame_equal

from scrapers.vgchartz.scrape_hardware_sales import *


@pytest.fixture
def sample_url():
    return "https://www.vgchartz.com/tools/hw_date.php?reg=Global&ending=Weekly"


def test_get_sales_data_returns_dict(sample_url):
    data = get_sales_data(sample_url)
    assert is_dict_like(data)


def test_get_sales_data_contains_series_data(sample_url):
    data = get_sales_data(sample_url)
    assert "series" in data
    assert len(data["series"]) > 0


def test_get_sales_data_series_data_has_name_and_data_keys(sample_url):
    data = get_sales_data(sample_url)
    series_data = data["series"]
    for series in series_data:
        assert "name" in series
        assert "data" in series


def test_get_sales_dataframe():
    # Create sample input data
    data = {
        "series": [
            {
                "name": "PS5",
                "data": [
                    {"x": 1662163200000, "y": 66303},
                    {"x": 1662768000000, "y": 70385},
                    {"x": 1663372800000, "y": 63778},
                ],
            },
            {
                "name": "Xbox Series X",
                "data": [
                    {"x": 1662163200000, "y": 48800},
                    {"x": 1662768000000, "y": 50632},
                ],
            },
        ]
    }

    # Convert Unix timestamps to dates
    dates = [
        pd.to_datetime(point["x"], unit="ms")
        for series in data["series"]
        for point in series["data"]
    ]

    # Expected output data
    expected_output = pd.DataFrame(
        {
            "console": ["PS5", "PS5", "PS5", "Xbox Series X", "Xbox Series X"],
            "date": dates,
            "sales": [66303, 70385, 63778, 48800, 50632],
        }
    )

    expected_output["sales"] = expected_output["sales"]

    output = get_sales_dataframe(data)
    output["sales"] = output["sales"].astype(int)
    assert_frame_equal(output, expected_output)


def test_calculate_other_sales():
    # Sample input data
    data = pd.DataFrame(
        {
            "console": ["X360", "X360", "X360", "X360", "X360", "X360", "X360", "X360"],
            "date": [
                "2005-11-26",
                "2005-11-26",
                "2005-11-26",
                "2005-11-26",
                "2005-12-24",
                "2005-12-24",
                "2005-12-24",
                "2005-12-24",
            ],
            "sales": [5, 5, 2, 16, 6, 4, 3, 15],
            "region": [
                "USA",
                "Europe",
                "Japan",
                "Global",
                "USA",
                "Europe",
                "Japan",
                "Global",
            ],
        }
    )

    # Expected output data
    expected_output = pd.DataFrame(
        {
            "console": [
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
                "X360",
            ],
            "date": [
                "2005-11-26",
                "2005-12-24",
                "2005-11-26",
                "2005-12-24",
                "2005-11-26",
                "2005-12-24",
                "2005-11-26",
                "2005-12-24",
                "2005-11-26",
                "2005-12-24",
            ],
            "region": [
                "Europe",
                "Europe",
                "Global",
                "Global",
                "Japan",
                "Japan",
                "USA",
                "USA",
                "Others",
                "Others",
            ],
            "sales": [5, 4, 16, 15, 2, 3, 5, 6, 4, 2],
        }
    )

    # Convert dates to datetime format
    data["date"] = pd.to_datetime(data["date"])
    expected_output["date"] = pd.to_datetime(expected_output["date"])
    print(expected_output)

    # Test the function
    output = calculate_other_sales(data)
    print(output)
    assert_frame_equal(output, expected_output)


def test_main_integration():
    consoles = ["PS5", "PS4"]
    regions = ["USA", "Europe", "Japan", "Global"]
    start_date = "2022-08-16"
    df = main(regions, consoles, start_date=start_date)
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"console", "date", "sales", "region"}
    assert not df.empty

    df.to_csv("test_hw_sales.csv", index=False)
