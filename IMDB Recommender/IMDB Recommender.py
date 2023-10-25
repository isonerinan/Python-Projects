import math
import shutil
import sys
import os
import requests
from bs4 import BeautifulSoup
import csv
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QDialog, QLineEdit, QDialogButtonBox, QFileDialog, QMessageBox, QMenu, QAction, \
    QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QErrorMessage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QIcon, QPalette, QColor
from PyQt5.QtSvg import QSvgRenderer
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}

# Custom QDialog class for the Preferences dialog
class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")
        # Ask the user to enter their IMDb user page link and watchlist export link
        self.user_lists_link_label = QLabel("IMDB User Lists Link:", self)
        self.user_lists_link_input = QLineEdit(self)
        self.watchlist_link_label = QLabel("Watchlist Export Link:", self)
        self.watchlist_link_input = QLineEdit(self)

        # Add a button to select the ratings.csv file
        self.ratings_file_label = QLabel("Ratings File Path:", self)
        self.ratings_file_input = QPushButton("Select File", self)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.custom_accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.user_lists_link_label)
        layout.addWidget(self.user_lists_link_input)
        layout.addWidget(self.watchlist_link_label)
        layout.addWidget(self.watchlist_link_input)
        layout.addWidget(self.ratings_file_label)
        layout.addWidget(self.ratings_file_input)
        layout.addWidget(button_box)
        self.setLayout(layout)

        # Connect the ratings_file_input button to the select_ratings_file function
        self.ratings_file_input.clicked.connect(self.select_ratings_file)

    def custom_accept(self):
        # Check the user inputs and create a flag
        self.user_lists_link = self.user_lists_link_input.text()
        self.watchlist_link = self.watchlist_link_input.text()

        input_flag = self.check_input(self.user_lists_link, self.watchlist_link)
        print(f"Input flag: {input_flag}")

        # Check if "user_preferences.txt" file exists
        if os.path.isfile("user_preferences.txt"):
            # Read the user preferences from the text file
            print("Preferences file exists.")
            self.old_user_lists_link, self.old_watchlist_link = window.checkPreferences()
            print(self.old_user_lists_link, self.old_watchlist_link)

            self.old_user_lists_link, self.old_watchlist_link= self.correct_preferences(self.old_user_lists_link, self.old_watchlist_link)

            preferences_flag = self.check_preferences(self.old_user_lists_link, self.old_watchlist_link)
            print(f"Preferences flag: {preferences_flag}")

            # Check if the flags give an error
            self.result(preferences_flag, input_flag)

        else:
            preferences_flag = 1
            print(f"Preferences flag: {preferences_flag}")
            self.result(preferences_flag, input_flag)

    # Check if the user input is a valid URL
    def check_url(self, url):
            # Check if the URL starts with "https://www.imdb.com/"
            return url.startswith("https://www.imdb.com/")

    # Check all the possible combinations of user inputs and flag them
    def check_input(self, lists_input, watchlist_input):
        # Check and flag if the user inputs are valid URLs
        if self.check_url(lists_input) and self.check_url(watchlist_input):
            return 0
        elif lists_input == "" and watchlist_input == "":
            return 1
        elif self.check_url(lists_input) and watchlist_input == "":
            return 2
        elif lists_input == "" and self.check_url(watchlist_input):
            return 3
        elif (not self.check_url(lists_input) and lists_input != "") and (not self.check_url(watchlist_input) and watchlist_input != ""):
            return 4
        elif (not self.check_url(lists_input) and lists_input != "") and self.check_url(watchlist_input):
            return 5
        elif self.check_url(lists_input) and (not self.check_url(watchlist_input) and watchlist_input != ""):
            return 6
        elif (not self.check_url(lists_input) and lists_input != "") and watchlist_input == "":
            return 7
        elif lists_input == "" and (not self.check_url(watchlist_input) and watchlist_input != ""):
            return 8
        else:
            return 9

    # Check all the possible combinations of preferences file inputs and flag them
    def check_preferences(self, lists_pref, watchlist_pref):
        if self.check_url(lists_pref) and self.check_url(watchlist_pref):
            return 0
        elif lists_pref == "" and watchlist_pref == "":
            return 1
        elif self.check_url(lists_pref) and watchlist_pref == "":
            return 2
        elif lists_pref == "" and self.check_url(watchlist_pref):
            return 3

    # Correct the user preferences file if there is something wrong with it
    def correct_preferences(self, lists_pref, watchlist_pref):
        if not self.check_url(lists_pref):
            lists_pref = ""

        if not self.check_url(watchlist_pref):
            watchlist_pref = ""

        return lists_pref, watchlist_pref

    # Return error message based on the preferences and input flags
    def result(self, preferences_flag, input_flag):
        match (preferences_flag, input_flag):
            case (0, 4) | (1, 1) | (1, 4) | (2, 4) | (2, 7) | (3, 4) | (3, 8):
                # Show QMessageBox with the error message
                error_message = QMessageBox()
                error_message.setWindowTitle("Error")
                error_message.setText("Please enter a valid URL for both fields.")
                error_message.setIcon(QMessageBox.Critical)
                error_message.exec_()

            case (0, 5) | (0, 7) | (1, 3) | (1, 5) | (2, 5) | (3, 1) | (3, 3) | (3, 5) | (3, 7):
                # Show QMessageBox with the error message
                error_message = QMessageBox()
                error_message.setWindowTitle("Error")
                error_message.setText("Please enter a valid URL for the \"IMDB User Lists Link\" field.")
                error_message.setIcon(QMessageBox.Critical)
                error_message.exec_()

            case (0, 6) | (0, 8) | (1, 2) | (1, 6) | (1, 7) | (1, 8) | (2, 1) | (2, 2) | (2, 6) | (2, 8) | (3, 6):
                # Show QMessageBox with the error message
                error_message = QMessageBox()
                error_message.setWindowTitle("Error")
                error_message.setText("Please enter a valid URL for the \"Watchlist Export Link\" field.")
                error_message.setIcon(QMessageBox.Critical)
                error_message.exec_()

            case (0, 0) | (1, 0) | (2, 0) | (3, 0):
                self.accept()

            case (0, 1):
                self.user_lists_link = self.old_user_lists_link
                self.watchlist_link = self.old_watchlist_link
                self.accept()

            case (0, 2) | (3, 2):
                self.watchlist_link = self.old_watchlist_link
                self.accept()

            case (0, 3) | (2, 3):
                self.user_lists_link = self.old_user_lists_link
                self.accept()




    # Ask user to select the directory for their ratings.csv file
    def select_ratings_file(self):
        # Open a file dialog to select the ratings.csv file
        ratings_file_path = QFileDialog.getOpenFileName(self, 'Select ratings.csv', '', 'CSV files (*.csv)')[0]

        # Check if the user selected a file
        if ratings_file_path:
            # Check if the ratings.csv file is in the same directory as the script or executable
            if not os.path.dirname(os.path.realpath(__file__)) + "ratings.csv" == ratings_file_path:
                # If not, copy the ratings.csv file to the same directory as the script
                shutil.copy(ratings_file_path, "ratings.csv")

            # Update the ratings_file_input text with the ratings.csv file path
            self.ratings_file_input.setText(ratings_file_path)

