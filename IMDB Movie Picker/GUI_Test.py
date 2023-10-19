import shutil
import sys
import os
import requests
from bs4 import BeautifulSoup
import csv
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QInputDialog, QDialog, QLineEdit, QDialogButtonBox, QFileDialog, QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QIcon
from PyQt5.QtSvg import QSvgRenderer

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}

# Custom QDialog class for the Preferences dialog
class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")
        # Ask the user to enter their IMDb user page link and watchlist export link
        self.user_page_link_label = QLabel("IMDB User Page Link:", self)
        self.user_page_link_input = QLineEdit(self)
        self.watchlist_link_label = QLabel("Watchlist Export Link:", self)
        self.watchlist_link_input = QLineEdit(self)

        # Add a button to select the ratings.csv file
        self.ratings_file_label = QLabel("Ratings File Path:", self)
        self.ratings_file_input = QPushButton("Select File", self)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.custom_accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.user_page_link_label)
        layout.addWidget(self.user_page_link_input)
        layout.addWidget(self.watchlist_link_label)
        layout.addWidget(self.watchlist_link_input)
        layout.addWidget(self.ratings_file_label)
        layout.addWidget(self.ratings_file_input)
        layout.addWidget(button_box)
        self.setLayout(layout)

        # Connect the ratings_file_input button to the select_ratings_file function
        self.ratings_file_input.clicked.connect(self.select_ratings_file)

    def custom_accept(self):
            user_page_url = self.user_page_link_input.text()
            watchlist_url = self.watchlist_link_input.text()

            if self.check_url(user_page_url) and self.check_url(watchlist_url):
                super().accept()  # If URLs are valid, close the dialog

            elif self.check_url(user_page_url) and not self.check_url(watchlist_url):
                # Show an error pop-up
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Invalid URL")
                msg.setText("Please enter a valid Watchlist URL.")
                msg.exec_()

            elif not self.check_url(user_page_url) and self.check_url(watchlist_url):
                # Show an error pop-up
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Invalid URL")
                msg.setText("Please enter a valid User Page URL.")
                msg.exec_()

            else:
                # Show an error pop-up
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Invalid URLs")
                msg.setText("Invalid URLs. Please enter valid IMDb URLs.")
                msg.exec_()

        # Check if the user input is a valid URL
    def check_url(self, url):
            # Check if the URL starts with "https://www.imdb.com/"
            return url.startswith("https://www.imdb.com/")

    # Ask user to select the directory for their ratings.csv file
    def select_ratings_file(self):
        # Open a file dialog to select the ratings.csv file
        ratings_file_path = QFileDialog.getOpenFileName(self, 'Select ratings.csv', '', 'CSV files (*.csv)')[0]

        # Check if the user selected a file
        if ratings_file_path:
            # Check if the ratings.csv file is in the same directory as the script
            if not os.path.isfile(ratings_file_path):
                # If not, copy the ratings.csv file to the same directory as the script
                shutil.copy(ratings_file_path, os.path.dirname(os.path.realpath(__file__)))


            # Update the ratings_file_input text with the ratings.csv file path
            self.ratings_file_input.setText(ratings_file_path)

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

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        main_layout.addLayout(content_layout)

        # Create a menu toolbar with an "Options" menu (which has "User Preferences" and "Theme" submenus), "Help" menu, and "About" menu
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Options")

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)

        menu_bar.addAction(help_action)
        menu_bar.addAction(about_action)

        # Create a "User Preferences" action in the "Options" menu
        user_preferences_action = QAction("User Preferences", self)
        user_preferences_action.triggered.connect(self.create_preferences_file)
        options_menu.addAction(user_preferences_action)

        # Create a "Theme" submenu in the "Options" menu
        theme_menu = QMenu("Theme", self)
        options_menu.addMenu(theme_menu)

        # Create a "Light" action in the "Theme" submenu
        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(self.light_theme)
        theme_menu.addAction(light_theme_action)

        # Create a "Dark" action in the "Theme" submenu
        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(self.dark_theme)
        theme_menu.addAction(dark_theme_action)

        # Check if the preferences file exists, and create it if not
        self.preferences_file = "user_preferences.txt"
        self.user_page_link = ""
        self.watchlist_link = ""

        # Check if the preferences file exists or not empty
        if not self.check_preferences_file() or os.stat(self.preferences_file).st_size == 0:
            self.create_preferences_file()

        # Check the preferences file and get the necessary links
        self.user_page_link, self.watchlist_link = self.checkPreferences()

        # Create a combo box to select a list
        list_combo = QComboBox()
        list_combo.addItem("Watchlist")  # Add a default option
        self.list_names = []
        self.list_links = []

        # Send an HTTP GET request to fetch the IMDb user lists page
        url = self.user_page_link + "/lists"
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

        # self.dark_theme()

    def check_preferences_file(self):
        return os.path.isfile(self.preferences_file)

    # Create a new preferences file in a form of dictionary
    def create_preferences_file(self):
        dialog = PreferencesDialog() # Open the "User Preferences" dialog
        result = dialog.exec_()
        if result == QDialog.Accepted:
            user_page_link = str(dialog.user_page_link_input.text())
            watchlist_link = str(dialog.watchlist_link_input.text())
            with open(self.preferences_file, "w") as file:
                file.write(f"\"User Page Link\": \"{user_page_link}\"\n\"Watchlist Link\": \"{watchlist_link}\"")

    def find_random_movie(self):
        selected_index = self.list_combo.currentIndex()
        if selected_index == 0:
            self.watchlist_random(self.watchlist_link)
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

                # To get the title type and the poster, we need to scrape the movie's/series' own page
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

    ## IF A WATCHLIST, DOWNLOAD THE CSV FILE AND SELECT A MOVIE/SERIES RANDOMLY ##
    def watchlist_random(self, url):
        # Define the destination file path where you want to save the CSV file
        self.watchlist_csv = 'watchlist.csv'

        # Send an HTTP GET request to the URL0
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the content of the response
            content = response.text

            # Save the content to the destination file
            with open(self.watchlist_csv, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            print(
                "\nFailed to download the CSV file. Check the URL or make sure your watchlist is public and try again.")
            return

        # Read the CSV file and store its data in a list of dictionaries
        csv_data = []
        with open(self.watchlist_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                csv_data.append(row)

        # Check if there's data in the CSV file
        if csv_data:
            # Randomly select a row from the CSV data
            random_item = random.choice(csv_data)

            # Check if the user has rated the movie/series before
            user_rating = self.checkRatings(random_item['Title'], random_item['Title Type'])

            # Extract and print the desired columns
            self.result_label.setText(f"<div style=\"font-size: 18px;\">"
                                      f"<a href=\"{random_item['URL']}\"><h1>{random_item['Title']}</h1></a><br>"
                                      f"<b>Title Type:</b> {random_item['Title Type']}<br>"
                                      f"<b>IMDb Rating:</b> {random_item['IMDb Rating']}<br>"
                                      f"<b>Runtime:</b> {random_item['Runtime (mins)']}<br>"
                                      f"<b>Year:</b> {random_item['Year']}<br>"
                                      f"<b>Genres:</b> {random_item['Genres']}<br>"
                                      f"<b>Director/Creator:</b> {random_item['Directors']}<br><br></div>"
                                      f"{user_rating}")

            # To get the title type and the poster, we need to scrape the movie's/series' own page
            # Send an HTTP GET request to fetch the list page
            second_response = requests.get(random_item['URL'], headers=headers)

            # Check if the request was successful
            if second_response.status_code == 200:
                # Parse the HTML content of the page
                second_soup = BeautifulSoup(second_response.content, 'html.parser')

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

        else:
            print("The CSV file is empty.")
            return


    ## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
    def checkRatings(self, title, title_type):
        # URL of the IMDb ratings export page
        # (does not work because of IMDB's robots.txt's web scraping precautions)
        # So the best way would be to download ratings.csv manually
        # ratings_url = "https://www.imdb.com/user/ur135017478/ratings/export"

        # Define the destination file path where you want to save the CSV file
        self.ratings_csv = 'ratings.csv'

        """
        # Send the request using the session
        ratings_response = session.get(ratings_url)

        # Check if the request was successful
        if ratings_response.status_code == 200:
            # Get the content of the response
            content = response.text

            # Save the content to the destination file
            with open(self.ratings_csv, 'w', encoding='utf-8') as file:
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
            with open(self.ratings_csv, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    self.ratings_csv_data.append(row)
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


    # Check the preferences file for the user's IMDb user page link and watchlist export link
    def checkPreferences(self):
        with open(self.preferences_file, "r") as file:
            preferences = file.read()
            preferences = preferences.split("\n")

            user_page_link = preferences[0].split(": ")[1].strip("\"")
            watchlist_link = preferences[1].split(": ")[1].strip("\"")

            return user_page_link, watchlist_link

    # Change the theme to light
    def light_theme(self):
        self.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.list_combo.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.result_label.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.poster_label.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.menuBar().setStyleSheet("background-color: #ffffff; color: #000000;")

    # Change the theme to dark
    def dark_theme(self):
        self.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.list_combo.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.result_label.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.poster_label.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.menuBar().setStyleSheet("background-color: #000000; color: #ffffff;")

    # Show the help dialog
    # Show the help dialog
    def help(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help")
        msg.setText(
            "This program allows you to randomly select a movie or TV series from your IMDb watchlist or any of your IMDb lists.<br><br>"
            "For more information on how to use this program, please visit:<br><br>"
            "<a href='https://github.com/isonerinan/Python-Projects/tree/main/IMDB%20Movie%20Picker'>"
            "https://github.com/isonerinan/Python-Projects/tree/main/IMDB%20Movie%20Picker</a>")
        msg.exec_()

    # Show the about dialog
    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("<h1>IMDB Movie Picker</h1>"
                    "<h3>Version 1.0</h3>"
                    "<b>Created by:</b> İbrahim Soner İNAN<br><br>"
                    "<a href='https://github.com/isonerinan'>GitHub</a><br><br>"
                    "<a href='https://www.linkedin.com/in/isonerinan'>LinkedIn</a><br><br>"
                    "<a href='https://www.instagram.com/isonerinan'>Instagram</a><br><br>"
                    "<a href='https://www.twitter.com/isonerinan'>Twitter</a>")
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
