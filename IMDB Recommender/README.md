# FEATURES
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/6937b376-10e2-4464-9891-7dd1814a5434)

## Movie/Series Recommendation From Your Watchlist
Your watchlist must be set public before importing. (See [Importing Your Watchlist](#importing-your-watchlist))

## Movie/Series Recommendation From Your Existing Lists
After importing, you can choose to get recommendations from any of your public user lists. (See [Importing Your Lists](#importing-your-lists))

## Movie/Series Recommendation From Custom IMDB List
The program can take a publicly available user link list as an input and randomly select a movie from that list. (See [Getting Recommendation From Custom User Lists](#getting-recommendation-from-custom-user-lists))

## Filtering
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/8728f674-72c2-4927-8f53-2aabb4bb0f2e)

You can filter the minimum IMDB rating, maximum runtime and desired genre so that the recommendations will be more relevant.

## Rating History Check
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/93fc0d1c-d105-4ae9-a7fc-d93e556c4c78)

The program checks if you have rated the recommended movie before and shows your rating score along with the date of rating.

The web scraping code snippet is in the code, however due to IMDB's robots.txt (https://www.imdb.com/robots.txt) this program cannot web scrape the user ratings page. Therefore you need to download and import the ratings.csv yourself. (See [Importing Your Ratings](#importing-your-ratings))

## Favorites
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d7b65c72-5027-4cc6-bd11-20d5519e0956)

You can favorite the recommended movie/series using the star icon at the upper left corner of the window, and can see your favorited titles from the "Settings" menu.

## Statistics
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/5c17f8b7-cc1f-4309-a9cf-8ab8d5966ae1)

Using your IMDB ratings (if you have imported your [ratings.csv](#importing-your-ratings) file), the program calculates which directors, genres or TV series are your favorites.

### Favorite Directors
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/dbe14d04-05c4-4263-85cd-72c2282296be)

Your favorite directors are calculated using how many of their movies you have rated, and your average rating for them. It is assumed that you tend to watch more movies from the directors you love more.

### Favorite Genres
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/153528fa-0604-44d0-afb8-f9c5f7e48815)

Your favorite genres are calculated using how many titles you have rated that belongs to that genre, and your average rating for them. It is assumed that you tend to watch more movies from the genres you love more.

### Favorite TV Series
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d921a818-bccb-4754-8b21-75bf0e46414f)

Your favorite TV Series are calculated using your rating for the series, your rating for the series' individual episodes, and how many episodes you have rated. It is assumed that you tend to rate more episode from the series you love more.

## Dark / Light Mode
![img_1](https://github.com/isonerinan/Python-Projects/assets/38159563/12624afc-1bea-4f47-a352-86b271dee044)

# HOW TO USE
## Downloads
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/3725a159-7791-4101-83a9-bfcec8e55ccd)

- Download [IMDB_Recommender_v3.1.zip](https://github.com/isonerinan/Python-Projects/releases/download/v3.1/IMDB_Recommender_v3.1.zip) and extract wherever you like.
- Download [star.svg](https://github.com/isonerinan/Python-Projects/blob/27cfd4181afd54c833545aa73f0aec42dcdd4c74/IMDB%20Recommender/star.svg)
- Make sure they are in the same directory.

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
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/ce4a477a-45e2-4a37-a863-52fd2ebf71cf)

If, for whatever reason, you decided to give a shot to someone else's taste in movies and found a user list (or maybe your friend shared their list with you?), you can just copy the link (example: https://www.imdb.com/list/ls521086952/) and paste it to the search bar at the bottom of the window and click the "Search" button.

You are now ready to use the program. Have a nice watch!

# Working On
- Bug fixes

# TODO
- Version control
- "Currently Watching" tab
- Gamification (Point System), maybe?
- Find out if I can bypass IMDB's robots.txt (probably not)
- Add support for other sites like Letterboxd, maybe?