# Custom QDialog class for the Favorites dialog
class MyFavoritesDialog(QDialog):
    def __init__(self, favorites_data):
        super().__init__()
        self.setWindowTitle("Favorites")

        layout = QVBoxLayout()

        # Set the window size to a reasonable size so that the table is visible
        self.resize(800, 500)

        # If there are too many favorites, show them in a table
        if favorites_data:
            table = QTableWidget()
            table.setRowCount(len(favorites_data))
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Title", "URL"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            for row in range(len(favorites_data)):
                for column in range(2):
                    table.setItem(row, column, QTableWidgetItem(favorites_data[row][column]))

            layout.addWidget(table)

        else:
            no_favorites_label = QLabel("You have no favorited movies/series.")
            layout.addWidget(no_favorites_label)

        self.setLayout(layout)

# Custom QDialog class for the Statistics dialog
class StatisticsWindow(QDialog):
    def __init__(self, ratings_data):
        super().__init__()
        self.setWindowTitle("Statistics")

        # Set the window size to a reasonable size
        self.resize(700, 400)

        layout = QVBoxLayout()

        # Your favorite director/creator based on the average rating you have given to their movies/series
        favorite_director_label = QLabel("<h3>Your Favorite Movie Directors</h3>")
        favorite_director_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_director_label)

        # Get the favorite director/creator
        favorite_directors = self.get_favorite_director(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        director_labels_layout = QVBoxLayout()

        # Iterate through the favorite directors and add them to QLabel widgets
        for director, info in favorite_directors[:5]:
            director_label = QLabel(f"<b>{director}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            director_label.setAlignment(Qt.AlignCenter)
            director_labels_layout.addWidget(director_label)

        # Add "See All" button
        director_see_all = QPushButton("See All")
        # Connect the button click to see_all_directors function
        director_see_all.clicked.connect(lambda: self.see_all_directors(ratings_data, favorite_directors))
        director_labels_layout.addWidget(director_see_all)

        # Create a QWidget to hold the QLabel widgets
        director_labels_widget = QWidget()
        director_labels_widget.setLayout(director_labels_layout)

        # Add the director_labels_widget to your main layout
        layout.addWidget(director_labels_widget)

        # Your favorite genre based on the average rating you have given to movies/series of that genre
        favorite_genre_label = QLabel("<h3>Your Favorite Genres</h3>")
        favorite_genre_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_genre_label)

        # Get the favorite genre
        favorite_genres = self.get_favorite_genre(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        genre_labels_layout = QVBoxLayout()

        # Iterate through the favorite directors and add them to QLabel widgets
        for genre, info in favorite_genres[:5]:
            genre_label = QLabel(f"<b>{genre}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            genre_label.setAlignment(Qt.AlignCenter)
            genre_labels_layout.addWidget(genre_label)

        # Add "See All" button
        genre_see_all = QPushButton("See All")
        # Connect the button click to see_all_genres function
        genre_see_all.clicked.connect(lambda: self.see_all_genres(ratings_data, favorite_genres))
        genre_labels_layout.addWidget(genre_see_all)

        # Create a QWidget to hold the QLabel widgets
        genre_labels_widget = QWidget()
        genre_labels_widget.setLayout(genre_labels_layout)

        # Add the director_labels_widget to your main layout
        layout.addWidget(genre_labels_widget)

        # Your favorite TV series based on the average rating you have given to its episodes
        favorite_tv_series_label = QLabel("<h3>Your Favorite TV Shows</h3>")
        favorite_tv_series_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_tv_series_label)

        # Get the favorite TV series
        favorite_tv_series = self.get_favorite_tv_series(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        tv_labels_layout = QVBoxLayout()

        # Iterate through the favorite directors and add them to QLabel widgets
        for tv, info in favorite_tv_series[:5]:
            tv_label = QLabel(f"<b>{tv}:</b> {info[0]}/10 ({info[1]:.2f}/10 average episode rating in {info[2]} episodes) with {info[3]:.2f} ❤️")
            tv_label.setAlignment(Qt.AlignCenter)
            tv_labels_layout.addWidget(tv_label)

        # Add "See All" button
        tv_see_all = QPushButton("See All")
        # Connect the button click to see_all_tv_series function
        tv_see_all.clicked.connect(lambda: self.see_all_tv_series(ratings_data, favorite_tv_series))
        tv_labels_layout.addWidget(tv_see_all)

        # Create a QWidget to hold the QLabel widgets
        tv_labels_widget = QWidget()
        tv_labels_widget.setLayout(tv_labels_layout)

        # Add the director_labels_widget to your main layout
        layout.addWidget(tv_labels_widget)

        # Add more labels or widgets for other statistics

        self.setLayout(layout)

    def get_favorite_director(self, ratings_data):
        director_ratings = {}
        director_title_counts = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is "movie"
            if item['Title Type'] == "movie":
                # Extract director and rating
                director = item['Directors']
                rating = float(item['Your Rating'])

                # Check if the director is already in the dictionary
                if director in director_ratings:
                    # Add the rating to the existing director
                    director_ratings[director] += rating
                    director_title_counts[director] += 1
                else:
                    # Add the director to the dictionary
                    director_ratings[director] = rating
                    director_title_counts[director] = 1

        # Check if there are any ratings
        if director_ratings:
            # Calculate the average rating for each director
            director_average_ratings = {
                director: director_ratings[director] / director_title_counts[director]
                for director in director_ratings
            }

            # Calculate the love_formula for each director
            director_love_formulas = {
                director: (avg_rating, director_title_counts[director], ((avg_rating ** 5) * (director_title_counts[director] ** 1.3)) / 1000)
                for director, avg_rating in director_average_ratings.items()
            }

            # Sort the directors by the love_formula in descending order
            sorted_directors = sorted(director_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            return sorted_directors
        else:
            return "N/A"  # Return "N/A" and 0.0 for average rating when there are no ratings

    def see_all_directors(self, ratings_data, favorite_directors):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Directors")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many directors, show them in a table
        if favorite_directors:
            table = SortableTable(len(favorite_directors), 4)
            table.setHorizontalHeaderLabels(["Director", "Average Rating", "Title Count", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (director, info) in enumerate(favorite_directors):
                # Convert data to strings
                director_str = str(director)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(director_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)


        else:
            no_directors_label = QLabel("You have no favorite directors.")
            layout.addWidget(no_directors_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    # Get the favorite genre based on the average rating you have given to movies/series of that genre
    def get_favorite_genre(self, ratings_data):
        genre_ratings = {}
        genre_title_counts = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is "movie"
            if item['Title Type'] == "movie":
                # Extract genre and rating
                genre = item['Genres']
                rating = float(item['Your Rating'])

                # Check if the genre is already in the dictionary
                if genre in genre_ratings:
                    # Add the rating to the existing genre
                    genre_ratings[genre] += rating
                    genre_title_counts[genre] += 1
                else:
                    # Add the genre to the dictionary
                    genre_ratings[genre] = rating
                    genre_title_counts[genre] = 1

        # Check if there are any ratings
        if genre_ratings:
            # Calculate the average rating for each genre
            genre_average_ratings = {
                genre: genre_ratings[genre] / genre_title_counts[genre]
                for genre in genre_ratings
            }

            # Calculate the love_formula for each genre
            genre_love_formulas = {
                genre: (avg_rating, genre_title_counts[genre],
                           ((avg_rating ** 5) * (genre_title_counts[genre] ** 1.3)) / 1000)
                for genre, avg_rating in genre_average_ratings.items()
            }

            # Sort the genres by the love_formula in descending order
            sorted_genres = sorted(genre_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            return sorted_genres
        else:
            return "N/A"  # Return "N/A" and 0.0 for average rating when there are no ratings

    def see_all_genres(self, ratings_data, favorite_genres):
        # Create a new QDialog to show all the genres
        dialog = QDialog()
        dialog.setWindowTitle("All Genres")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many genres, show them in a table
        if favorite_genres:
            table = SortableTable(len(favorite_genres), 4)
            table.setHorizontalHeaderLabels(["Genre", "Average Rating", "Title Count", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (genre, info) in enumerate(favorite_genres):
                # Convert data to strings
                genre_str = str(genre)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(genre_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

        else:
            no_genres_label = QLabel("You have no favorite genres.")
            layout.addWidget(no_genres_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    # Get the favorite TV series based on the average rating you have given to its episodes
    def get_favorite_tv_series(self, ratings_data):
        tv_series_data = {}

        # Loop through the ratings_data list
        for item in ratings_data:

            # Check if the title type is "tvSeries"
            if item['Title Type'] == "tvSeries":
                series_name = item['Title']
                rating = float(item['Your Rating'])

                if series_name not in tv_series_data:
                    tv_series_data[series_name] = {
                        'Your Rating': 0,
                        'Average Episode Rating': 0.0,
                        'Love Formula': 0.0,
                        'Episode Count': 0  # Initialize episode count
                    }

                # Update TV series rating
                tv_series_data[series_name]['Your Rating'] = rating
                tv_series_data[series_name]['Average Episode Rating'] += 0.0
                tv_series_data[series_name]['Episode Count'] += 0

            # Check if the title type is "tvEpisode"
            elif item['Title Type'] == "tvEpisode":
                # Split the title into series name and episode name
                # There are four possibilities:
                # "Series Name: Episode Name",
                # "Series Name: 'Episode Name: Episode Part'",
                # "'IP Name: Series Name': Episode Name",
                # "'IP Name: Series Name': 'Episode Name: Episode Part'"
                title_split = item['Title'].split(":")

                # Determine how many colons are in the title and act accordingly
                num_colons = len(title_split)

                if num_colons == 2:
                    # Format: "Series Name: Episode Name"
                    series_name = title_split[0]
                elif num_colons == 3:
                    # Format: "Series Name: 'Episode Name: Episode Part'" or "'IP Name: Series Name': Episode Name"
                    # Check the URL to determine which format it is
                    title_url = item['URL']

                    # Get the HTML content of the title URL
                    title_html = requests.get(title_url, headers=headers).text

                    # Create a BeautifulSoup object from the HTML content
                    title_soup = BeautifulSoup(title_html, 'html.parser')

                    # Get the title from the HTML content
                    series_name = title_soup.find("div", class_="kBNRhP").a.text
                    print(series_name)

                elif num_colons == 4:
                    # Format: "'IP Name: Series Name': 'Episode Name: Episode Part'"
                    series_name = title_split[0] + ":" + title_split[1]
                else:
                    # Handle unexpected formats
                    continue  # Skip this item

                if series_name not in tv_series_data:
                    tv_series_data[series_name] = {
                        'Your Rating': 0,
                        'Average Episode Rating': 0.0,
                        'Love Formula': 0.0,
                        'Episode Count': 0  # Initialize episode count
                    }

                # Update episode rating
                tv_series_data[series_name]['Your Rating'] += 0
                tv_series_data[series_name]['Average Episode Rating'] += float(item['Your Rating'])
                tv_series_data[series_name]['Episode Count'] += 1

        # Calculate average episode ratings and love formulas
        for series_name, data in tv_series_data.items():
            if data['Episode Count'] > 0:
                data['Average Episode Rating'] /= data['Episode Count']

            if data['Episode Count'] != 0 and data['Your Rating'] != 0:
                love_formula = (
                        # Geometric mean of user's rating for the series and average episode rating
                        # Weighted by the number of episodes rated by the user
                        math.sqrt((data['Average Episode Rating'] ** 5) *
                                  (data['Your Rating'] ** 5)) *
                        (data['Episode Count'] ** 1.3) / 1000
                )

            elif data['Episode Count'] != 0 and data['Your Rating'] == 0:
                love_formula = (
                        (data['Average Episode Rating'] ** 2.5) *
                        (data['Episode Count'] ** 1.3) / 1000
                )

            elif data['Episode Count'] == 0 and data['Your Rating'] != 0:
                love_formula = (
                        (data['Your Rating'] ** 5) / 1000
                )

            data['Love Formula'] = love_formula

        # Sort the TV series by love formula in descending order
        sorted_series = sorted(
            tv_series_data.items(),
            key=lambda x: x[1]['Love Formula'],
            reverse=True
        )

        # Return the sorted data in the desired format
        formatted_data = [(series_name, (data['Your Rating'], data['Average Episode Rating'], data['Episode Count'], data['Love Formula'])) for
                          series_name, data in sorted_series]

        return formatted_data if formatted_data else "N/A"

    def see_all_tv_series(self, ratings_data, favorite_tv_series):
        # Create a new QDialog to show all the TV series
        dialog = QDialog()
        dialog.setWindowTitle("All TV Shows")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1000, 550)

        layout = QVBoxLayout()

        # If there are too many TV series, show them in a table
        if favorite_tv_series:
            table = SortableTable(len(favorite_tv_series), 5)
            table.setHorizontalHeaderLabels(["TV Show", "Series Rating", "Average Episode Rating", "Episodes Rated By You", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (series, info) in enumerate(favorite_tv_series):
                # Convert data to strings
                series_str = str(series)
                series_rating_str = f"{int(info[0])}"
                avg_rating_str = f"{info[1]:.2f}"
                episode_count_str = str(info[2])
                your_love_str = f"{info[3]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(series_str))
                table.setItem(row, 1, QTableWidgetItem(series_rating_str))
                table.setItem(row, 2, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 3, QTableWidgetItem(episode_count_str))
                table.setItem(row, 4, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

        else:
            no_tv_series_label = QLabel("You have no favorite TV shows.")
            layout.addWidget(no_tv_series_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

class SortableTable(QTableWidget):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels([""])
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)
        self.sorting_order = Qt.DescendingOrder  # Default sorting order

    def sort_table(self, logicalIndex):
        items = [(
                 self.item(row, logicalIndex).text(), [self.item(row, col).text() for col in range(self.columnCount())],
                 row) for row in range(self.rowCount())]

        if self.sorting_order == Qt.AscendingOrder:
            items.sort(key=lambda x: (float(x[0]) if x[0].replace(".", "", 1).isdigit() else x[0], x[1]))
        else:
            items.sort(key=lambda x: (float(x[0]) if x[0].replace(".", "", 1).isdigit() else x[0], x[1]), reverse=True)

        for row, (_, row_data, original_row) in enumerate(items):
            for col, value in enumerate(row_data):
                new_item = QTableWidgetItem(value)
                self.setItem(row, col, new_item)

        self.sorting_order = Qt.AscendingOrder if self.sorting_order == Qt.DescendingOrder else Qt.DescendingOrder


class ModernApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.theme = "dark"
        self.star_color = "white"
        # Create a star icon at the top left corner on the movie poster
        star_icon = QIcon("star.svg")
        star_icon_renderer = QSvgRenderer("star.svg")
        self.star_icon_pixmap = QPixmap(20, 20)
        self.star_icon_pixmap.fill(Qt.transparent)
        self.star_icon_painter = QPainter(self.star_icon_pixmap)
        star_icon_renderer.render(self.star_icon_painter)
        self.star_icon_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        self.star_icon_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
        self.star_icon_painter.end()
        self.star_icon_label = QLabel()
        self.star_icon_label.setPixmap(self.star_icon_pixmap)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("IMDB Recommender")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Create a menu toolbar
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Options")

        statistics_action = QAction("Your Statistics", self)
        statistics_action.triggered.connect(self.statistics)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)

        menu_bar.addAction(statistics_action)
        menu_bar.addAction(help_action)
        menu_bar.addAction(about_action)

        # Create a "User Preferences" action in the "Options" menu
        user_preferences_action = QAction("User Preferences", self)
        user_preferences_action.triggered.connect(self.create_preferences_file)
        options_menu.addAction(user_preferences_action)

        # Create a "Favorites" action in the "Options" menu
        favorites_action = QAction("Favorites", self)
        favorites_action.triggered.connect(self.favorites)
        options_menu.addAction(favorites_action)

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
        self.user_lists_link = ""
        self.watchlist_link = ""

        # Create a combo box to select a list
        self.list_combo = QComboBox()
        self.list_combo.addItem("Watchlist")  # Add a default option
        self.list_names = []
        self.list_links = []

        # Check if the preferences file exists or not empty
        if not self.check_preferences_file() or os.stat(self.preferences_file).st_size == 0:
            self.create_preferences_file()

        # Check the preferences file and get the necessary links
        self.user_lists_link, self.watchlist_link = self.checkPreferences()

        if not (self.user_lists_link == "" and self.watchlist_link == ""):
            # Send an HTTP GET request to fetch the IMDb user lists page
            response = requests.get(self.user_lists_link, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                list_items = soup.find_all('li', class_='ipl-zebra-list__item user-list')

                # Extract the list names and links
                for item in list_items:
                    list_name = item.find('a', class_='list-name').text.strip()
                    self.list_names.append(list_name)
                    href = item.find('a', class_='list-name')['href']
                    list_link = f'https://www.imdb.com{href}'
                    self.list_links.append(list_link)
                    self.list_combo.addItem(list_name)

        self.main_layout.addWidget(self.list_combo)

        # Create a new QLabel for displaying the movie/series poster
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.poster_label)

        # Create a QLabel for displaying movie/series details
        self.result_label = QLabel("Movie Recommendation Will Appear Here")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setOpenExternalLinks(True)
        self.result_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.result_label.setTextFormat(Qt.RichText)
        self.main_layout.addWidget(self.result_label)

        # Create a QLineEdit for custom IMDB list input
        self.custom_list = QLineEdit()
        self.custom_list.setPlaceholderText("Want to explore a custom list? Paste it here!")
        self.custom_list.setAlignment(Qt.AlignCenter)

        # Create a QPushButton
        search_button = QPushButton("Search")

        # Connect the button's clicked signal to the slot
        search_button.clicked.connect(self.search_button_click)

        # Add both the QLineEdit and the button to a container widget
        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.addWidget(self.custom_list)
        container_layout.addWidget(search_button)
        container.setLayout(container_layout)

        # Add the container to the main layout
        self.main_layout.addWidget(container)

        self.setLayout(self.main_layout)

        find_movie_button = QPushButton("Find A Movie!")
        find_movie_button.clicked.connect(self.find_random_movie)
        self.main_layout.addWidget(find_movie_button)

        #self.list_combo = self.list_combo


    def check_preferences_file(self):
        return os.path.isfile(self.preferences_file)

    # Create a new preferences file in a form of dictionary
    def create_preferences_file(self):
        dialog = PreferencesDialog() # Open the "User Preferences" dialog
        result = dialog.exec_()

        if result == QDialog.Accepted:
            with open(self.preferences_file, "w") as file:
                file.write(f"\"User Lists Link\": \"{dialog.user_lists_link}\"\n"
                           f"\"Watchlist Link\": \"{dialog.watchlist_link}\"")

            # Update the combo box with the new lists
            self.list_combo.clear()
            self.list_combo.addItem("Watchlist")  # Add a default option
            self.list_names = []
            self.list_links = []


            if dialog.user_lists_link.startswith("https://www.imdb.com/"):
                # Send an HTTP GET request to fetch the IMDb user lists page
                response = requests.get(dialog.user_lists_link, headers=headers)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    list_items = soup.find_all('li', class_='ipl-zebra-list__item user-list')

                    # Extract the list names and links
                    for item in list_items:
                        list_name = item.find('a', class_='list-name').text.strip()
                        self.list_names.append(list_name)
                        href = item.find('a', class_='list-name')['href']
                        list_link = f'https://www.imdb.com{href}'
                        self.list_links.append(list_link)
                        self.list_combo.addItem(list_name)

            else:
                # Qmessagebox to show error
                error_message = QMessageBox()
                error_message.setWindowTitle("Error")
                error_message.setText("Please enter a valid URL for the \"IMDB User Lists Link\" field.")
                error_message.setIcon(QMessageBox.Critical)
                error_message.exec_()


    def find_random_movie(self):
        selected_index = self.list_combo.currentIndex()
        if selected_index == 0:
            self.watchlist_random("watchlist", self.watchlist_link)
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

            # Check how many titles are there in the list
            list_details = soup.select(".lister-total-num-results")
            number_of_titles_str = list_details[0].text.strip()

            # Use a regular expression to extract the integer
            match = re.search(r'\d+', number_of_titles_str)
            if match:
                # The group(0) will contain the first matched integer
                number_of_titles = int(match.group(0))

            # Calculate the page count
            page_count = (number_of_titles // 100) + 1


            # Append all pages to movie_details
            for page in range(2, page_count + 1):
                # Use regex to remove referral parameters
                list_url_without_referral = re.sub(r'[?&]ref_[^&]*', '', list_url)

                # Send an HTTP GET request to fetch the list page
                response = requests.get(f"{list_url_without_referral}?page={page}", headers=headers)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract the movie or TV series details from the list
                    movie_details += soup.select('.lister-item-content')

                else:
                    print("\nFailed to retrieve the list. Check the URL and try again.")
                    return

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
    def watchlist_random(self, title, url):
        # Define the destination file path where you want to save the CSV file
        self.watchlist_csv = f'watchlist.csv'

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

                    # Create a star icon at the top left corner on the movie poster
                    star_icon = QIcon("star.svg")
                    star_icon_renderer = QSvgRenderer("star.svg")
                    self.star_icon_pixmap = QPixmap(20, 20)
                    self.star_icon_pixmap.fill(Qt.transparent)
                    self.star_icon_painter = QPainter(self.star_icon_pixmap)
                    star_icon_renderer.render(self.star_icon_painter)
                    self.star_icon_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                    self.star_icon_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
                    self.star_icon_painter.end()

                    # Change the color of the star icon to yellow if it is in the favorites list
                    if self.check_favorites(random_item['Title']):
                        self.star_color = "yellow"
                        self.change_star_color(self.star_color)

                    else:
                        # If not in the favorites list, change the color of the star icon to white or black depending on the theme
                        if self.theme == "light":
                            self.star_color = "black"
                            self.change_star_color(self.star_color)

                        else:
                            self.star_color = "white"
                            self.change_star_color(self.star_color)

                    self.star_icon_label = QLabel(self.poster_label)
                    self.star_icon_label.setPixmap(self.star_icon_pixmap)
                    self.star_icon_label.move(10, 10)
                    self.star_icon_label.show()

                    # When clicked, save the movie/series' title and URL to a CSV file name "favorites.csv" and change the color of the star icon to yellow
                    # When clicked again, remove the movie/series from the CSV file and change the color of the star icon to white or black depending on the theme
                    self.star_icon_label.mousePressEvent = lambda event: self.save_favorite(random_item['Title'], random_item['URL'])

            else:
                print("\nFailed to retrieve the list. Check the URL and try again.")

        else:
            print("The CSV file is empty.")
            return


    ## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
    def checkRatings(self, title, title_type):
        # URL of the IMDb ratings export page
        # (does not work because of IMDB's robots.txt's web scraping precautions)
        # So the best way would be to download ratings.csv manually from the IMDb website

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
                    ratings_csv_data.append(row)

        except FileNotFoundError:
            return f"File not found."

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

            user_lists_link = preferences[0].split(": ")[1].strip("\"")
            watchlist_link = preferences[1].split(": ")[1].strip("\"")

            return user_lists_link, watchlist_link

    # Save the movie/series' title and URL to a CSV file name "favorites.csv"
    def save_favorite(self, title, url):
        # Define the destination file path where you want to save the CSV file
        favorites_csv = 'favorites.csv'

        # Initialize a list to store the favorites data
        favorites_data = []

        # Check if the file exists
        if os.path.isfile(favorites_csv):
            # If the file exists, load its data
            with open(favorites_csv, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # Skip the header row (if present)
                next(csv_reader, None)
                # Read the CSV data into a list of dictionaries
                for row in csv_reader:
                    if len(row) == 2:
                        csv_title, csv_url = row
                        favorites_data.append({'Title': csv_title, 'URL': csv_url})

        favorite = self.check_favorites(title)

        # Check if the movie/series is already in the favorites data
        if favorite:
            # If it is, remove the movie/series from the favorites data
            favorites_data.remove(favorite)

            # Write the updated data (including the new addition and removal) to "favorites.csv"
            with open(favorites_csv, 'w', encoding='utf-8') as file:
                # Write the header row
                file.write("Title,URL\n")
                # Write the updated data
                for data in favorites_data:
                    file.write(f"{data['Title']},{data['URL']}\n")

            # Change the color of the star icon to white/black depending on the theme
            if self.theme == "light":
                self.star_color = "black"
                self.change_star_color(self.star_color)
            else:
                self.star_color = "white"
                self.change_star_color(self.star_color)

            # Show a success pop-up
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Removed from Favorites")
            msg.setText("This movie/series has been removed from your favorites.")
            msg.exec_()
            return

        # Append the new movie/series' title and URL to the favorites data
        favorites_data.append({'Title': title, 'URL': url})

        # Write the updated data (including the new addition and removal) to "favorites.csv"
        with open(favorites_csv, 'w', encoding='utf-8') as file:
            # Write the header row
            file.write("Title,URL\n")
            # Write the updated data
            for favorite in favorites_data:
                file.write(f"{favorite['Title']},{favorite['URL']}\n")

        # Change the color of the star icon to yellow
        self.change_star_color("yellow")

        # Show a success pop-up
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Added to Favorites")
        msg.setText("This movie/series has been added to your favorites.")
        msg.exec_()

    # Check if the movie/series is already in the favorites.csv file
    def check_favorites(self, title):
        # Define the destination file path where you want to save the CSV file
        self.favorites_csv = 'favorites.csv'

        # Check if the file exists
        if not os.path.isfile(self.favorites_csv):
            print("File does not exist.")
            return False

        # Check if the movie/series is already in the favorites.csv file
        with open(self.favorites_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row["Title"] == title:
                    return row

        return False

    # Search button logic for custom list input
    def search_button_click(self):
        # Get the text from the QLineEdit
        list_link = self.custom_list.text()

        # Call the list_random function with the input
        self.list_random(list_link)

    # Change the star icon color
    def change_star_color(self, color):
        star_painter = QPainter(self.star_icon_pixmap)
        if color == "yellow":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 212, 59))
            star_painter.end()
            self.star_color = "yellow"

        elif color == "white":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
            star_painter.end()
            self.star_color = "white"

        elif color == "black":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(0, 0, 0))
            star_painter.end()
            self.star_color = "black"

        # Update the star icon label with the new pixmap
        self.star_icon_label.setPixmap(self.star_icon_pixmap)

    # Change the theme to light
    def light_theme(self):
        app.setPalette(light_palette)
        self.theme = "light"
        self.star_color = "black"

        if self.star_color != "yellow":
            self.change_star_color(self.star_color)

    # Change the theme to dark
    def dark_theme(self):
        app.setPalette(dark_palette)
        self.theme == "dark"
        self.star_color = "white"

        if self.star_color != "yellow":
            self.change_star_color(self.star_color)

    # Show the statistics dialog
    def statistics(self):
        # Check if ratings.csv exists
        self.ratings_csv = "ratings.csv"

        try:
            # Read the CSV file and store its data in a list of dictionaries
            ratings_csv_data = []
            with open(self.ratings_csv, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    ratings_csv_data.append(row)

        except FileNotFoundError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Statistics")
            msg.setText("You have not rated any movies/series yet.")
            msg.exec_()
            return

        statistics_window = StatisticsWindow(ratings_csv_data)
        statistics_window.exec_()



    # Show the help dialog
    def help(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help")
        msg.setText(
            "This program allows you to randomly select a movie or TV series from your IMDb watchlist or any of your IMDb lists.<br><br>"
            "For more information on how to use this program, please visit:<br><br>"
            "<a href='https://github.com/isonerinan/Python-Projects/tree/8d8131e42e8525747c1aaa511f09287187d4f8dc/IMDB%20Recommender'>"
            "https://github.com/isonerinan/Python-Projects/tree/8d8131e42e8525747c1aaa511f09287187d4f8dc/IMDB%20Recommender</a>")

        msg.exec_()

    # Show the about dialog
    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("<h1>IMDB Recommender</h1>"
                    "<h3>Version 2.5</h3>"
                    "<b>Created by:</b> İbrahim Soner İNAN<br><br>"
                    "<a href='https://github.com/isonerinan'>GitHub</a><br><br>"
                    "<a href='https://www.linkedin.com/in/isonerinan'>LinkedIn</a><br><br>"
                    "<a href='https://www.instagram.com/isonerinan'>Instagram</a><br><br>"
                    "<a href='https://www.twitter.com/isonerinan'>Twitter</a>")
        msg.exec_()

    # Show the favorited movies/series from the favorites.csv file
    def favorites(self):
        favorites_csv = 'favorites.csv'
        favorites_data = []

        # Check if the file exists
        if not os.path.isfile(favorites_csv):
            # If the file doesn't exist, show a message that there are no favorites.
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Favorites")
            msg.setText("You have no favorited movies/series.")
            msg.exec_()
            return

        # Read the favorites from the CSV file
        with open(favorites_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # Skip the header row
            next(csv_reader, None)
            for row in csv_reader:
                if len(row) == 2:
                    title, url = row
                    favorites_data.append((title, url))

        # Create and display the favorites dialog
        favorites_dialog = MyFavoritesDialog(favorites_data)
        favorites_dialog.exec_()



if __name__ == '__main__':
    # Create the application
    app = QApplication([])

    app.setStyle("Fusion")

    # Set the dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)

    # Set the light theme
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(255, 255, 255))
    light_palette.setColor(QPalette.WindowText, Qt.black)
    light_palette.setColor(QPalette.Base, QColor(240, 240, 240))
    light_palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ToolTipBase, Qt.black)
    light_palette.setColor(QPalette.ToolTipText, Qt.black)
    light_palette.setColor(QPalette.Text, Qt.black)
    light_palette.setColor(QPalette.Button, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ButtonText, Qt.black)
    light_palette.setColor(QPalette.BrightText, Qt.red)
    light_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    light_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    light_palette.setColor(QPalette.HighlightedText, Qt.white)

    # Initialize in dark mode
    app.setPalette(dark_palette)

    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
