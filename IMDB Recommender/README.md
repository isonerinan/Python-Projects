# FEATURES
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/6937b376-10e2-4464-9891-7dd1814a5434)

## Movie/Series Recommendation From User's Watchlist
The watchlist must be public and replaced with the existing link. (example: https://www.imdb.com/user/USER_NAME_HERE/watchlist)

## Movie/Series Recommendation From User's Existing Lists
All the publicly available user lists are shown. In order to personalize, the default link must be replaced. (example: https://www.imdb.com/user/USER_NAME_HERE/lists)

## Movie/Series Recommendation From Custom IMDB List
The program can take a publicly available user link list as an input and randomly select a movie from that list.

## Rating History Check
The program checks if the user have rated the recommended movie before and shows the rating score, and the date of rating. The web scraping code snippet is in the code, however due to IMDB's robots.txt (https://www.imdb.com/robots.txt) this program cannot web scrape the user ratings page. Therefore you need to download the ratings.csv yourself (See [Importing Your Ratings](#importing-your-ratings) for more).

## Favorite
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/501363e0-ba8e-4e4b-a5af-80427eed41d5)

The user can favorite the recommended movie/series using the star icon at the upper left corner of the window, and can see their favorited titles from the "Settings" menu.

# HOW TO USE
## Downloads
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/3725a159-7791-4101-83a9-bfcec8e55ccd)

- Download [IMDB Recommender.py](https://github.com/isonerinan/Python-Projects/blob/27cfd4181afd54c833545aa73f0aec42dcdd4c74/IMDB%20Recommender/IMDB%20Recommender.py)
- Download [star.svg](https://github.com/isonerinan/Python-Projects/blob/27cfd4181afd54c833545aa73f0aec42dcdd4c74/IMDB%20Recommender/star.svg)

Make sure they are in the same directory, if not, you have to change the directory in the code accordingly. 

## CSV Files
### Importing Your Watchlist
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d4a0a6e7-4699-4224-9bd1-53f71c6b2843)

- Go to your IMDB Watchlist page
- Find the export link at the bottom of the page
- Right click and copy the link
- Paste it in the User Preferences window of the program

### Importing Your Lists
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/bf5ede4b-c663-4c02-9b19-dcacde26e414)

- Find the dropdown menu at the top right corner
- Go to "Your Lists" page and copy the URL
- Paste it in the User Preferences window of the program

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
- Find out if I can bypass IMDB's robots.txt (probably not)
- Add support for other sites like Letterboxd, maybe?
