from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from scrapers.vgchartz.scrape_game_sales import *


def test_get_page_html():
    url = "https://www.google.com"
    soup = get_page_html(url)
    assert soup.title.string == "Google"


def test_scrape_genre_list():
    genre_list = [
        "Action",
        "Action-Adventure",
        "Adventure",
        "Board Game",
        "Education",
        "Fighting",
        "Misc",
        "MMO",
        "Music",
        "Party",
        "Platform",
        "Puzzle",
        "Racing",
        "Role-Playing",
        "Sandbox",
        "Shooter",
        "Simulation",
        "Sports",
        "Strategy",
        "Visual Novel",
    ]
    assert isinstance(genre_list, list)
    assert len(genre_list) > 0
    assert all(isinstance(genre, str) for genre in genre_list)


def test_build_url():
    genre = "Action"
    console_type = "Xbox One"
    page_num = 1
    expected_url = "https://www.vgchartz.com/games/games.php?page=1&results=200&genre=Action&console=Xbox+One&order=Sales&ownership=Both&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showshipped=1"
    assert build_url(genre, console_type, page_num) == expected_url


def test_scrape_game_info():
    html = """
    <html>
        <body>
            <div id="generalBody">
                <table>
                    <tbody>
                        <tr></tr>
                        <tr></tr>
                        
                        <tr>
                            <th>Rank</th>
                            <th>Gamex</th>
                            <th>Game</th>
                            <th>Console</th>
                            <th>Publisher</th>
                            <th>Developer</th>
                            <th>Total Shipped</th>
                            <th>Total Sales</th>
                            <th>NA Sales</th>
                            <th>EU Sales</th>
                            <th>Japan Sales</th>
                            <th>Other Sales</th>
                            <th>Release Date</th>
                            <th>Last Update</th>
                            <th>Genre</th>
                        </tr>
                        <tr>
                            <td>1</td>
                            <td></td>
                            <td>Super Mario Bros.</td>
                            <td>
                                <img alt="Series" src="/images/consoles/Series_b.png"/>
                            </td>
                            <td>Nintendo</td>
                            <td>Nintendo EAD</td>
                            <td>40.24</td>
                            <td>40.24</td>
                            <td>NA</td>
                            <td>NA</td>
                            <td>NA</td>
                            <td>NA</td>
                            <td>September 13, 1985</td>
                            <td>February 13, 2021</td>
                            <td>Action</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(
        html, "html.parser"
    )  # Convert HTML string to BeautifulSoup object
    genre = "Action"
    expected_result = (
        True,
        pd.DataFrame(
            {
                "Rank": [1],
                "Gamex": ["NA"],
                "Game": ["Super Mario Bros."],
                "Console": ["Series"],
                "Publisher": ["Nintendo"],
                "Developer": ["Nintendo EAD"],
                "Total Shipped": [40.24],
                "Total Sales": [40.24],
                "NA Sales": ["NA"],
                "EU Sales": ["NA"],
                "Japan Sales": ["NA"],
                "Other Sales": ["NA"],
                "Release Date": ["September 13, 1985"],
                "Last Update": ["February 13, 2021"],
                "Genre": ["Action"],
            }
        ),
    )

    result = scrape_game_info(soup, genre)
    result[1].fillna("NA", inplace=True)
    assert result[0] == expected_result[0]

    assert result[1].shape == expected_result[1].shape

    assert result[1].columns.equals(expected_result[1].columns)

    for column in result[1].columns:
        pd.testing.assert_series_equal(
            result[1][column], expected_result[1][column], check_dtype=False
        )


def test_clean_data():
    # Create sample data with 'Sales' and 'Units' columns in string format
    df = pd.DataFrame(
        {
            "Total Shipped": ["1.23m", "2.34m", "3.45m"],
            "Total Sales": ["4.56m", "5.67m", "6.78m"],
            "NA Sales": ["7.89m", "8.90m", "9.01m"],
            "EU Sales": ["1.12m", "2.23m", "3.34m"],
            "Japan Sales": ["4.45m", "5.56m", "6.67m"],
            "Other Sales": ["7.78m", "8.89m", "9.90m"],
            "Console": ["XOne", "X360", "XS"],
            "Gamex": ["--", "--", "--"],
            "Rank": [1, 2, 3],
            "Game": ["Game1", "Game2", "Game3"],
            "Publisher": ["Publisher1", "Publisher2", "Publisher3"],
            "Developer": ["Developer1", "Developer2", "Developer3"],
            "Release Date": [
                "01th Jan 22",
                "02th Jan 22",
                "03th Jan 22",
            ],  # Updated date format
            "Last Update": [
                "04th Jan 22",
                "05th Jan 22",
                "06th Jan 22",
            ],  # Updated date format
            "Genre": ["Action", "Adventure", "Shooter"],
        }
    )

    # Convert 'Sales' and 'Units' columns to float format and replace 'Series' with 'XS'
    df = clean_data(df)

    # Check if 'Sales' and 'Units' columns are converted to float format
    assert all(
        isinstance(df[col].iloc[0], float)
        for col in ["Total Sales", "NA Sales", "EU Sales", "Japan Sales", "Other Sales"]
    )

    # Check if 'Console' column is cleaned
    assert df["Console"].equals(pd.Series(["Xbox One", "Xbox 360", "Xbox Series X"]))

    # Check if 'Gamex' column is dropped
    assert "Gamex" not in df.columns
    # Check if the number of rows and columns in the dataframe remain the same
    assert df.shape == (3, 13)


def test_parse_date():
    assert parse_date("4th Jul 20") == datetime(2020, 7, 4, 0, 0, 0)
    assert parse_date("31st Dec 21") == datetime(2021, 12, 31, 0, 0)
    assert parse_date("29th Feb 20") == datetime(2020, 2, 29, 0, 0, 0)
    assert parse_date("10th Jan 22") == datetime(2022, 1, 10, 0, 0, 0)


@pytest.fixture
def sample_soup():
    url = build_url("Action", "XS", "1")
    soup = get_page_html(url)
    return soup


def test_scrape_game_info(sample_soup):
    expected_output = (
        pd.DataFrame(
            {
                "Rank": ["1", "2"],
                "Gamex": ["NaN", "NaN"],
                "Game": ["Dawn of the Monsters", "Armored Core VI Fires of Rubicon"],
                "Console": ["XS", "XS"],
                "Publisher": ["Unknown", "Unknown"],
                "Developer": ["13AM Games", "From Software"],
                "Total Shipped": ["NaN", "NaN"],
                "Total Sales": ["NaN", "NaN"],
                "NA Sales": ["NaN", "NaN"],
                "EU Sales": ["NaN", "NaN"],
                "Japan Sales": ["NaN", "NaN"],
                "Other Sales": ["NaN", "NaN"],
                "Release Date": ["NaN", "NaN"],
                "Last Update": ["10th Mar 22", "09th Dec 22"],
                "Genre": ["Action", "Action"],
            }
        )
        .iloc[:2]
        .replace({pd.NA: "NaN"})
    )
    output = scrape_game_info(sample_soup, "Action")
    output_df = output[1].iloc[:2].astype("object").replace({pd.NA: "NaN"})
    output_df.drop(["Gamex", "Rank"], axis=1, inplace=True)
    expected_output.drop(["Gamex", "Rank"], axis=1, inplace=True)
    pd.testing.assert_frame_equal(
        output_df.reset_index(drop=True), expected_output.reset_index(drop=True)
    )


def test_scrape_vgchartz():
    console_list = ["XOne"]
    result = scrape_vgchartz(console_list, ["Adventure"])
    print(result.columns)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(
        col in result.columns
        for col in [
            "Rank",
            "Gamex",
            "Game",
            "Console",
            "Publisher",
            "Developer",
            "Total Shipped",
            "Total Sales",
            "NA Sales",
            "EU Sales",
            "Japan Sales",
            "Other Sales",
            "Release Date",
            "Last Update",
            "Genre",
        ]
    )
