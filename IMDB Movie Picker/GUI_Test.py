import sys
import os
import requests
from bs4 import BeautifulSoup
import csv
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}

class ModernApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("IMDB Movie Picker")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Check if the preferences file exists, and create it if not
        self.preferences_file = "user_preferences.txt"
        self.user_page_link = ""

        if not self.check_preferences_file():
            self.create_preferences_file()

        # Load the user's IMDB user page link from the preferences file
        self.load_user_page_link()

        # Create a combo box to select a list
        list_combo = QComboBox()
        list_combo.addItem("Watchlist")  # Add a default option
        self.list_names = []
        self.list_links = []

        # Send an HTTP GET request to fetch the IMDb user lists page
        url = 'https://www.imdb.com/user/ur135017478/lists'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            list_items = soup.find_all('li', class_='ipl-zebra-list__item user-list')

            for item in list_items:
                list_name = item.find('a', class_='list-name').text.strip()
                self.list_names.append(list_name)
                href = item.find('a', class_='list-name')['href']
                list_link = f'https://www.imdb.com{href}'
                self.list_links.append(list_link)
                list_combo.addItem(list_name)

        main_layout.addWidget(list_combo)

        # Create a new QLabel for displaying the movie/series poster
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.poster_label)

        # Create a QLabel for displaying movie/series details
        self.result_label = QLabel("Movie Recommendation Will Appear Here")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setOpenExternalLinks(True)
        self.result_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.result_label.setTextFormat(Qt.RichText)

        main_layout.addWidget(self.result_label)

        find_movie_button = QPushButton("Find A Movie!")
        find_movie_button.clicked.connect(self.find_random_movie)
        main_layout.addWidget(find_movie_button)

        self.list_combo = list_combo

    def check_preferences_file(self):
        return os.path.isfile(self.preferences_file)

    def create_preferences_file(self):
        user_page_link, ok = QInputDialog.getText(self, "IMDB User Page Link", "Enter your IMDB user page link:")
        if ok:
            with open(self.preferences_file, "w") as file:
                file.write(user_page_link)

    def load_user_page_link(self):
        with open(self.preferences_file, "r") as file:
            self.user_page_link = file.read()

    def find_random_movie(self):
        selected_index = self.list_combo.currentIndex()
        if selected_index == 0:
            self.list_random('https://www.imdb.com/list/ls507767575/')
        else:
            selected_list_link = self.list_links[selected_index - 1]
            self.list_random(selected_list_link)

    def list_random(self, list_link):
        # Define the URL of your IMDb list
        list_url = list_link

        # Send an HTTP GET request to fetch the list page
        response = requests.get(list_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the movie or TV series details from the list
            movie_details = soup.select('.lister-item-content')

            # Check if there are any movie details
            if movie_details:
                # Randomly select a movie detail from the list
                random_movie_detail = random.choice(movie_details)

                # Extract the desired information
                title = random_movie_detail.find('h3', class_='lister-item-header').find('a').text.strip()
                url = 'https://www.imdb.com' + random_movie_detail.find('h3', class_='lister-item-header').find('a')['href']

                title_type = ""
                directors = ""

                # To get the title type, we need to scrape the movie's/series' own page
                # Send an HTTP GET request to fetch the list page
                second_response = requests.get(url, headers=headers)

                # Check if the request was successful
                if second_response.status_code == 200:
                    # Parse the HTML content of the page
                    second_soup = BeautifulSoup(second_response.content, 'html.parser')

                    # Extract the movie or TV series details from the list
                    type_details = second_soup.select("div.iwmAVw")
                    if type_details:
                        title_type = type_details[0].select_one('li.ipc-inline-list__item[role="presentation"]').text.strip()

                    if title_type.isdigit():
                        title_type = "Movie"

                    director_details = second_soup.select("div.sc-dffc6c81-3")

                    if director_details:
                        directors = director_details[0].select_one("a.ipc-metadata-list-item__list-content-item--link").text.strip()

                    # Get the movie poster URL from the IMDb page
                    poster_image = second_soup.find('img', class_='ipc-image')

                    if poster_image:
                        poster_url = poster_image['src']

                        # Create a pixmap from the poster image URL
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(poster_url).content)

                        # Set the pixmap to the poster_label
                        self.poster_label.setPixmap(pixmap)


                else:
                    print("\nFailed to retrieve the list. Check the URL and try again.")

                imdb_rating = random_movie_detail.find('span', class_='ipl-rating-star__rating').text.strip()
                runtime = random_movie_detail.find('span', class_='runtime').text.strip()
                year = random_movie_detail.find('span', class_='lister-item-year').text.strip()
                genres = random_movie_detail.find('span', class_='genre').text.strip()
                user_rating = self.checkRatings(title, title_type)

                # Update self.result_label with the movie recommendation
                self.result_label.setText(f"<div style=\"font-size: 18px;\">"
                                          f"<a href=\"{url}\"><h1>{title}</h1></a><br>"
                                          f"<b>Title Type:</b> {title_type}<br>"
                                          f"<b>IMDb Rating:</b> {imdb_rating}<br>"
                                          f"<b>Runtime:</b> {runtime}<br>"
                                          f"<b>Year:</b> {year}<br>"
                                          f"<b>Genres:</b> {genres}<br>"
                                          f"<b>Director/Creator:</b> {directors}<br><br></div>"
                                          f"{user_rating}")



            else:
                print("\nNo movie details found on the list page. Check the HTML structure or the URL.")
        else:
            print("\nFailed to retrieve the list. Check the URL and try again.")
            return


    ## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
    def checkRatings(self, title, title_type):
        # URL of the IMDb ratings export page
        # (does not work because of IMDB's robots.txt's web scraping precautions)
        # So the best way would be to download ratings.csv manually
        # ratings_url = "https://www.imdb.com/user/ur135017478/ratings/export"

        # Define the destination file path where you want to save the CSV file
        ratings_csv = 'ratings.csv'

        """
        # Send the request using the session
        ratings_response = session.get(ratings_url)

        # Check if the request was successful
        if ratings_response.status_code == 200:
            # Get the content of the response
            content = response.text

            # Save the content to the destination file
            with open(ratings_csv, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            print(ratings_response)
            print("Failed to download the CSV file. Check the URL or make sure your ratings list is public and try again.")
            return
        """

        # Check if ratings.csv exists
        try:
            # Read the CSV file and store its data in a list of dictionaries
            ratings_csv_data = []
            with open(ratings_csv, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    ratings_csv_data.append(row)
        except FileNotFoundError:
            return

        # Check if there's data in the CSV file
        if ratings_csv_data:
            # Iterate through the CSV data to find a match for the provided title
            for item in ratings_csv_data:
                if item["Title"] == title:
                    your_rating = item["Your Rating"]
                    date_rated = item["Date Rated"]

                    rating_result = f"\nYou have rated this {title_type} with a rating of <b>{your_rating}/10</b> on <b>{date_rated}</b>."
                    return rating_result # Exit the function once a match is found

            # If no match is found, print a message
            rating_result = f"\nYou have not rated this {title_type}."
            return rating_result

        else:
            rating_result = f"\nYou have not rated this {title_type}."
            return rating_result

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
