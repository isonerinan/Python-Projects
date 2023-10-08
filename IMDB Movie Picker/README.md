# FEATURES
## Movie/Series Recommendation From A User's Watchlist
The watchlist must be public and replaced with the existing link. (example: https://www.imdb.com/user/USER_NAME_HERE/watchlist)

## Movie/Series Recommendation From A User's Existing Lists
All the publicly available user lists are shown. In order to personalize, the default link must be replaced. (example: https://www.imdb.com/user/USER_NAME_HERE/lists)

## Movie/Series Recommendation From A Custom IMDB List
The program can take a publicly available user link list as an input and randomly select a movie from that list.

## Rating History Check
The program checks if the user have rated the recommended movie before and shows the rating score, and the date of rating.

The web scraping code snippet is in the code, however due to IMDB's robots.txt (https://www.imdb.com/robots.txt) this program cannot web scrape the user ratings page. Therefore you need to download the ratings.csv yourself (See [CSV Files](#important-csv-files) for more).

# HOW TO USE
## Downloads
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/3725a159-7791-4101-83a9-bfcec8e55ccd)
- Download [IMDB Random Movie Picker.py](https://github.com/isonerinan/Python-Projects/blob/main/IMDB%20Movie%20Picker/IMDB%20Random%20Movie%20Picker.py)

- Download [ratings.csv](https://github.com/isonerinan/Python-Projects/blob/main/IMDB%20Movie%20Picker/ratings.csv)

- Download [watchlist.csv](https://github.com/isonerinan/Python-Projects/blob/main/IMDB%20Movie%20Picker/watchlist.csv)

Make sure they are in the same directory, if not, you have to change the directory in the code accordingly. 

## (Important) CSV Files
Note that the CSV files are empty.

You can:
- Leave them as is (not recommended because the default is my own watchlist)
- Replace them with your own

To replace them, first go to your IMDB Watchlist and Ratings pages. (Example: https://www.imdb.com/user/YOUR_USER_NAME/ratings and https://www.imdb.com/user/YOUR_USER_NAME/watchlist)

Download the ratings.csv every time you want to update your ratings history for the program using "Export" button:
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/47e54226-9744-4844-9c68-0d9db57e09ee)

Copy the link at the bottom of your Watchlist page:
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/d4a0a6e7-4699-4224-9bd1-53f71c6b2843)


Find the snippet of code below in IMDB Random Movie Picker.py and replace the url with your copied link.
```
def watchlist_random():
    # URL of the IMDb watchlist export page
    url = 'https://www.imdb.com/list/ls507767575/export'
```

## Adding All of Your public IMDB lists

You probably want to replace my lists with your own. To do so, find the code snippet below and change the URL with yours (example: https://www.imdb.com/user/YOUR_USER_NAME/lists).
```
## ASK USER TO PICK A LIST
while True:

    # Replace this URL with the IMDb user lists URL
    url = 'https://www.imdb.com/user/ur135017478/lists'
```

You are now ready to use the program. Have a nice watch!

## Custom User Lists

If, for whatever reason, you decided to give a shot to someone else's taste in movies and found a user list (maybe your friend shared their list with you?) that you would like to try, you can just copy the link (example: https://www.imdb.com/list/ls521086952/) and paste it when prompted:
![image](https://github.com/isonerinan/Python-Projects/assets/38159563/46c6493b-d243-4a7e-83de-5504704f4b83)

# TODO
- Add GUI
- Find out if I can bypass IMDB's robots.txt (probably not)
- Add support for other sites like Letterboxd, maybe?
