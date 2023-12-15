![Watchable-Cover](https://github.com/isonerinan/Python-Projects/assets/38159563/a18af7df-49ea-4761-9fef-b21a3a47e58a)
# FEATURES
If you want to learn how to use, [check here!](#how-to-use)
## Movie/Series Recommendation From Your Watchlist
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/925da13e-c58c-42ce-84d9-01a95868e321)

Your watchlist must be set public before importing. (See [Importing Your Watchlist](#importing-your-watchlist))

## Movie/Series Recommendation From Your Existing Lists
After importing, you can choose to get recommendations from any of your public user lists. (See [Importing Your Lists](#importing-your-lists))

## Movie/Series Recommendation From Custom IMDB List
The program can take a publicly available user link list as an input and randomly select a movie from that list. (See [Getting Recommendation From Custom User Lists](#getting-recommendation-from-custom-user-lists))

## Filtering
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/58f62f88-8dd6-43c3-aa6c-853bd7feef3a)

You can filter the minimum IMDB rating, maximum runtime and desired genre so that the recommendations will be more relevant.

## Rating History Check
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/39b3b9d4-311c-4b19-8a45-22b6ff6f51df)

The program checks if you have rated the recommended movie before and shows your rating score along with the date of rating.

The web scraping code snippet is in the code, however due to IMDB's robots.txt (https://www.imdb.com/robots.txt) this program cannot web scrape the user ratings page. Therefore you need to download and import the ratings.csv yourself. (See [Importing Your Ratings](#importing-your-ratings))

## Favorites
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/14c086db-b723-4aca-ba37-b5c22f794119)

You can favorite the recommended movie/series using the star icon at the upper left corner of the window, and can see your favorited titles from the "Settings" menu.

## Statistics
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/f25f2b37-3687-4d0c-8979-ce51ae63b078)

Using your IMDB ratings (if you have imported your [ratings.csv](#importing-your-ratings) file), the program calculates which directors, genres or TV series are your favorites.

### Favorite Directors
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/682bc094-f38a-4848-9ac0-46f2d51599c8)

Your favorite directors are calculated using how many of their movies you have rated, and your average rating for them. It is assumed that you tend to watch more movies from the directors you love more.

### Favorite Actors/Actresses
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d3b14b76-53a6-4307-8584-346ab4e17881)

Your favorite actors/actresses are calculated using how many of their movies/shows you have rated, and your average rating for them. It is assumed that you tend to watch more movies/shows from the actors you love more.

### Favorite TV Series
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/b9e48d55-2248-4322-a051-dc37e60a857e)

Your favorite TV Series are calculated using your rating for the series, your rating for the series' individual episodes, and how many episodes you have rated. It is assumed that you tend to rate more episode from the series you love more.

### Favorite Genres
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/55b936f1-317d-4440-978b-ce3078fadec5)

Your favorite genres are calculated using how many titles you have rated that belongs to that genre, and your average rating for them. It is assumed that you tend to watch more movies from the genres you love more.

### Favorite Years
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/f50e96b7-daed-402f-b271-b03cf4942253)
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/ac02a94e-f1ad-4a74-8352-b07d81c9724a)

Your favorite years are calculated using how many movies/shows you have rated from that year, and your average rating for them. The discussions for the golden year of cinema is over (for you).

### Watchlist Statistics
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/1fe5fc7c-aabc-48c0-84c8-c1c72f1502d4)

You are what you watch! And your watchlist is the future you. Meet your future self.

## Dark / Light Mode
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/e3e0e1df-5f99-4dd2-bcbb-cdafb8d4fb9d)

## Now Watching
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d8ed442f-1b02-4463-ba46-d0fa04789d87)

If you want to keep track of the shows you are currently watching, we've got you covered.

# HOW TO USE
## Downloads
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/faa63971-96c4-4b87-b4bb-c4d346d37c57)

- Go to [Releases](https://github.com/isonerinan/Python-Projects/releases) and download the version you desire by clicking the ZIP file (always the last version is recommended)
- Unzip the contents wherever you like
- Clicking the "IMDB_Recommender.exe" file should work without any problems

## Imports
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/94601f23-37f9-4dab-ad4f-01eec4a624d7)

### Importing Your Watchlist
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d4a0a6e7-4699-4224-9bd1-53f71c6b2843)

- Go to your IMDB Watchlist page
- Find the export link at the bottom of the page
- Right click and copy the link
- Paste it in the User Preferences window of the program
- The link should look like this: https://www.imdb.com/list/lsxxxxxxxxx/export

### Importing Your Lists
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/bf5ede4b-c663-4c02-9b19-dcacde26e414)

- Find the dropdown menu at the top right corner
- Go to "Your Lists" page and copy the URL
- Paste it in the User Preferences window of the program
- The link should look like this: https://www.imdb.com/user/urxxxxxxxxx/lists

### Importing Your Ratings
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/eeef4e39-df0e-4225-9ec3-a352d8f7ab00)

- Go to "Your Ratings" page
- Find the export button in the screenshot
- Download "ratings.csv"
- In the User Preferences window, click "Select File" button and locate "ratings.csv"
- Repeat this process whenever you would like to update your ratings history

### Getting Recommendation From Custom User Lists
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/1413cb87-75c7-4fa7-b815-6022df890fc5)

If, for whatever reason, you decided to give a shot to someone else's taste in movies and found a user list (or maybe your friend shared their list with you?), you can just copy the link (example: https://www.imdb.com/list/ls521086952/) and paste it to the search bar at the bottom of the window and click the "Search" button.

You are now ready to use the program. Have a nice watch!

# Working On
- Bug fixes

# TODO
- Adding notes on recommendations/favorites
- Version control
- Gamification (Point System), maybe?
- Find out if I can bypass IMDB's robots.txt (probably not)
- Add support for other sites like Letterboxd, maybe?
