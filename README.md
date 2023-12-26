# Indie Game Recommender

## Overview
This is is basically what it says it is, a indie game recommender, a website that recommends indie games based on your recently played games. Just input a game you've played, and the recommender will suggest 5 indie games with similar genres.

#### Video Demo:  <URL HERE>

## Technologies Used
- **Back-end:** Python with Flask
- **Frontend:** HTML with Bootstrap
- **CSS:** Custom styles, but kept minimal
## Recommender algorithm
The project employs the **Jaccard Index** to compare game genres and provide recommendations 

## How it works

* User inputs a game, and the system queries the IGDB API.
* The games id is used to get and store its genres.
* A list of 300 games is cached in **games_list.json**  to make the process faster and make less calls to the API.
* The recommender compares inputted game genres to those of the 300 games using Jaccard similarity
* The top 5 similar games are selected, and their summary and cover url are displayed

## Features (Future implementations)

* A Sign-up page for saving user recommendations.
* Individual breakdown of each recommended game.
* Optimizing the recommendation system to use other parameters, but its currently limited by the amount of calls that can be done to the API.
* Make a option to select the platform of the recommend game.

## Sources

- [GeeksforGeeks: Measures of Distance in Data Mining](https://www.geeksforgeeks.org/measures-of-distance-in-data-mining/)
- [W3Schools: AI Learning](https://www.w3schools.com/ai/ai_learning.asp)
- [LearnDataSci: Jaccard Similarity](https://www.learndatasci.com/glossary/jaccard-similarity/)


#### Special thanks to the devs at  [IGDB](https://www.igdb.com/) for making the data so accessible


## Challenges in Project Development

The project was full of riddles for me to solve. From selecting a API to get the games from, to being able to code a recommender without previous knowledge on how to build any algorithm or data mining.

- **API Selection** there was a couple of options to choose from. After lots of research the IGDB  thanks to their well documented nature and their active developer community supporting it.

- **Algorithm** Creating the recommender was the one that took the most time to research, because of my lack of experience in building algorithms or the know hows of data mining. With the objective in mind of looking for a mehtod to compare sets of items within the inputted game against those of other games

- **Genre-based comparison** I ended up deciding to use genres to compare the games. It made most sense after considering maybe using the themes of the games.

- **Ways to compare the information** My search came down to two options for comparing the information: the Cosine Index and the Jaccard Index. Finally decided on the Jaccard index because of its simplicity in comparing data sets.
