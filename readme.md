<a name="readme-top"></a>


<br />
<div align="center">
  <a href="https://github.com/Liftingthedata/xbox_de_project">
    <img src="images/xbox_logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Xbox Data Scraping Pipeline</h3>

  <p align="center">
    A data-driven project that uses Python, Airflow, GCP and K8s to gather & provide insights into Xbox data.
</div>

<div align="center" style="display: flex;">
    <a href="images/dashboard-1.png" style="flex: 1; margin-right: 5px;">
        <img src="images/dashboard-1.png" alt="Dashboard Screenshot 1" width="300" height="200">
    </a>
    <a href="images/dashboard-2.png" style="flex: 1; margin-left: 5px;">
        <img src="images/dashboard-2.png" alt="Dashboard Screenshot 2" width="300" height="200">
    </a>
</div>
<br>
<div align="center">
  <a href="https://lookerstudio.google.com/u/3/reporting/3b68c870-507f-4618-8454-fbae208bbc14/page/1M">
    View Dashboard Here
  </a>


</div>

<br>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#architecture">Architecture</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
  </ol>
</details>



## About The Project



<br>
The project aims to gather and analyze Xbox-specific data from multiple sources, including Metacritic, VGChartz, and Twitter. 
The collected data includes console and game sales, game ratings, user reviews, sentiment analysis for Xbox-related tweets, and more. 
The project utilizes scraping scripts written in Python. The pipline is orchestrated by Airflow, and the whole pipeline runs on Kubernetes (GKE) for efficient and scalable data processing.

## Architecture

<div align="center">
  <a>
    <img src="images/architecture.png" alt="architecture">
  </a>

</div>


The architecture of the project is designed to collect, process, and analyze data related to Xbox in a periodic fashion.

A simplified overview of the project's architecture can be summarized in the flow chart below.

```mermaid
flowchart LR

A[Data Scraping] --> B[Data Storage]
A --> C[Data Ingestion]
C --> D[Data Analysis]
D --> E[Insights & Metrics]
E --> F[(Decision Making)]
```

<!-- -   Data Sources:
    
    -   Metacritic: Provides game ratings and reviews.
    -   VGChartz: Offers Xbox console and game sales data.
    -   Twitter: Gathers Xbox-related tweets for sentiment analysis.
-   Scraping Scripts:
    
    -   Python scripts are developed to scrape data from Metacritic, VGChartz, and Twitter.
    -   Each script handles the specific scraping logic for its respective data source.
-   Data Extraction:
    
    -   The scraping scripts extract the relevant data from each source.
    -   Extracted data includes game ratings, reviews, sales figures, and tweets.
-   Data Storage:
    
    -   Extracted data is uploaded to Google Cloud Storage (GCS).
    -   GCS serves as a centralized storage location for the collected data.
-   Data Ingestion:
    
    -   The data from GCS is ingested into Google BigQuery.
    -   BigQuery is a scalable and fully-managed data warehouse that allows efficient querying and analysis of large datasets.
-   Data Analysis:
    
    -   The ingested data in BigQuery is analyzed using various techniques and algorithms.
    -   Sentiment analysis is performed on Twitter data to gauge user sentiment towards Xbox.
-   Dashboard and Insights:
    
    -   The analyzed data is used to generate metrics and statistics.
    -   A dashboard is created to present the insights obtained from the gathered data.
    -   The dashboard provides visualizations and key findings to aid decision-making. -->
    
<!-- Weighted_Performance = (Critic_Reviews_Count * 0.7 * Meta_Score + User_Rating_Count * 0.3 * User_Score) / (Critic_Reviews_Count + User_Rating_Count)

Here's an explanation of the equation:

Critic_Reviews_Count: This represents the total count of critic reviews for a game.
Meta_Score: It represents the average score given by the critics.
User_Rating_Count: This represents the total count of user reviews for a game.
User_Score: It represents the average score given by the users.
The equation assigns a weightage of 0.7 to the critic reviews and 0.3 to the user reviews. These weightage values can be adjusted based on the relative importance you want to give to each factor.

The formula calculates the weighted performance by multiplying the respective counts, scores, and weightages, and then dividing the weighted sum by the total count of reviews (critic and user) to obtain the average weighted performance.

This equation provides a way to combine the influence of both critics and users in evaluating the performance of a game, while also considering the review counts. Adjusting the weightage values allows you to emphasize the importance of one factor over the other, according to your preferences and project requirements. -->
## Getting Started



### Prerequisites


* [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)


### Installation


1. Clone the repository:
```sh
git clone https://github.com/Elsayed91/xbox_de_project.git
```
2. Install Pipenv
```sh
pip install pipenv
```
3. rename template.env to .env and fill out the values
4. run project setup script:
```sh
make setup
```


## How to improve

1. For starters, the game pass look up function is working properly for most part, but sometimes it just doesn't work.
for example take the game at this link https://www.metacritic.com/game/xbox-series-x/potion-craft-alchemist-simulator
this game is listed as potion-craft in the gamepass mastersheet. Okay, we can implement some sort of fuzzy matching, but this ends up putting us
at a position where similar titles can be mistaken, leading to more inaccurate data. 
At the moment there are 506 games in gamepass ultimate, however the table we create has  465.
2. This Project is mainly about Xbox as a console, however it doesn't have to be. Xbox PC could be baked in.

- Prices 


sentiment analysis per game
data analysis
nlp

