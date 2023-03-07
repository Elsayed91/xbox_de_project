from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from scrapers.vgchartz.scrape_game_sales import *

# def test_get_page_html():
#     url = "https://www.google.com"
#     soup = get_page_html(url)
#     assert soup.title.string == "Google"
    
# def test_scrape_genre_list():
#     genre_list = ['Action', 'Action-Adventure', 'Adventure', 'Board Game', 'Education', 
#                 'Fighting', 'Misc', 'MMO', 'Music', 'Party', 'Platform', 'Puzzle',
#                 'Racing', 'Role-Playing', 'Sandbox', 'Shooter', 'Simulation', 'Sports',
#                 'Strategy', 'Visual Novel']
#     assert isinstance(genre_list, list)
#     assert len(genre_list) > 0
#     assert all(isinstance(genre, str) for genre in genre_list)
    
    
# def test_build_url():
#     genre = "Action"
#     console_type = "Xbox One"
#     page_num = 1
#     expected_url = "https://www.vgchartz.com/games/games.php?page=1&results=200&genre=Action&console=Xbox+One&order=Sales&ownership=Both&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showshipped=1"
#     assert build_url(genre, console_type, page_num) == expected_url
    
# def test_scrape_game_info():
#     html = """
#     <html>
#         <body>
#             <div id="generalBody">
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Rank</th>
#                             <th>Gamex</th>
#                             <th>Game</th>
#                             <th>Console</th>
#                             <th>Publisher</th>
#                             <th>Developer</th>
#                             <th>Total Shipped</th>
#                             <th>Total Sales</th>
#                             <th>NA Sales</th>
#                             <th>EU Sales</th>
#                             <th>Japan Sales</th>
#                             <th>Other Sales</th>
#                             <th>Release Date</th>
#                             <th>Last Update</th>
#                             <th>Genre</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr>
#                             <td>1</td>
#                             <td></td>
#                             <td>Super Mario Bros.</td>
#                             <td>
#                                 <img src="console.png" alt="NES" />
#                             </td>
#                             <td>Nintendo</td>
#                             <td>Nintendo EAD</td>
#                             <td>40.24</td>
#                             <td>40.24</td>
#                             <td>NA</td>
#                             <td>NA</td>
#                             <td>NA</td>
#                             <td>NA</td>
#                             <td>September 13, 1985</td>
#                             <td>February 13, 2021</td>
#                             <td>Action</td>
#                         </tr>
#                     </tbody>
#                 </table>
#             </div>
#         </body>
#     </html>
#     """
#     soup = BeautifulSoup(html, 'html.parser')
#     genre = 'Action'
#     expected_result = (
#         True,
#         pd.DataFrame({
#             'Rank': [1],
#             'Gamex': [''],
#             'Game': ['Super Mario Bros.'],
#             'Console': ['NES'],
#             'Publisher': ['Nintendo'],
#             'Developer': ['Nintendo EAD'],
#             'Total Shipped': [40.24],
#             'Total Sales': [40.24],
#             'NA Sales': ['NA'],
#             'EU Sales': ['NA'],
#             'Japan Sales': ['NA'],
#             'Other Sales': ['NA'],
#             'Release Date': ['September 13, 1985'],
#             'Last Update': ['February 13, 2021'],
#             'Genre': ['Action']
#         })
#     )

#     result = scrape_game_info(soup, genre)

#     assert result == expected_result


# def test_clean_data():
#     # Create sample data with 'Sales' and 'Units' columns in string format
#     df = pd.DataFrame({
#         'Total Shipped': ['1.23m', '2.34m', '3.45m'],
#         'Total Sales': ['4.56m', '5.67m', '6.78m'],
#         'NA Sales': ['7.89m', '8.90m', '9.01m'],
#         'EU Sales': ['1.12m', '2.23m', '3.34m'],
#         'Japan Sales': ['4.45m', '5.56m', '6.67m'],
#         'Other Sales': ['7.78m', '8.89m', '9.90m'],
#         'Console': ['XOne', 'X360', 'XS'],
#         'Gamex': ['--', '--', '--'],
#         'Rank': [1, 2, 3],
#         'Game': ['Game1', 'Game2', 'Game3'],
#         'Publisher': ['Publisher1', 'Publisher2', 'Publisher3'],
#         'Developer': ['Developer1', 'Developer2', 'Developer3'],
#         'Release Date': ['2022-01-01', '2022-01-02', '2022-01-03'],
#         'Last Update': ['2022-01-04', '2022-01-05', '2022-01-06'],
#         'Genre': ['Action', 'Adventure', 'Shooter']
#     })

#     # Convert 'Sales' and 'Units' columns to float format and replace 'Series' with 'XS'
#     df = clean_data(df)

#     # Check if 'Sales' and 'Units' columns are converted to float format
#     assert all(isinstance(df[col].iloc[0], float) for col in ['Total Sales', 'NA Sales', 'EU Sales', 'Japan Sales', 'Other Sales'])

#     # Check if 'Console' column is cleaned
#     assert df['Console'].equals(pd.Series(['XOne', 'X360', 'XS']))

#     # Check if 'Gamex' column is dropped
#     assert 'Gamex' not in df.columns

#     # Check if the number of rows and columns in the dataframe remain the same
#     assert df.shape == (3, 14)

# @pytest.fixture
# def sample_soup():
#     url = build_url('Action', 'XS', '1')
#     soup = get_page_html(url)
#     return soup

# def test_scrape_game_info(sample_soup):
#     expected_output = pd.DataFrame({
#         'Rank': ["1", "2"],
#         'Gamex': ['NaN','NaN'],
#         'Game': ['Dawn of the Monsters', 'Armored Core VI Fires of Rubicon'],
#         'Console': ['XS', 'XS'],
#         'Publisher': ['Unknown', 'Unknown'],
#         'Developer': ['13AM Games', 'From Software'],
#         'Total Shipped': ['NaN','NaN'],
#         'Total Sales': ['NaN','NaN'],
#         'NA Sales': ['NaN','NaN'],
#         'EU Sales': ['NaN','NaN'],
#         'Japan Sales': ['NaN','NaN'],
#         'Other Sales': ['NaN','NaN'],
#         'Release Date': ['NaN','NaN'],
#         'Last Update': ['10th Mar 22', '09th Dec 22'],
#         'Genre': ['Action', 'Action']
#     }).iloc[:2].replace({pd.NA: 'NaN'})
#     output = scrape_game_info(sample_soup, 'Action')
#     output_df = output[1].iloc[:2].astype('object').replace({pd.NA: 'NaN'})
#     output_df.drop(['Gamex', 'Rank'], axis=1, inplace=True)
#     expected_output.drop(['Gamex', 'Rank'], axis=1, inplace=True)
#     print(output_df)
#     print(expected_output)
#     pd.testing.assert_frame_equal(output_df.reset_index(drop=True), expected_output.reset_index(drop=True))



def test_scrape_vgchartz():
    console_list = ['XOne']
    result = scrape_vgchartz(console_list,['Adventure'])
    print(result.columns)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(col in result.columns for col in ['Rank', 'Gamex', 'Game', 'Console', 'Publisher', 'Developer',
       'Total Shipped', 'Total Sales', 'NA Sales', 'EU Sales', 'Japan Sales',
       'Other Sales', 'Release Date', 'Last Update', 'Genre'])
