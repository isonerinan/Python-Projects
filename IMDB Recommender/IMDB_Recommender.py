import math
import shutil
import sys
import os
import webbrowser

import requests
from bs4 import BeautifulSoup
import csv
import random
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QDialog, QLineEdit, QDialogButtonBox, QFileDialog, QMessageBox, QMenu, QAction, \
    QTableWidget, QHeaderView, QTableWidgetItem, QSlider, QGridLayout, QListWidget, QScrollArea
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPalette, QColor, QFont
from PyQt5.QtSvg import QSvgRenderer
import re
import mechanize
import time
import matplotlib.pyplot as plt
import numpy as np

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}

browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.addheaders = [headers]

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

        # If there are any favorites, show them in a table
        if favorites_data:
            table = QTableWidget()
            table.setRowCount(len(favorites_data))
            table.setColumnCount(3)  # Add an extra column for the delete button
            table.setHorizontalHeaderLabels(["Title", "URL", "Delete"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setEditTriggers(QTableWidget.NoEditTriggers)

            for row in range(len(favorites_data)):
                for column in range(2):
                    table.setItem(row, column, QTableWidgetItem(favorites_data[row][column]))

                # Create a delete button for each row
                delete_button = QPushButton("X")
                delete_button.clicked.connect(self.delete_row)
                delete_button.setProperty("row_index", row)  # Store the row index as a property
                table.setCellWidget(row, 2, delete_button)

            layout.addWidget(table)

        else:
            no_favorites_label = QLabel("You have no favorited movies/series.")
            layout.addWidget(no_favorites_label)

        self.setLayout(layout)

    def delete_row(self):
        # Get the clicked button and the associated row index
        sender = self.sender()
        row_index = sender.property("row_index")
        print(f"Row index: {row_index}")

        # Read the content of the favorites.csv file into a list
        with open('favorites.csv', 'r') as file:
            lines = file.readlines()
            print(lines)

        if 0 <= row_index < len(lines) - 1:
            # Remove the identified row from the list
            lines.pop(row_index + 1)
            print(lines)

            # Write the updated list back to the favorites.csv file (open mode read and write so that we can update lines again)
            with open('favorites.csv', 'w') as file:
                file.writelines(lines)

            # Remove the row from the table
            table = self.findChild(QTableWidget)
            if table is not None:
                table.removeRow(row_index)

            # Update row_index property of the delete buttons
            for row in range(row_index, table.rowCount()):
                button = table.cellWidget(row, 2)
                button.setProperty("row_index", row)

# Custom QDialog class for the Statistics dialog
class StatisticsWindow(QDialog):
    def __init__(self, ratings_data):
        super().__init__()
        self.setWindowTitle("Statistics")

        # Set the window size to a reasonable size
        self.resize(700, 400)

        layout = QGridLayout()

        # Your favorite director/creator based on the average rating you have given to their movies/series
        favorite_director_label = QLabel("<h3>Your Favorite Movie Directors</h3>")
        favorite_director_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_director_label, 0, 0, 1, 2)   # Row 0, Col 0-1

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
        director_see_all.clicked.connect(lambda: self.see_all_directors( favorite_directors))
        director_labels_layout.addWidget(director_see_all)

        # Create a QWidget to hold the QLabel widgets
        director_labels_widget = QWidget()
        director_labels_widget.setLayout(director_labels_layout)

        # Add the director_labels_widget to your main layout
        layout.addWidget(director_labels_widget, 1, 0)  # Row 1, Col 0

        # Your favorite actor/actress based on the average rating you have given to their movies/series
        favorite_actor_label = QLabel("<h3>Your Favorite Actors/Actresses</h3>")
        favorite_actor_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_actor_label, 2, 0, 1, 2) # Row 2, Col 0-1

        # Get the favorite actor/actress
        favorite_actors = self.get_favorite_actor()

        # Create a QVBoxLayout to add QLabel widgets
        actor_labels_layout = QVBoxLayout()

        # Iterate through the favorite actors and add them to QLabel widgets
        for actor, info in favorite_actors[:5]:
            actor_label = QLabel(f"<b>{actor}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            actor_label.setAlignment(Qt.AlignCenter)
            actor_labels_layout.addWidget(actor_label)

        # Add "See All" button
        actor_see_all = QPushButton("See All")
        # Connect the button click to see_all_actors function
        actor_see_all.clicked.connect(lambda: self.see_all_actors(favorite_actors))
        actor_labels_layout.addWidget(actor_see_all)

        # Create a QWidget to hold the QLabel widgets
        actor_labels_widget = QWidget()
        actor_labels_widget.setLayout(actor_labels_layout)

        # Add the actor_labels_widget to your main layout
        layout.addWidget(actor_labels_widget, 3, 0)  # Row 3, Col 0

        # Your favorite genre based on the average rating you have given to movies/series of that genre
        favorite_genre_label = QLabel("<h3>Your Favorite Genres</h3>")
        favorite_genre_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_genre_label, 0, 2, 1, 2)  # Row 0, Col 2-3

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
        genre_see_all.clicked.connect(lambda: self.see_all_genres(favorite_genres))
        genre_labels_layout.addWidget(genre_see_all)

        # Create a QWidget to hold the QLabel widgets
        genre_labels_widget = QWidget()
        genre_labels_widget.setLayout(genre_labels_layout)

        # Add the genre_labels_widget to your main layout
        layout.addWidget(genre_labels_widget, 1, 2)  # Row 1, Col 2

        # Your favorite TV series based on the average rating you have given to its episodes
        favorite_tv_series_label = QLabel("<h3>Your Favorite TV Shows</h3>")
        favorite_tv_series_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_tv_series_label, 4, 0, 1, 2)  # Row 4, Col 0-1

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
        tv_see_all.clicked.connect(lambda: self.see_all_tv_series(favorite_tv_series))
        tv_labels_layout.addWidget(tv_see_all)

        # Create a QWidget to hold the QLabel widgets
        tv_labels_widget = QWidget()
        tv_labels_widget.setLayout(tv_labels_layout)

        # Add the tv_labels_widget to main layout
        layout.addWidget(tv_labels_widget, 5, 0)    # Row 5, Col 0

        # Your favorite years based on the average rating you have given to movies/series released in that year
        favorite_year_label = QLabel("<h3>Your Favorite Years</h3>")
        favorite_year_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_year_label, 2, 2, 1, 2)  # Row 2, Col 2-3

        # Get the favorite years
        chronological_years, year_stats = self.get_favorite_year(ratings_data)
        print(chronological_years)

        # Create a QVBoxLayout to add QLabel widgets
        year_labels_layout = QVBoxLayout()

        # Iterate through the favorite years and add them to QLabel widgets
        for year, info in year_stats[:5]:
            year_label = QLabel(f"<b>{year}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            year_label.setAlignment(Qt.AlignCenter)
            year_labels_layout.addWidget(year_label)

        # Add "See All" button
        year_see_all = QPushButton("See All")

        # Connect the button click to see_all_years function
        year_see_all.clicked.connect(lambda: self.see_all_years(chronological_years, year_stats))
        year_labels_layout.addWidget(year_see_all)

        # Create a QWidget to hold the QLabel widgets
        year_labels_widget = QWidget()
        year_labels_widget.setLayout(year_labels_layout)

        # Add the year_labels_widget to main layout
        layout.addWidget(year_labels_widget, 3, 2, 1, 2)  # Row 3, Col 2

        # Watchlist statistics
        watchlist_stats_label = QLabel("<h3>Your Watchlist Statistics</h3><br>"
                                       "<b>Top Title Types</b><br>")
        watchlist_stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(watchlist_stats_label, 4, 2, 1, 2)  # Row 4, Col 2-3

        # Get the watchlist statistics
        watchlist_type_stats, watchlist_genre_stats = self.get_watchlist_stats()

        # Create a QVBoxLayout to add QLabel widgets
        watchlist_stats_layout = QVBoxLayout()

        # Iterate through the watchlist statistics and add them to QLabel widgets
        for stat in watchlist_type_stats[:5]:
            watchlist_type_stat_label = QLabel(f"<b>{stat[0]}:</b> {stat[1][0]} ({stat[1][1]:.2f}%)")
            watchlist_type_stat_label.setAlignment(Qt.AlignCenter)
            watchlist_stats_layout.addWidget(watchlist_type_stat_label)

        watchlist_stats_layout.addWidget(QLabel("<br><center><b>Top Genres</b></center><br>"))

        for stat in watchlist_genre_stats[:5]:
            watchlist_genre_stat_label = QLabel(f"<b>{stat[0]}:</b> {stat[1][0]} ({stat[1][1]:.2f}%)")
            watchlist_genre_stat_label.setAlignment(Qt.AlignCenter)
            watchlist_stats_layout.addWidget(watchlist_genre_stat_label)


        # Add "See All" button
        watchlist_stats_see_all = QPushButton("See All")
        # Connect the button click to see_all_watchlist_stats function
        watchlist_stats_see_all.clicked.connect(lambda: self.see_all_watchlist_stats(watchlist_type_stats, watchlist_genre_stats))
        watchlist_stats_layout.addWidget(watchlist_stats_see_all)

        # Create a QWidget to hold the QLabel widgets
        watchlist_stats_widget = QWidget()
        watchlist_stats_widget.setLayout(watchlist_stats_layout)

        # Add the watchlist_stats_widget to your main layout
        layout.addWidget(watchlist_stats_widget, 5, 2)  # Row 5, Col 2

        self.setLayout(layout)

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    def get_favorite_year(self, ratings_data):
        window.update_result_label("Calculating your favorite years...")
        app.processEvents()
        time.sleep(1.5)

        # Create a dictionary to hold the year stats
        year_ratings = {}
        year_title_count = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is not empty
            if item['Title Type'] != "":
                # Extract year and rating
                year = int(item['Year'])
                rating = float(item['Your Rating'])


                # Check if the year is already in the dictionary
                if year in year_ratings:
                    # Add the rating to the existing year
                    year_ratings[year] += rating
                    year_title_count[year] += 1

                else:
                    # Add the year and rating to the dictionary
                    year_ratings[year] = rating
                    year_title_count[year] = 1

        # Check ifthere are any ratings
        if year_ratings:
            # Calculate the average rating for each year
            for year in year_ratings:
                year_ratings[year] /= year_title_count[year]

            # Calculate the love formula for each year
            year_love_formulas = {
                year: (avg_rating, year_title_count[year],
                       ((avg_rating ** 5) * (year_title_count[year] ** 1.3)) / 1000)
                for year, avg_rating in year_ratings.items()
            }

            # Sort the years by ascending order (earliest to latest)
            chronological_years = sorted(year_love_formulas.items(), key=lambda x: x[0])

            # Sort the years by the love_formula in descending order
            best_years = sorted(year_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            # Return the sorted year stats
            return chronological_years, best_years

        else:
            return "N/A"    # Return "N/A" if there are no ratings

    def see_all_years(self, chronological_years, year_stats):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()

        # If there are too many directors, show them in a table
        if year_stats:
            table = SortableTable(len(year_stats), 4)
            table.setHorizontalHeaderLabels(["Year", "Average Rating", "Rated Titles", "Your Love For The Year"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (year, info) in enumerate(year_stats):
                # Convert data to strings
                year_str = str(year)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(year_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

            # Create 3 buttons to see graphs: average rating, title count, love formula
            graph_buttons_layout = QVBoxLayout()

            # Love formula graph
            love_formula_graph_button = QPushButton("Your Favorite Years Graph")
            love_formula_graph_button.clicked.connect(lambda: self.show_love_formula_graph(chronological_years))
            graph_buttons_layout.addWidget(love_formula_graph_button)

            # Average rating graph
            avg_rating_graph_button = QPushButton("Average Rating Per Year Graph")
            avg_rating_graph_button.clicked.connect(lambda: self.show_avg_rating_graph(chronological_years))
            graph_buttons_layout.addWidget(avg_rating_graph_button)

            # Title count graph
            title_count_graph_button = QPushButton("Title Count Per Year Graph")
            title_count_graph_button.clicked.connect(lambda: self.show_title_count_graph(chronological_years))
            graph_buttons_layout.addWidget(title_count_graph_button)

            layout.addLayout(graph_buttons_layout)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def show_love_formula_graph(self, chronological_years):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()
        self.setLayout(layout)

        graph_text_label = QLabel("Hover over the bars to see how much you love each year.")

        # If there are any years, show them in a graph
        if chronological_years:
            # Create a list of years and love formulas
            love_formulas = [year[1][2] for year in chronological_years]

            years = [year[0] for year in chronological_years]

            # Create the figures and the axes
            fig, ax = plt.subplots()

            # Set the title
            ax.set_title("Your Favorite Years")

            # Set the x and y labels
            ax.set_xlabel("Year")
            ax.set_ylabel("Your Love")

            # Set the x and y ticks
            ax.set_xticks(years)
            ax.set_yticks(np.arange(0, max(love_formulas) + 1, max(love_formulas) / 15))

            # Set the x and y limits
            ax.set_xlim(min(years) - 1, max(years) + 1)
            ax.set_ylim(0, max(love_formulas) + 1)

            # Plot the bar chart
            ax.bar(years, love_formulas, color="#FFC107")

            # Rotate the x ticks
            plt.xticks(rotation=60)

            # Add a legend
            ax.legend(["Your Love"])

            # Embed the plot in the dialog
            canvas = plt.gcf().canvas
            canvas.draw()
            plt.close(fig)
            plt.show()
            # Extend into the whole row
            layout.addWidget(canvas)
            # Stretch the canvas to the whole row and column
            layout.setStretch(0, 1)

            # Hover over the bars to see the love formula
            def hover(event):
                # If the mouse is over a bar
                if event.xdata is not None and event.ydata is not None:
                    # Get the position of the cursor
                    cursor_pos = (event.x, event.y)

                    # Get the index of the bar
                    year = int(event.xdata)

                    # Check if the hovered year is in the years list, if yes, get the index of the year in years
                    if year in years:
                        year_index = years.index(year)

                        # Get the love formula of the year
                        love_formula = love_formulas[year_index]

                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\tlove_formula: {love_formula}")

                    # If not, set the love formula to 0
                    else:
                        love_formula = 0

                    graph_text_label.setText(f"Your love for {year}: {love_formula:.2f}")
                    app.processEvents()

            # Connect the hover function to the mouse move event
            canvas.mpl_connect("motion_notify_event", hover)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        layout.addWidget(graph_text_label)
        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def show_avg_rating_graph(self, chronological_years):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()
        self.setLayout(layout)

        graph_text_label = QLabel("Hover over the bars to see the average rating of each year.")

        # If there are any years, show them in a graph
        if chronological_years:
            # Create a list of years and average ratings
            avg_ratings = [year[1][0] for year in chronological_years]

            years = [year[0] for year in chronological_years]

            # Create the figures and the axes
            fig, ax = plt.subplots()

            # Set the title
            ax.set_title("Average Rating Per Year")

            # Set the x and y labels
            ax.set_xlabel("Year")
            ax.set_ylabel("Average Rating")

            # Set the x and y ticks
            ax.set_xticks(years)
            ax.set_yticks(np.arange(0, 11, 1))

            # Set the x and y limits
            ax.set_xlim(min(years) - 1, max(years) + 1)
            ax.set_ylim(0, 11)

            # Plot the bar chart
            ax.bar(years, avg_ratings, color="#FFC107")

            # Rotate the x ticks
            plt.xticks(rotation=60)

            # Add a legend
            ax.legend(["Average Rating"])

            # Embed the plot in the dialog
            canvas = plt.gcf().canvas
            canvas.draw()
            plt.close(fig)
            plt.show()
            # Extend into the whole row
            layout.addWidget(canvas)
            # Stretch the canvas to the whole row and column
            layout.setStretch(0, 1)

            # Hover over the bars to see the average rating
            def hover(event):
                # If the mouse is over a bar
                if event.xdata is not None and event.ydata is not None:
                    # Get the position of the cursor
                    cursor_pos = (event.x, event.y)

                    # Get the index of the bar
                    year = int(event.xdata)

                    # Check if the hovered year is in the years list, if yes, get the index of the year in years
                    if year in years:
                        year_index = years.index(year)

                        # Get the average rating of the year
                        avg_rating = avg_ratings[year_index]

                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\tavg_rating: {avg_rating}")

                    # If not, set the average rating to 0
                    else:
                        avg_rating = 0

                    graph_text_label.setText(f"Average Rating in {year}: {avg_rating:.2f}")
                    app.processEvents()

            # Connect the hover function to the mouse move event
            canvas.mpl_connect("motion_notify_event", hover)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        layout.addWidget(graph_text_label)
        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def show_title_count_graph(self, chronological_years):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()

        graph_text_label = QLabel("Hover over the bars to see the number of titles rated in each year.")

        # If there are any years, show them in a graph
        if chronological_years:
            # Create a list of years and title counts
            title_counts = [year[1][1] for year in chronological_years]

            years = [year[0] for year in chronological_years]

            # Create the figures and the axes
            fig, ax = plt.subplots()

            # Set the title
            ax.set_title("Title Count Per Year")

            # Set the x and y labels
            ax.set_xlabel("Year")
            ax.set_ylabel("Title Count")

            # Set the x and y ticks
            ax.set_xticks(years)
            ax.set_yticks(np.arange(0, max(title_counts) + 1, 1))

            # Set the x and y limits
            ax.set_xlim(min(years) - 1, max(years) + 1)
            ax.set_ylim(0, max(title_counts) + 1)

            # Plot the bar chart
            ax.bar(years, title_counts, color="#FFC107")

            # Rotate the x ticks
            plt.xticks(rotation=60)

            # Add a legend
            ax.legend(["Title Count"])

            # Embed the plot in the dialog
            canvas = plt.gcf().canvas
            canvas.draw()
            plt.close(fig)
            plt.show()

            layout.addWidget(canvas)
            # Stretch the canvas to the whole row and column
            layout.setStretch(0, 1)

            # Hover over the bars to see the title count
            def hover(event):
                # If the mouse is over a bar
                if event.xdata is not None and event.ydata is not None:
                    # Get the index of the bar
                    year = int(event.xdata)

                    # Check if the hovered year is in the years list, if yes, get the index of the year in years
                    if year in years:
                        year_index = years.index(year)

                        # Get the title count of the year
                        title_count = title_counts[year_index]

                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\ttitle_count: {title_count}")

                    # If not, set the title count to 0
                    else:
                        title_count = 0

                    graph_text_label.setText(f"Title Count in {year}: {title_count}")
                    app.processEvents()

            # Connect the hover function to the mouse move event
            canvas.mpl_connect("motion_notify_event", hover)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        layout.addWidget(graph_text_label)
        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def get_watchlist_stats(self):
        window.update_result_label("Calculating your watchlist statistics...")
        app.processEvents()
        time.sleep(1.5)

        # Read the watchlist.csv file into a list
        with open('watchlist.csv', 'r') as file:
            watchlist_data = list(csv.DictReader(file))

        # Calculate the number of movies and series in the watchlist
        movie_count = 0
        series_count = 0
        episode_count = 0
        mini_series_count = 0
        short_count = 0
        tv_movie_count = 0
        tv_special_count = 0
        video_count = 0
        video_game_count = 0
        podcast_count = 0
        podcast_episode_count = 0
        tv_miniseries_count = 0
        tv_short_count = 0
        documentary_count = 0
        music_video_count = 0

        for item in watchlist_data:
            if item['Title Type'] == "movie":
                movie_count += 1
            elif item['Title Type'] == "tvSeries":
                series_count += 1
            elif item['Title Type'] == "tvEpisode":
                episode_count += 1
            elif item['Title Type'] == "tvMiniSeries":
                mini_series_count += 1
            elif item['Title Type'] == "short":
                short_count += 1
            elif item['Title Type'] == "tvMovie":
                tv_movie_count += 1
            elif item['Title Type'] == "tvSpecial":
                tv_special_count += 1
            elif item['Title Type'] == "video":
                video_count += 1
            elif item['Title Type'] == "videoGame":
                video_game_count += 1
            elif item['Title Type'] == "podcastSeries":
                podcast_count += 1
            elif item['Title Type'] == "podcastEpisode":
                podcast_episode_count += 1
            elif item['Title Type'] == "tvMiniSeries":
                tv_miniseries_count += 1
            elif item['Title Type'] == "tvShort":
                tv_short_count += 1
            elif item['Title Type'] == "documentary":
                documentary_count += 1
            elif item['Title Type'] == "musicVideo":
                music_video_count += 1

        title_count = len(watchlist_data)

        # Create a dictionary of title types, their counts and percentages to return
        type_stats = { "Movies": (movie_count, movie_count / title_count * 100),
                          "Series": (series_count, series_count / title_count * 100),
                          "Episodes": (episode_count, episode_count / title_count * 100),
                          "Mini-Series": (mini_series_count, mini_series_count / title_count * 100),
                          "Short Films": (short_count, short_count / title_count * 100),
                          "TV Movies": (tv_movie_count, tv_movie_count / title_count * 100),
                          "TV Specials": (tv_special_count, tv_special_count / title_count * 100),
                          "Videos": (video_count, video_count / title_count * 100),
                          "Video Games": (video_game_count, video_game_count / title_count * 100),
                          "Podcasts": (podcast_count, podcast_count / title_count * 100),
                          "Podcast Episodes": (podcast_episode_count, podcast_episode_count / title_count * 100),
                          "TV Mini-Series": (tv_miniseries_count, tv_miniseries_count / title_count * 100),
                          "TV Shorts": (tv_short_count, tv_short_count / title_count * 100),
                          "Documentaries": (documentary_count, documentary_count / title_count * 100),
                          "Music Videos": (music_video_count, music_video_count / title_count * 100)}

        # Sort the title types by the percentage in descending order
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1][1], reverse=True)

        # Get the count of each individual genre in the watchlist
        genre_count = {}
        for item in watchlist_data:
            if item['Title Type'] == "movie" or item['Title Type'] == "tvSeries" or item['Title Type'] == "tvEpisode"\
                    or item['Title Type'] == "tvMiniSeries" or item['Title Type'] == "short"\
                    or item['Title Type'] == "tvMovie" or item['Title Type'] == "tvSpecial"\
                    or item['Title Type'] == "video" or item['Title Type'] == "videoGame"\
                    or item['Title Type'] == "podcastSeries" or item['Title Type'] == "podcastEpisode"\
                    or item['Title Type'] == "tvMiniSeries" or item['Title Type'] == "tvShort"\
                    or item['Title Type'] == "documentary" or item['Title Type'] == "musicVideo":

                genres = item['Genres'].split(", ")

                for genre in genres:
                    if genre in genre_count:
                        genre_count[genre] += 1
                    else:
                        genre_count[genre] = 1

                # Create a dictionary of genres, their counts and percentages to return
                genre_stats = {genre: (genre_count[genre], genre_count[genre] / title_count * 100) for genre in genre_count}

                # Sort the genres by the percentage in descending order
                sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1][1], reverse=True)

        random_genre = random.choice(sorted_genres)[0]
        random_type = random.choice(sorted_types)[0]
        random_title = random.choice(watchlist_data)['Title']

        jokes_list = [f"Looks like you wanna watch an unhealthy amount of {sorted_genres[0][0]} {sorted_types[0][0]}.",
                      f"{random_genre} {random_type}? An interesting combination.",
                      f"Do you really wanna watch {random_title}? I wouldn't."]

        # Make a joke if there are any titles in the watchlist other than movies, series, episodes and mini-series
        if short_count > 0:
            jokes_list.append(f"You have {short_count} short films in your watchlist.<br><br>You must be a busy person if you want to watch shorts.")
        if tv_movie_count > 0:
            jokes_list.append(f"You have {tv_movie_count} TV movies in your watchlist.<br><br>I hope you know that they are not real movies.")
        if tv_special_count > 0:
            jokes_list.append(f"TV SPECIALS? REALLY? You really have {tv_special_count} TV specials in your watchlist.<br><br>Wow.")
        if video_count > 0:
            jokes_list.append(f"You have {video_count} videos in your watchlist.<br><br>What even is a video? Go on YouTube or whatever if you want to watch videos, dude.")
        if video_game_count > 0:
            jokes_list.append(f"You have {video_game_count} video games in your watchlist. Why do you use IMDB to keep track of your video games?")
        if podcast_count > 0:
            jokes_list.append(f"You have {podcast_count} podcasts in your watchlist.<br><br>I don't know what to say, just don't listen to Andrew Tate and we are good.")
        if podcast_episode_count > 0:
            jokes_list.append(f"You have {podcast_episode_count} podcast episodes in your watchlist.<br><br>I don't know what to say, just don't listen to Andrew Tate and we are good.")
        if documentary_count > 0:
            jokes_list.append(f"You have {documentary_count} documentaries in your watchlist. I hope you are not a flat earther.")
        if music_video_count > 0:
            jokes_list.append(f"You have {music_video_count} music videos in your watchlist. Spotify is just over there, mate.")
        if tv_short_count > 0:
            jokes_list.append(f"You have {tv_short_count} TV shorts in your watchlist.<br><br>Let me guess, you are a busy person and you don't have time to watch full episodes, right?")


        if 'Adult' in genre_count and genre_count['Adult'] > 0:
            jokes_list.append(f"You have {genre_count['Adult']} adult titles in your watchlist.<br><br>Pervert.")
        if 'Reality-TV' in genre_count and genre_count['Reality-TV'] > 0:
            jokes_list.append(f"You have {genre_count['Reality-TV']} reality TV shows in your watchlist.<br><br>"
                              f"I hope you know that they are not real.")
        if 'Talk-Show' in genre_count and genre_count['Talk-Show'] > 0:
            jokes_list.append(f"You have {genre_count['Talk-Show']} talk shows in your watchlist.<br><br>Why?")
        if 'News' in genre_count and genre_count['News'] > 0:
            jokes_list.append(f"You have {genre_count['News']} news shows in your watchlist.<br><br>"
                              f"My brother, you are not missing out on anything, trust me.")
        if 'Game-Show' in genre_count and genre_count['Game-Show'] > 0:
            jokes_list.append(f"You have {genre_count['Game-Show']} game shows in your watchlist.<br><br>"
                              f"I don't know what a game show is, but I am sure it is not a real show.")
        if 'Film-Noir' in genre_count and genre_count['Film-Noir'] > 0:
            jokes_list.append(f"You have {genre_count['Film-Noir']} film noir titles in your watchlist.<br><br>Not everything is black and white, you know??")
        if 'Musical' in genre_count and genre_count['Musical'] > 0:
            jokes_list.append(f"You have {genre_count['Musical']} musicals in your watchlist.<br><br>Are you a theater kid?")
        if 'Music' in genre_count and genre_count['Music'] > 0:
            jokes_list.append(f"You have {genre_count['Music']} music titles in your watchlist.<br><br>")
        if 'Sport' in genre_count and genre_count['Sport'] > 0:
            jokes_list.append(f"You have {genre_count['Sport']} sports titles in your watchlist.<br><br>Okay, I guess?")
        if 'Drama' in genre_count and genre_count['Drama'] > 0:
            jokes_list.append(f"You have {genre_count['Drama']} drama titles in your watchlist.<br><br>Are you a drama queen?")
            jokes_list.append(f"You have {genre_count['Drama']} drama titles in your watchlist.<br><br>"
                              f"Having 'drama' as a genre in your IMDb watchlist is like having 'food' as a cuisine in your restaurant menu: "
                              f"everything is a food and every goddamn movie is a drama.")

        window.update_result_label(random.choice(jokes_list))
        app.processEvents()
        time.sleep(5)

        return sorted_types, sorted_genres

    def see_all_watchlist_stats(self, type_stats, genre_stats):
        # Create a new QDialog to show all the watchlist statistics
        dialog = QDialog()
        dialog.setWindowTitle("Watchlist Statistics")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are any watchlist statistics, show them in two tables in a QHBoxLayout
        if type_stats and genre_stats:
            # Create a QHBoxLayout to add the two tables
            tables_layout = QHBoxLayout()

            # Create a QTableWidget to show the title type statistics
            type_table = QTableWidget()
            type_table.setRowCount(len(type_stats))
            type_table.setColumnCount(2)
            type_table.setHorizontalHeaderLabels(["Title Type", "Count"])
            type_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            type_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            type_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Iterate through the title type statistics and add them to the table
            for row, stat in enumerate(type_stats):
                type_table.setItem(row, 0, QTableWidgetItem(stat[0]))
                type_table.setItem(row, 1, QTableWidgetItem(f"{stat[1][0]} ({stat[1][1]:.2f}%)"))

            # Add the table to the QHBoxLayout
            tables_layout.addWidget(type_table)

            # Create a QTableWidget to show the genre statistics
            genre_table = QTableWidget()
            genre_table.setRowCount(len(genre_stats))
            genre_table.setColumnCount(2)
            genre_table.setHorizontalHeaderLabels(["Genre", "Count"])
            genre_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            genre_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            genre_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Iterate through the genre statistics and add them to the table
            for row, stat in enumerate(genre_stats):
                genre_table.setItem(row, 0, QTableWidgetItem(stat[0]))
                genre_table.setItem(row, 1, QTableWidgetItem(f"{stat[1][0]} ({stat[1][1]:.2f}%)"))

            # Add the table to the QHBoxLayout
            tables_layout.addWidget(genre_table)

            # Add the QHBoxLayout to the QVBoxLayout
            layout.addLayout(tables_layout)

        else:
            no_stats_label = QLabel("You have no titles in your watchlist.")
            layout.addWidget(no_stats_label)

        dialog.setLayout(layout)
        dialog.exec_()

    def get_favorite_director(self, ratings_data):
        window.update_result_label("Calculating your favorite directors...")
        app.processEvents()
        time.sleep(1.5)

        director_ratings = {}
        director_title_counts = {}
        director_titles = {}

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
                    director_titles[director].append(item['Title'])
                else:
                    # Add the director to the dictionary
                    director_ratings[director] = rating
                    director_title_counts[director] = 1
                    director_titles[director] = [item['Title']]


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

            # Select a random director from the dictionary and show it
            random_director = random.choice(list(director_ratings.keys()))

            jokes_list = [f"You have rated {len(director_ratings)} directors.<br><br>That's a lot of directors.",
                          f"I see {random_director} here.<br><br>I wonder if you really like them or you're just pretentious.",
                          f"{random_director}? That's a weird name.",
                          f"{random_director}? We've got a cinephile here, folks!",
                          f"{sorted_directors[0][0]}? I don't know who that is.<br><br>Oops, sorry! They were your favorite director.",
                          f"Do I see {random_director} here? Interesting...",
                          f"{random_director}?! Do you even watch cinema?!",
                          f"Ladies and gentlemen, {random_director}!",
                          f"Do you ever think that your life would be better if {random_director} directed it?<br><br>Me neither."]

            random_title = random.choice(director_titles[random_director])

            jokes_list.extend([f"Do you love {random_director} because of {random_title}?",
                               f"Are you really telling me that you love {random_director} who directed the abomination that is {random_title}?",
                               f"I believe {random_director} is a national treasure and {random_title} is a masterpiece. I am tired of pretending it's not.",
                               f"{random_director} is a great director, but {random_title} is a terrible movie. I am sorry.",
                               f"{random_director} is a terrible director, but {random_title} is a great movie. I am not sorry."])


            if len(director_titles[random_director]) > 1:
                random_title_2 = random.choice([title for title in director_titles[random_director] if title != random_title])
                jokes_list.extend([f"Between {random_title} and {random_title_2}, {random_director} has definitely been kidnapped and replaced by a doppelganger.",
                                   f"Did you know that {random_director} directed both {random_title} and {random_title_2}?<br><br>This isn't a trick question, it's true.",
                                   f"You have 5 seconds: which {random_director} movie is better, {random_title} or {random_title_2}?"])

            if len(director_ratings) > 1:
                random_director_2 = random.choice([director in director_ratings.keys() and director != random_director])
                jokes_list.extend([f"Did you know that {random_director} and {random_director_2} are siblings?<br><br>No, you did not! Because they are not. Probably...",
                                   f"Seems like your dream movie would be directed by {random_director} and {random_director_2}.<br><br>That would be an interesting collab.",
                                   f"Seems like you are a fan of {random_director} and {random_director_2}.<br><br>That's a weird combination, and I love it.",
                                   f"Your range is amazing. You love {random_director} and {random_director_2}.<br><br>That's like loving salt on pineapple. You have to try it to understand."])

            if random_director == "Christopher Nolan":
                nolan_list = ["time", "Hans Zimmer", "Michael Caine", "practical effects"]
                window.update_result_label(f"Seems like you are obsessed with Christopher Nolan as much as Christopher Nolan is obsessed with {random.choice(nolan_list)}.")

            elif random_director == "Quentin Tarantino":
                tarantino_list = ["feet", "N-word", "Uma Thurman", "violence", "70s"]
                window.update_result_label(f"Seems like you are obsessed with Quentin Tarantino as much as Quentin Tarantino is obsessed with {random.choice(tarantino_list)}.")

            elif random_director == "Martin Scorsese":
                scorcese_list = ["gangsters", "Robert De Niro", "Leonardo DiCaprio"]
                window.update_result_label(f"Seems like you are obsessed with Martin Scorsese as much as Martin Scorsese is obsessed with {random.choice(scorcese_list)}.")

            elif random_director == "Stanley Kubrick":
                kubrick_list = ["symmetry", "colors", "the number 42", "the moon"]
                window.update_result_label(f"Seems like you are obsessed with Stanley Kubrick as much as Stanley Kubrick is obsessed with {random.choice(kubrick_list)}.")

            elif random_director == "David Fincher":
                fincher_list = ["the color green", "Trent Reznor"]
                window.update_result_label(f"Seems like you are obsessed with David Fincher as much as David Fincher is obsessed with {random.choice(fincher_list)}.")

            elif random_director == "Steven Spielberg":
                spielberg_list = ["aliens", "John Williams", "the 80s", "dinosaurs", "sharks", "Tom Hanks", "the military"]
                window.update_result_label(f"Seems like you are obsessed with Steven Spielberg as much as Steven Spielberg is obsessed with {random.choice(spielberg_list)}.")

            elif random_director == "Alfred Hitchcock":
                hitchcock_list = ["blondes", "suspense"]
                window.update_result_label(f"Seems like you are obsessed with Alfred Hitchcock as much as Alfred Hitchcock is obsessed with {random.choice(hitchcock_list)}.")

            elif random_director == "Tim Burton":
                burton_list = ["Johnny Depp", "Helena Bonham Carter", "the color black", "stop motion", "Danny Elfman"]
                window.update_result_label(f"Seems like you are obsessed with Tim Burton as much as Tim Burton is obsessed with {random.choice(burton_list)}.")

            elif random_director == "Wes Anderson":
                anderson_list = ["symmetry", "pastel colors", "ensemble casts"]
                window.update_result_label(f"Seems like you are obsessed with Wes Anderson as much as Wes Anderson is obsessed with {random.choice(anderson_list)}.")

            else:
                window.update_result_label(random.choice(jokes_list))
                app.processEvents()
                time.sleep(5)

            return sorted_directors
        else:
            return "N/A"  # Return "N/A" and 0.0 for average rating when there are no ratings

    def see_all_directors(self, favorite_directors):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Directors")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many directors, show them in a table
        if favorite_directors:
            table = SortableTable(len(favorite_directors), 4)
            table.setHorizontalHeaderLabels(["Director", "Average Rating", "Rated Movies", "Your Love For Them"])
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

    def get_favorite_actor(self):
        window.update_result_label("Calculating your favorite actors/actresses...")
        app.processEvents()
        time.sleep(1.5)

        actor_ratings = {}
        actor_title_counts = {}
        actor_titles = {}

        # Get the user lists page from user_preferences.txt
        lists_link, watchlist_link = window.checkPreferences()
        ratings_link = lists_link.replace("lists", "ratings")

        # Send an HTTP GET request to fetch the ratings page
        try:
            # Open the URL
            response = browser.open(ratings_link)

            html_content = response.read()

            # Get the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the movie or TV series details from the list
            movie_details = soup.select('.lister-item-content')

            # Check how many titles are there in the list
            list_details = soup.select(".lister-list-length")
            number_of_titles_str = list_details[0].text.strip()

            # Use a regular expression to extract the integer
            match = re.search(r'\d+', number_of_titles_str)

            if match:
                # The group(0) will contain the first matched integer
                number_of_titles = int(match.group(0))
                window.update_result_label(f"Oh, boy.<br><br>"
                                           f"Found {number_of_titles} titles in your ratings list. That's AT LEAST {number_of_titles} actors/actresses for me to analyze.<br><br>"
                                           f"I may be a robot, but come on...")
                app.processEvents()
                time.sleep(5)

            # Calculate the page count
            page_count = math.ceil(number_of_titles / 100)

            # Append all pages to movie_details
            for page in range(2, page_count + 1):
                window.update_result_label(f"I am {page} layers deep in your ratings and I am too afraid to turn back now!")
                app.processEvents()

                # Find the "NEXT" button at the bottom of the page and extract the link
                next_button = soup.select_one(".lister-page-next")
                next_button_link = next_button['href']

                # Update the ratings_link with the next page link
                ratings_link = f"https://www.imdb.com{next_button_link}"

                try:
                    # Open the URL
                    response = browser.open(ratings_link)

                    # Get the HTML content
                    html_content = response.read()

                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Extract the movie or TV series details from the list
                    movie_details += soup.select('.lister-item-content')

                except mechanize.URLError as e:
                    print(f"An error occurred: {e}")


            # Check if there are any movie details
            if movie_details:
                # Loop through the movie details
                for movie in movie_details:
                    # Get the title
                    title_element = movie.select_one(".lister-item-header a")
                    title = title_element.text.strip()

                    # Extract the title type
                    isEpisode_element = movie.find("small", class_="text-primary")
                    if isEpisode_element:
                        isEpisode = isEpisode_element.text.strip()
                    else:
                        isEpisode = ""

                    # Check if the title type is not an episode
                    if "Episode:" not in isEpisode:
                        # Extract actors and rating
                        # Find the <p> element with directors and actors
                        p_element = movie.select("p.text-muted.text-small a")

                        # Extract the actors from the text of each item in the list
                        actors = [actor.text.strip() for actor in p_element if "dir" not in actor['href']]

                        # Get the rating and directors from ratings.csv and remove directors from actors
                        with open('ratings.csv', 'r') as file:
                            ratings_data = list(csv.DictReader(file))

                            # Loop through the ratings_data list
                            for item in ratings_data:
                                # Check if the title type is "movie"
                                if item['Title Type'] == "movie":
                                    # Extract title and rating
                                    rating = int(item['Your Rating'])

                                    # Check if the title is the same as the current title
                                    if title == item['Title']:
                                        # Extract directors
                                        directors = item['Directors'].split(", ")

                                        # Remove directors from actors
                                        actors = [actor for actor in actors if actor not in directors]

                                        break

                        # Loop through the actors
                        for actor in actors:
                            # Check if the actor is already in the dictionary
                            if actor in actor_ratings:
                                # Add the rating to the existing actor
                                actor_ratings[actor] += rating
                                actor_title_counts[actor] += 1
                                actor_titles[actor].append(title)
                            else:
                                # Add the actor to the dictionary
                                actor_ratings[actor] = rating
                                actor_title_counts[actor] = 1
                                actor_titles[actor] = [title]

                # Select a random actor from the dictionary and show it
                random_actor = random.choice(list(actor_ratings.keys()))
                # Select a random title from the actor's titles
                random_title = random.choice(actor_titles[random_actor])

                # Select a random_actor_2 and random_actor_3 from the dictionary that is different than each other and random_actor
                random_actor_2 = random.choice([actor for actor in actor_ratings.keys() if actor != random_actor])
                random_actor_3 = random.choice([actor for actor in actor_ratings.keys() if actor != random_actor and actor != random_actor_2])


                jokes_list = [
                    f"Are you {random_actor}? Because only a narcissist would rate themselves {actor_ratings[random_actor] / actor_title_counts[actor]}/10 high...",
                    f"I get {random_actor}, but {random_actor} in {random_title}? Really?",
                    f"I can see why you like {random_actor} so much. I mean, I don't, but I can see why you do...",
                    f"I found {random_actor} in your ratings. Should I call the police?",
                    f"Do you have a crush on {random_actor}? I won't tell anyone...",
                    f"I am not sure if I should be impressed or disgusted by your love for {random_actor}...",
                    f"You watched {random_actor} in {actor_title_counts[random_actor]} titles and I don't know what to do with this information...",
                    f"Seems like you have a thing for {random_actor}...",
                    f"Quick, {random_actor} is coming! Act natural!",
                    f"Fuck, Marry, Kill: {random_actor}, {random_actor_2}, {random_actor_3}<br><br>Waiting for your answer...",
                    f"You reaaally like {random_actor}, and you are objectively right!"]

                if len(actor_titles[random_actor]) > 1:
                    # Select random_title_2 from the actor's titles that is different than random_title
                    random_title_2 = random.choice([title for title in actor_titles[random_actor] if title != random_title])
                    jokes_list.extend([f"I loved {random_actor} in {random_title}, but I am not so sure about {random_title_2}...",
                                      f"Quick question: {random_actor} in {random_title} or {random_title_2}?"])

                # Check if the actor has any formal titles, if not take a random joke from the jokes_list
                has_formal_title = False
                for prefix in ["Sir", "Sire", "Dame", "Madam", "Mistress", "Gentleman", "Mistress",
                               "Mrs.", "Ms.", "Miss", "Lord", "Lady", "Esq.", "Esquire",
                               "Excellency", "Honour", "The Honourable"]:
                    if prefix in random_actor:
                        if random_actor == "Sir Ian McKellen":
                            window.update_result_label(f"{random_actor}? I am no Gandalf, but I approve!")
                        else:
                            # Perform your desired action when a match is found
                            window.update_result_label(f"{random_actor}? Looks royal enough for me...")
                            has_formal_title = True
                        break  # Exit the loop after the first match (optional)

                if not has_formal_title:
                    if "Dr." in random_actor:
                        window.update_result_label(f"{random_actor}? I should bring my apple with me to keep them away!")
                    elif "Prof." in random_actor:
                        window.update_result_label(f"{random_actor}? Why is a professor acting? Shouldn't they be teaching?")
                    elif random_actor == "Bryan Cranston":
                        window.update_result_label(f"{random_actor}? I am the one who rates!")
                    elif random_actor == "Bob Odenkirk":
                        window.update_result_label(f"You watch {random_actor} at Starbucks?<br><br>"
                                                   f"I don't get it, what's the kick? Why doncha do it at home like the rest of us, with a big flat-screen TV, 50 channels of pay-per-view?"
                                                   f"In a Starbucks, that's nice!")
                    elif random_actor == "Aaron Paul":
                        window.update_result_label(f"This is my own private {random_actor} and I will not be harassed... Bitch!")
                    elif random_actor == "Dean Norris":
                        window.update_result_label(f"{random_actor}? Sex gifs.")
                    elif random_actor == "Giancarlo Esposito":
                        window.update_result_label(f"I found here a \"{random_actor}\", but I think I can call him Gus.")
                    else:
                        window.update_result_label(random.choice(jokes_list))

                app.processEvents()
                time.sleep(5)

                # Check if there are any ratings
                if actor_ratings:
                    # Calculate the average rating for each actor
                    actor_average_ratings = {
                        actor: actor_ratings[actor] / actor_title_counts[actor]
                        for actor in actor_ratings
                    }

                    # Calculate the love_formula for each actor
                    actor_love_formulas = {
                        actor: (avg_rating, actor_title_counts[actor],
                                   ((avg_rating ** 5) * (actor_title_counts[actor] ** 1.3)) / 1000)
                        for actor, avg_rating in actor_average_ratings.items()
                    }

                    # Sort the actors by the love_formula in descending order
                    sorted_actors = sorted(actor_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

                    return sorted_actors
                else:
                    return "N/A"

        except mechanize.URLError as e:
            print(f"An error occurred: {e}")

    def see_all_actors(self, favorite_actors):
        # Create a new QDialog to show all the actors
        dialog = QDialog()
        dialog.setWindowTitle("All Actors")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many actors, show them in a table
        if favorite_actors:
            table = SortableTable(len(favorite_actors), 4)
            table.setHorizontalHeaderLabels(["Actor", "Average Rating", "Title Count", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (actor, info) in enumerate(favorite_actors):
                # Convert data to strings
                actor_str = str(actor)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(actor_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

        else:
            no_actors_label = QLabel("You have no favorite actors.")
            layout.addWidget(no_actors_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()


    # Get the favorite genre based on the average rating you have given to movies/series of that genre
    def get_favorite_genre(self, ratings_data):
        window.update_result_label("Calculating your favorite genres...")
        app.processEvents()
        time.sleep(1.5)

        genre_ratings = {}
        genre_title_counts = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is not "tvEpisode", since the genre of a TV episode is the genre of the TV series
            if item['Title Type'] != "tvEpisode":
                # Extract genres and rating
                genres = item['Genres'].split(", ")
                rating = float(item['Your Rating'])

                # Loop through the genres
                for genre in genres:
                    # Check if the genre is already in the dictionary
                    if genre in genre_ratings:
                        # Add the rating to the existing genre
                        genre_ratings[genre] += rating
                        genre_title_counts[genre] += 1
                    else:
                        # Add the genre to the dictionary
                        genre_ratings[genre] = rating
                        genre_title_counts[genre] = 1

        # Select a random genre from the dictionary and show it
        random_genre = random.choice(list(genre_ratings.keys()))

        # Find out if the genre starts with a vowel or a consonant
        if random_genre[0].lower() in "aeiou":
            window.update_result_label(f"Seems like we found an {random_genre} lover...")
        else:
            window.update_result_label(f"Seems like we found a {random_genre} lover...")
        app.processEvents()
        time.sleep(5)

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

    def see_all_genres(self, favorite_genres):
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
        window.update_result_label("Calculating your favorite TV series...")
        app.processEvents()
        time.sleep(1.5)

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
                    window.update_result_label(f"Checking out individual episodes such as:<br>"
                                               f"{item['Title']}")
                    app.processEvents()
                    # Format: "Series Name: 'Episode Name: Episode Part'" or "'IP Name: Series Name': Episode Name"
                    # Check the URL to determine which format it is
                    title_url = item['URL']

                    # Get the HTML content of the title URL
                    title_html = requests.get(title_url, headers=headers).text

                    # Create a BeautifulSoup object from the HTML content
                    title_soup = BeautifulSoup(title_html, 'html.parser')

                    # Get the title from the HTML content
                    series_name = title_soup.find("div", class_="bTLVGY").a.text

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

        # Select a random TV series from the dictionary and show it
        random_series = random.choice(list(tv_series_data.keys()))

        jokes_list = [f"How many times have you binge-watched {random_series} already?",
                      f"You sure waste a lot of time watching {random_series}.",
                      f"{random_series}? That's a questionable choice but who am I to judge?",
                      f"I don't think the world is ready for another season of {random_series}.",
                      f"Just between us: I, too, love {random_series}.",
                      f"Apparently you have rated {tv_series_data[random_series]['Episode Count']} episodes of {random_series}.<br><br>That's not at all weird... At all...",
                      f"I am proud of you, unlike your friends who doesn't like {random_series}.",
                      f"I know you watch {random_series} when you are alone. I am always watching you.",
                      f"I know you watch {random_series} because of the nudity. But I'll keep your secret.",
                      f"I am pretty sure you really liked {random_series} since you rated it {tv_series_data[random_series]['Your Rating']}/10.<br><br>"
                      f"But I bet you don't even remember what it was about...",

                      f"I am pretty sure you really liked {random_series} since you rated it {tv_series_data[random_series]['Your Rating']}/10.<br><br>"
                      f"But it might be that you generally rate everything high...",

                      f"Today's kids would think {random_series} is from the history books or something, that's how old you are.",
                      f"Today's kids would think {random_series} is lame.<br><br>I mean it is, but they don't have to know that.",
                      f"If you were a character in {random_series}, you would be the guy walking in the background. You know, the one that no one cares about.",
                      f"I am pretty sure you are the only person in the world who likes {random_series}.",
                      f"I know you watched {random_series} illegally. I am calling the police.",
                      f"If your life was a TV series, it would be {random_series}: boring and uninteresting.",
                      f"If your life was a TV series, it would be {random_series}: horribly cliché and only going downhill after the first episode.<br><br>"
                      f"But I am sure you would rate it 10/10.",

                      f"If your life was a TV series, it would be {random_series}: a complete waste of time.",
                      f"If {random_series} was a person, I am afraid you would run away with them from your own wedding.",
                      f"If {random_series} was a person, I am sure they would kill you and cry at your funeral, that's how awful {random_series} is. But you still like it."]

        if len(tv_series_data.keys()) > 1:
            random_series_2 = random.choice([series for series in tv_series_data.keys() if series != random_series])
            jokes_list.extend([
                f"It's beyond me how you can enjoy BOTH {random_series} and {random_series_2}.",
                f"Quick question: {random_series} or {random_series_2}?",
                f"If {random_series} and {random_series_2} had a baby, it would be the worst thing ever.<br><br>You seem to like both, though...",

                f"Did you know that {random_series} and {random_series_2} were created by the same person?<br><br>"
                f"Well, they weren't. And if you said yes, you are a liar. Be better..."
            ])

        # Check if the title has a number in it
        if any(char.isdigit() for char in random_series):
            # Take the full number from the title
            number = re.search(r'\d+', random_series).group(0)
            window.update_result_label(f"{jokes_list[0]} {number}?!")

        else:
            # Take a random joke from the jokes_list
            joke = random.choice(jokes_list)
            window.update_result_label(f"{joke}")

        app.processEvents()
        time.sleep(5)

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

    def see_all_tv_series(self, favorite_tv_series):
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

class NowWatchingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Now Watching")
        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Show what the user is currently watching
        self.now_watching_label = QLabel("You are now watching:")
        self.now_watching_label.setAlignment(Qt.AlignCenter)
        self.now_watching_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        content_layout.addWidget(self.now_watching_label)

        # Create a list widget to show what the user is currently watching
        self.now_watching_list = QListWidget()
        self.check_now_watching_list()
        self.now_watching_list.setStyleSheet("font-size: 20px;")
        content_layout.addWidget(self.now_watching_list)

        # Create a button to remove the selected title from the list
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_title)
        content_layout.addWidget(self.remove_button)

        # Create a button to clear the list
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_list)
        content_layout.addWidget(self.clear_button)

        # Create a search bar
        self.search_bar = QLineEdit()

        # Create a search button next to the search bar
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search)

        # Create a horizontal layout for the search bar and the search button
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        content_layout.addLayout(search_layout)

        # Create a list widget to show the search results
        self.search_results_list = QListWidget()
        self.search_results_list.setStyleSheet("font-size: 20px;")
        content_layout.addWidget(self.search_results_list)

        # Create a button to add the selected title to the list
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_title)
        content_layout.addWidget(self.add_button)

    # Class Functions
    def check_now_watching_list(self):
        # Check if watching.csv exists
        if os.path.exists("watching.csv"):
            # Open watching.csv and add the titles to the list
            with open("watching.csv", "r") as file:
                for line in file:
                    # Do not add the title if it is "Title"
                    if line.strip("\n") == "Title":
                        continue

                    # Remove the newline character
                    line = line.strip("\n")

                    # Add the title to the list
                    self.now_watching_list.addItem(line)

    def remove_title(self):
        # Check if there are any selected items
        if self.now_watching_list.selectedItems():
            # Loop through the selected items
            for item in self.now_watching_list.selectedItems():
                # Remove the item from the list
                self.now_watching_list.takeItem(self.now_watching_list.row(item))

                # Remove the item from watching.csv, if it exists
                if os.path.exists("watching.csv"):
                    with open("watching.csv", "r") as file:
                        lines = file.readlines()

                    with open("watching.csv", "w") as file:
                        for line in lines:
                            if line.strip("\n") != item.text():
                                file.write(line)

        else:
            # Show a message
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Please select a title to remove.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def clear_list(self):
        # Clear the list
        self.now_watching_list.clear()

        # Clear watching.csv, if it exists
        if os.path.exists("watching.csv"):
            with open("watching.csv", "w") as file:
                file.write("Title\n")


    def search(self):
        # Clear the list
        self.search_results_list.clear()

        # Get the search query
        search_query = self.search_bar.text()

        # Check if the search query is not empty
        if search_query:
            # Perform an IMDB search
            try:
                # Open the URL
                response = browser.open(f"https://www.imdb.com/find?q={search_query}&ref_=nv_sr_sm")

                # Get the HTML content
                html_content = response.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract the titles and their respective links from the search results
                search_results = soup.select("div.sc-17bafbdb-2")
                print(search_results)
                search_results = search_results[0].select("li.ipc-metadata-list-summary-item")

                # Check if there are any search results
                if search_results:
                    # Loop through the search results
                    for result in search_results:
                        # Extract the title
                        title_element = result.select_one("a")
                        title = title_element.text.strip()

                        # Add the title to the list
                        self.search_results_list.addItem(title)

                else:
                    # Show a message
                    self.search_results_list.addItem("No search results found.")

            except mechanize.URLError as e:
                print(f"An error occurred: {e}")

        else:
            # Show a message
            self.search_results_list.addItem("Please enter a search query.")

    def add_title(self):
        # Check if there are any selected items
        if self.search_results_list.selectedItems():
            # Loop through the selected items
            for item in self.search_results_list.selectedItems():
                # Add the item to the list
                self.now_watching_list.addItem(item.text())

            # If watching.csv doesn't exist, create it
            if not os.path.exists("watching.csv"):
                with open("watching.csv", "w") as file:
                    file.write("Title\n")

            # Add the selected title to watching.csv
            with open("watching.csv", "a") as file:
                file.write(f"{item.text()}\n")

        else:
            # Show a message
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Please select a title to add.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()


class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QPixmap)

    def __init__(self, image_url):
        super().__init__()
        self.image_url = image_url

    def run(self):
        # Download the image
        image_data = requests.get(self.image_url).content

        # Convert the image data to QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Emit the signal with the loaded pixmap
        self.image_loaded.emit(pixmap)


class DetailsWindow(QDialog):
    def __init__(self, title_url):
        super().__init__()
        # Access the title's URL
        response = browser.open(title_url)

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the number of awards and nominations (span.ipc-metadata-list-item__list-content-item ::before)
            awards = soup.select_one("div[data-testid='awards']")
            if awards:
                awards = awards.select_one("span", class_="ipc-metadata-list-item__list-content-item").text.strip()
            print(awards)
        else:
            # Get the title from result_label's text's first row
            print("An error occurred while getting the awards and nominations on title")

        # Get certificate ratings and parental guide
        response = browser.open(title_url + "parentalguide")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the certificate ratings
            certificate_ratings_list = []
            certificate_ratings = soup.select_one("section[id='certificates']")

            if certificate_ratings:
                certificate_ratings = certificate_ratings.find("ul" , class_="ipl-inline-list")
                if certificate_ratings:
                    for item in certificate_ratings:
                        item = item.text.strip().replace('\n', '').replace('  ', '')
                        certificate_ratings_list.append(item)

            certificate_ratings_list = [item for item in certificate_ratings_list if item]  # Remove empty strings
            print(certificate_ratings_list)

            # Get the parental guide
            sex_nudity_list = []
            sex_nudity = soup.select_one("section[id='advisory-nudity']")

            if sex_nudity:
                sn_severity = sex_nudity.find("span", class_="ipl-status-pill").text.strip()
                sex_nudity = sex_nudity.find_all("li", class_="ipl-zebra-list__item")
                for item in sex_nudity:
                    sex_nudity_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            print(sex_nudity_list)

            violence_gore_list = []
            violence_gore = soup.select_one("section[id='advisory-violence']")

            if violence_gore:
                violence_severity = violence_gore.find("span", class_="ipl-status-pill").text.strip()
                violence_gore = violence_gore.find_all("li", class_="ipl-zebra-list__item")
                for item in violence_gore:
                    violence_gore_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            print(violence_gore_list)

            profanity_list = []
            profanity = soup.select_one("section[id='advisory-profanity']")

            if profanity:
                profanity_severity = profanity.find("span", class_="ipl-status-pill").text.strip()
                profanity = profanity.find_all("li", class_="ipl-zebra-list__item")
                for item in profanity:
                    profanity_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            print(profanity_list)

            alcohol_drugs_smoking_list = []
            alcohol_drugs_smoking = soup.select_one("section[id='advisory-alcohol']")

            if alcohol_drugs_smoking:
                ad_severity = alcohol_drugs_smoking.find("span", class_="ipl-status-pill").text.strip()
                alcohol_drugs_smoking = alcohol_drugs_smoking.find_all("li", class_="ipl-zebra-list__item")
                for item in alcohol_drugs_smoking:
                    alcohol_drugs_smoking_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            print(alcohol_drugs_smoking_list)

            frightening_intense_scenes_list = []
            frightening_intense_scenes = soup.select_one("section[id='advisory-frightening']")

            if frightening_intense_scenes:
                fis_severity = frightening_intense_scenes.find("span", class_="ipl-status-pill").text.strip()
                frightening_intense_scenes = frightening_intense_scenes.find_all("li", class_="ipl-zebra-list__item")
                for item in frightening_intense_scenes:
                    frightening_intense_scenes_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            print(frightening_intense_scenes_list)

        self.setWindowTitle("Details")
        self.resize(1400, 800)

        self.main_layout = QGridLayout(self, spacing=0)

        # Show certificate ratings
        certificate_widget = QWidget()

        certificate_ratings_label = QLabel("<h2>Certificate Ratings</h2>")
        certificate_list_label = QLabel()
        certificate_list_label.setText(", ".join(certificate_ratings_list))
        certificate_list_label.setStyleSheet("font-size: 18px;")
        certificate_list_label.setWordWrap(True)
        certificate_list_label.hide()

        certificate_button = QPushButton("Show/Hide Certificate Ratings")
        certificate_button.clicked.connect(lambda: certificate_list_label.show() if certificate_list_label.isHidden() else certificate_list_label.hide())

        default_button_stylesheet = certificate_button.styleSheet()

        certificate_label_widget = QWidget()
        certificate_label_widget_layout = QHBoxLayout()
        certificate_label_widget_layout.addWidget(certificate_ratings_label)
        certificate_label_widget_layout.addWidget(certificate_button)
        certificate_label_widget_layout.setAlignment(Qt.AlignLeft)
        certificate_label_widget.setLayout(certificate_label_widget_layout)

        certificate_widget_layout = QVBoxLayout()
        certificate_widget_layout.addWidget(certificate_label_widget)
        certificate_widget_layout.addWidget(certificate_list_label)
        certificate_widget.setLayout(certificate_widget_layout)

        self.main_layout.addWidget(certificate_widget, 0, 0)

        # Show parental guide: Nudity, Violence, Profanity, Alcohol, Drugs & Smoking, Frightening & Intense Scenes
        parental_guide_widget = QWidget()
        parental_guide_label_widget = QWidget()
        parental_guide_label = QLabel("<h2>Parental Guide</h2>")

        # Create a button to show/hide the parental guide
        parental_guide_button = QPushButton("| Show/Hide")
        parental_guide_button.clicked.connect(
            lambda: parental_guide_container.show() if parental_guide_container.isHidden() else parental_guide_container.hide())
        parental_guide_button.setStyleSheet("border: 3px solid black; border-radius: 8px;")


        parental_guide_label_widget_layout = QHBoxLayout()
        parental_guide_label_widget_layout.addWidget(parental_guide_label)
        parental_guide_label_widget_layout.addWidget(parental_guide_button)
        parental_guide_label_widget_layout.setAlignment(Qt.AlignLeft)
        parental_guide_label_widget.setLayout(parental_guide_label_widget_layout)


        # Nudity
        sex_nudity_label = QLabel(f"<h3>Sex & Nudity ({sn_severity})</h3>")
        sex_nudity_list_label = QLabel(f"\t-" + "\n\n\t- ".join(sex_nudity_list))
        sex_nudity_list_label.setStyleSheet("font-size: 18px;")
        sex_nudity_list_label.setWordWrap(True)
        sex_nudity_list_label.hide()

        match(sn_severity):
            case "Severe":
                sex_nudity_label.setStyleSheet("color: red;")
            case "Moderate":
                sex_nudity_label.setStyleSheet("color: orange;")
            case "Mild":
                sex_nudity_label.setStyleSheet("color: green;")

        sex_nudity_label_widget = QWidget()
        sex_nudity_button = QPushButton("| Show/Hide")
        sex_nudity_button.setStyleSheet("border: 2px solid black; border-radius: 8px; font-size: 18px;")
        sex_nudity_label_widget_layout = QHBoxLayout()
        sex_nudity_button.clicked.connect(lambda: sex_nudity_list_label.show() if sex_nudity_list_label.isHidden() else sex_nudity_list_label.hide())
        sex_nudity_label_widget_layout.addWidget(sex_nudity_label)
        sex_nudity_label_widget_layout.addWidget(sex_nudity_button)
        sex_nudity_label_widget_layout.setAlignment(Qt.AlignLeft)
        sex_nudity_label_widget.setLayout(sex_nudity_label_widget_layout)

        # Violence & Gore
        violence_gore_label = QLabel(f"<h3>Violence & Gore ({violence_severity})</h3>")
        violence_gore_list_label = QLabel("\t- " + "\n\n\t- ".join(violence_gore_list))
        violence_gore_list_label.setStyleSheet("font-size: 18px;")
        violence_gore_list_label.setWordWrap(True)
        violence_gore_list_label.hide()

        match(violence_severity):
            case "Severe":
                violence_gore_label.setStyleSheet("color: red;")
            case "Moderate":
                violence_gore_label.setStyleSheet("color: orange;")
            case "Mild":
                violence_gore_label.setStyleSheet("color: green;")

        violence_gore_label_widget = QWidget()
        violence_gore_button = QPushButton("| Show/Hide")
        violence_gore_button.setStyleSheet("border: 2px solid black; border-radius: 8px; font-size: 18px;")
        violence_gore_label_widget_layout = QHBoxLayout()
        violence_gore_button.clicked.connect(
            lambda: violence_gore_list_label.show() if violence_gore_list_label.isHidden() else violence_gore_list_label.hide())
        violence_gore_label_widget_layout.addWidget(violence_gore_label)
        violence_gore_label_widget_layout.addWidget(violence_gore_button)
        violence_gore_label_widget_layout.setAlignment(Qt.AlignLeft)
        violence_gore_label_widget.setLayout(violence_gore_label_widget_layout)

        # Profanity
        profanity_label = QLabel(f"<h3>Profanity ({profanity_severity})</h3>")
        profanity_list_label = QLabel("\t- " + "\n\n\t- ".join(profanity_list))
        profanity_list_label.setStyleSheet("font-size: 18px;")
        profanity_list_label.setWordWrap(True)
        profanity_list_label.hide()

        match(profanity_severity):
            case "Severe":
                profanity_label.setStyleSheet("color: red;")
            case "Moderate":
                profanity_label.setStyleSheet("color: orange;")
            case "Mild":
                profanity_label.setStyleSheet("color: green;")

        profanity_label_widget = QWidget()
        profanity_button = QPushButton("| Show/Hide")
        profanity_button.setStyleSheet("border: 2px solid black; border-radius: 8px; font-size: 18px;")
        profanity_label_widget_layout = QHBoxLayout()
        profanity_button.clicked.connect(
            lambda: profanity_list_label.show() if profanity_list_label.isHidden() else profanity_list_label.hide())
        profanity_label_widget_layout.addWidget(profanity_label)
        profanity_label_widget_layout.addWidget(profanity_button)
        profanity_label_widget_layout.setAlignment(Qt.AlignLeft)
        profanity_label_widget.setLayout(profanity_label_widget_layout)

        # Alcohol, Drugs & Smoking
        alcohol_drugs_smoking_label = QLabel(f"<h3>Alcohol, Drugs & Smoking ({ad_severity})</h3>")
        alcohol_drugs_smoking_list_label = QLabel("\t- " + "\n\n\t- ".join(alcohol_drugs_smoking_list))
        alcohol_drugs_smoking_list_label.setStyleSheet("font-size: 18px;")
        alcohol_drugs_smoking_list_label.setWordWrap(True)
        alcohol_drugs_smoking_list_label.hide()

        match(ad_severity):
            case "Severe":
                alcohol_drugs_smoking_label.setStyleSheet("color: red;")
            case "Moderate":
                alcohol_drugs_smoking_label.setStyleSheet("color: orange;")
            case "Mild":
                alcohol_drugs_smoking_label.setStyleSheet("color: green;")

        alcohol_drugs_smoking_label_widget = QWidget()
        alcohol_drugs_smoking_button = QPushButton("| Show/Hide")
        alcohol_drugs_smoking_button.setStyleSheet("border: 2px solid black; border-radius: 8px; font-size: 18px;")
        alcohol_drugs_smoking_label_widget_layout = QHBoxLayout()
        alcohol_drugs_smoking_button.clicked.connect(
            lambda: alcohol_drugs_smoking_list_label.show() if alcohol_drugs_smoking_list_label.isHidden() else alcohol_drugs_smoking_list_label.hide())
        alcohol_drugs_smoking_label_widget_layout.addWidget(alcohol_drugs_smoking_label)
        alcohol_drugs_smoking_label_widget_layout.addWidget(alcohol_drugs_smoking_button)
        alcohol_drugs_smoking_label_widget_layout.setAlignment(Qt.AlignLeft)
        alcohol_drugs_smoking_label_widget.setLayout(alcohol_drugs_smoking_label_widget_layout)

        # Frightening & Intense Scenes
        frightening_intense_scenes_label = QLabel(f"<h3>Frightening & Intense Scenes ({fis_severity})</h3>")
        frightening_intense_scenes_list_label = QLabel("\t- " + "\n\n\t- ".join(frightening_intense_scenes_list))
        frightening_intense_scenes_list_label.setStyleSheet("font-size: 18px;")
        frightening_intense_scenes_list_label.setWordWrap(True)
        frightening_intense_scenes_list_label.hide()

        match(fis_severity):
            case "Severe":
                frightening_intense_scenes_label.setStyleSheet("color: red;")
            case "Moderate":
                frightening_intense_scenes_label.setStyleSheet("color: orange;")
            case "Mild":
                frightening_intense_scenes_label.setStyleSheet("color: green;")

        frightening_intense_scenes_label_widget = QWidget()
        frightening_intense_scenes_button = QPushButton("| Show/Hide")
        frightening_intense_scenes_button.setStyleSheet("border: 2px solid black; border-radius: 8px; font-size: 18px;")
        frightening_intense_scenes_label_widget_layout = QHBoxLayout()
        frightening_intense_scenes_button.clicked.connect(
            lambda: frightening_intense_scenes_list_label.show() if frightening_intense_scenes_list_label.isHidden() else frightening_intense_scenes_list_label.hide())
        frightening_intense_scenes_label_widget_layout.addWidget(frightening_intense_scenes_label)
        frightening_intense_scenes_label_widget_layout.addWidget(frightening_intense_scenes_button)
        frightening_intense_scenes_label_widget_layout.setAlignment(Qt.AlignLeft)
        frightening_intense_scenes_label_widget.setLayout(frightening_intense_scenes_label_widget_layout)

        # Create a container widget for the parental guide
        parental_guide_container = QWidget()
        parental_guide_container_layout = QVBoxLayout()
        parental_guide_container.hide()

        # Make the parental guide scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(parental_guide_widget)
        scroll_area.setStyleSheet("border: none;")

        parental_guide_container_layout.addWidget(sex_nudity_label_widget)
        parental_guide_container_layout.addWidget(sex_nudity_list_label)
        parental_guide_container_layout.addWidget(violence_gore_label_widget)
        parental_guide_container_layout.addWidget(violence_gore_list_label)
        parental_guide_container_layout.addWidget(profanity_label_widget)
        parental_guide_container_layout.addWidget(profanity_list_label)
        parental_guide_container_layout.addWidget(alcohol_drugs_smoking_label_widget)
        parental_guide_container_layout.addWidget(alcohol_drugs_smoking_list_label)
        parental_guide_container_layout.addWidget(frightening_intense_scenes_label_widget)
        parental_guide_container_layout.addWidget(frightening_intense_scenes_list_label)

        # Create another button at the end of the container in case the parental guide is too long
        parental_guide_button_inner = QPushButton("Show/Hide")
        parental_guide_button_inner.setStyleSheet("border: 3px solid black; border-radius: 8px;")
        parental_guide_button_inner.clicked.connect(
            lambda: parental_guide_container.show() if parental_guide_container.isHidden() else parental_guide_container.hide())

        parental_guide_container_layout.addWidget(parental_guide_button_inner)
        parental_guide_container.setLayout(parental_guide_container_layout)

        parental_guide_widget_layout = QVBoxLayout()
        parental_guide_widget_layout.addWidget(parental_guide_label_widget)
        parental_guide_widget_layout.addWidget(parental_guide_container)
        parental_guide_widget.setLayout(parental_guide_widget_layout)
        self.main_layout.addWidget(scroll_area, 1, 0)

        # Show the awards and nominations
        awards_widget = QWidget()
        awards_label = QLabel(f"<h2>Awards: {awards}</h2>")

        # Create a button to open the awards page
        awards_button = QPushButton("Show Awards && Nominations")
        awards_button.clicked.connect(lambda: webbrowser.open(title_url + "awards"))

        awards_widget_layout = QVBoxLayout()
        awards_widget_layout.addWidget(awards_label)
        awards_widget_layout.addWidget(awards_button)
        awards_widget.setLayout(awards_widget_layout)

        self.main_layout.addWidget(awards_widget, 2, 0)




        # Show the plot
        # Get to summaries page
        response = browser.open(title_url + "plotsummary")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the plot
            plot = soup.select_one("div[data-testid='sub-section-summaries']")
            if plot:
                # Get the list of plot summaries
                plot = plot.select("li[data-testid='list-item']")

                # Get the longest plot summary
                plot = max(plot, key=lambda x: len(x.text.strip()))

                # Get the plot text
                plot = plot.text.strip()

        else:
            print("An error occurred while getting the plot summary")

        plot_widget = QWidget()
        plot_label = QLabel("<h2>Plot</h2>")
        plot_text = QLabel(plot)
        plot_text.setWordWrap(True)

        # Add the plot text to a scroll area
        plot_scroll_area = QScrollArea()
        plot_scroll_area.setWidgetResizable(True)
        plot_scroll_area.setWidget(plot_text)
        plot_scroll_area.setStyleSheet("border: none;")

        plot_widget_layout = QVBoxLayout()
        plot_widget_layout.addWidget(plot_label)
        plot_widget_layout.addWidget(plot_scroll_area)
        plot_widget.setLayout(plot_widget_layout)

        self.main_layout.addWidget(plot_widget, 0, 1)

        # Show the plot keywords
        # Get to plot keywords page
        response = browser.open(title_url + "keywords")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the plot keywords
            plot_keywords = soup.select_one("div[data-testid='sub-section']")
            if plot_keywords:
                # Get the list of plot keywords
                plot_keywords = plot_keywords.select("li[data-testid='list-summary-item']")

                # Get the plot keywords text
                plot_keywords = [keyword.text.strip() for keyword in plot_keywords]

        else:
            print("An error occurred while getting the plot keywords")

        plot_keywords_widget = QWidget()
        plot_keywords_label = QLabel("<h2>Plot Keywords</h2>")
        plot_keywords_text = QLabel("\n".join(plot_keywords))
        plot_keywords_text.setWordWrap(True)

        # Add the plot keywords text to a scroll area
        plot_keywords_scroll_area = QScrollArea()
        plot_keywords_scroll_area.setWidgetResizable(True)
        plot_keywords_scroll_area.setWidget(plot_keywords_text)
        plot_keywords_scroll_area.setStyleSheet("border: none;")

        plot_keywords_widget_layout = QVBoxLayout()
        plot_keywords_widget_layout.addWidget(plot_keywords_label)
        plot_keywords_widget_layout.addWidget(plot_keywords_scroll_area)
        plot_keywords_widget.setLayout(plot_keywords_widget_layout)

        self.main_layout.addWidget(plot_keywords_widget, 1, 1)



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

        self.min_rating = 0.0
        self.max_runtime = 0
        self.selected_genre = "All Genres"
        self.selected_type = "All Types"
        self.max_episodes = 0

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

        now_watching_action = QAction("Now Watching", self)
        now_watching_action.triggered.connect(self.now_watching)

        menu_bar.addAction(statistics_action)
        menu_bar.addAction(now_watching_action)
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

        # Center every item in the combo box
        self.list_combo.setEditable(True)
        self.list_combo.lineEdit().setAlignment(Qt.AlignCenter)

        # Make the combo box searchable
        self.list_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.list_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.main_layout.addWidget(self.list_combo)

        # Create a "Filters" button
        filters_button = QPushButton("Filters", self)
        filters_button.clicked.connect(self.show_filters)
        self.main_layout.addWidget(filters_button)

        # Create a container widget to hold filter widgets
        self.filters_container = QWidget()
        self.filters_container.hide()
        self.main_layout.addWidget(self.filters_container)

        # Create a combo box to select a title type
        self.title_type_combo = QComboBox()
        self.title_type_combo.addItem("All Types")  # Add a default option
        self.title_type_combo.addItems(["Movies", "TV Series", "TV Episodes", "TV Mini-Series", "Shorts", "TV Movies", "TV Specials", "Videos", "Video Games", "Podcasts", "Podcast Episodes", "TV Mini-Series", "TV Shorts", "Documentaries", "Music Videos"])


        # Create a QSlider for selecting minimum IMDB rating
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setMinimum(0)
        self.rating_slider.setMaximum(20)  # To allow 0.5 increments, use 20 instead of 10
        self.rating_slider.setValue(0)  # Default to 0.0
        self.rating_slider.setTickInterval(1)
        self.rating_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QSlider for selecting maximum runtime
        self.runtime_slider = QSlider(Qt.Horizontal)
        self.runtime_slider.setMinimum(0)
        self.runtime_slider.setMaximum(180)  # Maximum runtime is 180 minutes
        self.runtime_slider.setValue(0)  # Default to 0
        self.runtime_slider.setTickInterval(1)
        self.runtime_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QSlider for selecting maximum number of episodes
        self.episodes_slider = QSlider(Qt.Horizontal)
        self.episodes_slider.setMinimum(0)
        self.episodes_slider.setMaximum(100)  # Maximum number of episodes is 100
        self.episodes_slider.setValue(0)  # Default to 0
        self.episodes_slider.setTickInterval(1)
        self.episodes_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QLabel to display the selected rating
        self.rating_label = QLabel("Minimum Rating: No Limit")

        # Create a QLabel to display the selected runtime
        self.runtime_label = QLabel("Maximum Runtime: No Limit")

        # Create a QLabel to display the selected number of episodes
        self.episodes_label = QLabel("Maximum Number of Episodes: No Limit")

        # Update the label when the slider value changes
        self.rating_slider.valueChanged.connect(self.update_rating_label)

        # Update the label when the slider value changes
        self.runtime_slider.valueChanged.connect(self.update_runtime_label)

        # Update the label when the slider value changes
        self.episodes_slider.valueChanged.connect(self.update_episodes_label)

        # Create a QComboBox for selecting genres
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All Genres")  # Add a default option
        # Add genre options to the combo box
        self.genre_combo.addItems(["Action", "Adult", "Adventure", "Animation",
                                   "Biography", "Comedy", "Crime", "Documentary",
                                   "Drama", "Family", "Fantasy", "Film Noir",
                                   "Game Show", "History", "Horror", "Musical",
                                   "Music", "Mystery", "News", "Reality-TV",
                                   "Romance", "Sci-Fi", "Short", "Sport",
                                   "Talk-Show", "Thriller", "War", "Western"])

        # Create a "Apply Filters" button
        apply_filters_button = QPushButton("Apply Filters")
        apply_filters_button.clicked.connect(self.apply_filters)

        # Create a layout for filter widgets
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(self.title_type_combo)
        filter_layout.addWidget(self.genre_combo)
        filter_layout.addWidget(self.rating_label)
        filter_layout.addWidget(self.rating_slider)
        filter_layout.addWidget(self.runtime_label)
        filter_layout.addWidget(self.runtime_slider)
        filter_layout.addWidget(self.episodes_label)
        filter_layout.addWidget(self.episodes_slider)
        filter_layout.addWidget(apply_filters_button)
        self.filters_container.setLayout(filter_layout)

        # Create a new QWidget for displaying the movie/series poster and details, horizontally
        self.poster_widget = QWidget()
        self.poster_layout = QHBoxLayout()
        self.poster_widget.setLayout(self.poster_layout)
        self.main_layout.addWidget(self.poster_widget)

        self.poster_label = QLabel()
        self.poster_label.hide()
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_layout.addWidget(self.poster_label)

        self.result_label = QLabel("Your recommendation will appear here.")
        self.result_label.setWordWrap(True)
        # Enable rich text
        self.result_label.setOpenExternalLinks(True)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.poster_layout.addWidget(self.result_label)

        # Create a new QLabel for displaying the movie/series description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.hide()
        self.main_layout.addWidget(self.description_label)

        # Create a new QPushButton for displaying more details about the movie/series
        self.more_details_button = QPushButton("More About This Title")
        self.more_details_button.clicked.connect(self.more_details)
        self.more_details_button.hide()
        self.main_layout.addWidget(self.more_details_button)

        # Create a QLineEdit for custom IMDB list input
        self.custom_list = QLineEdit()
        self.custom_list.setPlaceholderText("Want to explore a custom list? Paste it here!")
        self.custom_list.setAlignment(Qt.AlignCenter)

        # Create a QPushButton
        search_button = QPushButton("Search")

        # Connect the button's clicked signal to the slot
        search_button.clicked.connect(self.apply_filters)
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

        find_movie_button = QPushButton("Find Something to Watch!")
        find_movie_button.clicked.connect(self.apply_filters)
        find_movie_button.clicked.connect(self.find_random_movie)
        self.main_layout.addWidget(find_movie_button)

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

            # Create watchlist file
            self.watchlist_csv = f'watchlist.csv'

            # Send an HTTP GET request to the URL0
            response = requests.get(dialog.watchlist_link, headers=headers)

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
        # Change the cursor to indicate that the program is working
        QApplication.setOverrideCursor(Qt.WaitCursor)
        selected_index = self.list_combo.currentIndex()

        if selected_index == 0:
            self.update_result_label(0)
            app.processEvents()
            self.watchlist_random(self.watchlist_link, self.min_rating, self.selected_genre, self.max_runtime, self.selected_type, self.max_episodes)

        else:
            self.update_result_label(1)
            app.processEvents()
            selected_list_link = self.list_links[selected_index - 1]
            self.list_random(selected_list_link, self.min_rating, self.selected_genre, self.max_runtime, self.selected_type, self.max_episodes)

        # Change the cursor back to normal
        self.poster_label.show()
        self.result_label.setAlignment(Qt.AlignVCenter)
        self.description_label.show()
        self.more_details_button.show()
        QApplication.restoreOverrideCursor()

    def list_random(self, list_url, min_rating, selected_genre, max_runtime, selected_type, max_episodes):
        number_of_episodes = 0

        # If the user has selected a maximum number of episodes and not selected a title type, search only through TV series
        if max_episodes != 0 and selected_type == "All Types":
            self.update_result_label(3)
            app.processEvents()
            selected_type = "tvSeries"

        # If the user has selected a maximum number of episodes and a title type, respect the title type
        elif max_episodes != 0 and (selected_type == "tvSeries" or selected_type == "tvMiniSeries" or selected_type == "podcastSeries"):
            self.update_result_label(3)
            app.processEvents()
            selected_type = selected_type

        # If the user selected a title type other than any series, this overrides the episode filter
        else:
            self.update_result_label(3)
            app.processEvents()
            max_episodes = 0

        list_url = list_url + f"?sort=list_order,asc&st_dt=&mode=detail"

        if selected_type != "All Types":
            self.update_result_label(3)
            app.processEvents()
            list_url = list_url + f"&title_type={selected_type}"

        # Send an HTTP GET request to fetch the list page
        response = requests.get(list_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            self.update_result_label(7)
            app.processEvents()

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the movie or TV series details from the list
            movie_details = soup.select('.lister-item-content')

            # Check how many titles are there in the list
            list_details = soup.select(".lister-total-num-results")
            if list_details:
                number_of_titles_str = list_details[0].text.strip()

            else:
                list_details = soup.find_all("div.lister-details")
                print(list_details)
                number_of_titles_str = list_details[0].text.strip()

            # Use a regular expression to extract the integer
            match = re.search(r'\d+', number_of_titles_str)
            if match:
                # The group(0) will contain the first matched integer
                number_of_titles = int(match.group(0))

            # Calculate the page count
            page_count = math.ceil(number_of_titles / 100)


            # Append all pages to movie_details
            for page in range(2, page_count + 1):
                # Use regex to remove referral parameters
                list_url_without_referral = re.sub(r'[?&]ref_[^&]*', '', list_url)
                print(f"{list_url_without_referral}&page={page}")

                # Send an HTTP GET request to fetch the list page
                response = requests.get(f"{list_url_without_referral}&page={page}", headers=headers)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract the movie or TV series details from the list
                    movie_details += soup.select('.lister-item-content')

                else:
                    print("\nThere was a problem while retrieving the list. Check the URL and try again.")
                    return

            # Check if there are any movie details
            if movie_details:
                self.update_result_label(3)
                app.processEvents()

                # Filter movie details based on min_rating and selected_genre
                filtered_movie_details = []
                for movie_detail in movie_details:
                    imdb_rating = movie_detail.find('span', class_='ipl-rating-star__rating')
                    if imdb_rating:
                        imdb_rating = float(imdb_rating.text.strip())
                    else:
                        imdb_rating = 0.0

                    genres = movie_detail.find('span', class_='genre')
                    if genres:
                        genres = genres.text.strip()
                    else:
                        genres = "-"

                    runtime = movie_detail.find('span', class_='runtime')
                    if runtime:
                        runtime = runtime.text.strip()

                        # Check if runtime has decimal separator
                        if "." in runtime or "," in runtime:
                            runtime = runtime.replace(",", "")
                            runtime = runtime.replace(".", "")

                        runtime = runtime.split(" ")[0]

                    else:
                        runtime = 0

                    if imdb_rating >= min_rating and (selected_genre == "All Genres" or selected_genre in genres) and (max_runtime == 0 or int(runtime) <= max_runtime):
                        filtered_movie_details.append(movie_detail)

                # Check if there are any filtered movie details
                if filtered_movie_details:
                    self.update_result_label(4)
                    app.processEvents()

                    # Randomly select a movie detail from the list
                    random_movie_detail = random.choice(filtered_movie_details)

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
                        self.update_result_label(5)
                        app.processEvents()

                        # Parse the HTML content of the page
                        second_soup = BeautifulSoup(second_response.content, 'html.parser')

                        # Extract the movie or TV series details from the list
                        type_details = second_soup.select("div.sc-e6498a88-0")
                        if type_details:
                            title_type = type_details[0].select_one('li.ipc-inline-list__item[role="presentation"]').text.strip()

                        if title_type.isdigit():
                            title_type = "Movie"

                        # If the title is not a TV series, do not get the number of episodes
                        if title_type == "TV Series" or title_type == "TV Mini-Series":
                            episode_details = second_soup.find('span', class_='ipc-title__subtext')

                            if episode_details:
                                number_of_episodes = int(episode_details.text.strip())

                        else:
                            number_of_episodes = 0

                        # Check if the number of episodes is less than or equal to the selected maximum number of episodes
                        if max_episodes != 0:
                            # If the number of episodes is greater than the selected maximum number of episodes, try again until the list ends or a title matches the criteria
                            if number_of_episodes > max_episodes:
                                self.update_result_label(6)
                                app.processEvents()
                                for i in range(0, len(filtered_movie_details)):
                                    random_movie_detail = random.choice(filtered_movie_details)
                                    title = random_movie_detail.find('h3', class_='lister-item-header').find('a').text.strip()
                                    url = 'https://www.imdb.com' + random_movie_detail.find('h3', class_='lister-item-header').find('a')['href']
                                    second_response = requests.get(url, headers=headers)
                                    second_soup = BeautifulSoup(second_response.content, 'html.parser')
                                    type_details = second_soup.select("div.iwmAVw")
                                    if type_details:
                                        title_type = type_details[0].select_one('li.ipc-inline-list__item[role="presentation"]').text.strip()
                                    if title_type.isdigit():
                                        title_type = "Movie"
                                    if title_type == "TV Series" or title_type == "TV Mini-Series":
                                        episode_details = second_soup.find('span', class_='ipc-title__subtext')
                                        if episode_details:
                                            number_of_episodes = int(episode_details.text.strip())
                                    else:
                                        number_of_episodes = 0
                                    if number_of_episodes <= max_episodes:
                                        break

                                # If the number of episodes is still greater than the selected maximum number of episodes, show an error message
                                if number_of_episodes > max_episodes:
                                    self.result_label.setText(f"No title matches your criteria. Try again with different filters.")
                                    return

                        director_details = second_soup.select("div.ipc-metadata-list-item__content-container")

                        if director_details:
                            directors = director_details[0].select_one("a.ipc-metadata-list-item__list-content-item--link").text.strip()

                        description_details = second_soup.select("span.sc-466bb6c-0")

                        if description_details:
                            description = description_details[0].text.strip()
                            self.description_label.setText(f"{description}")

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
                            if self.check_favorites(title):
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
                            self.star_icon_label.mousePressEvent = lambda event: self.save_favorite(title, url)

                    else:
                        print("\nFailed to retrieve the list. Check the URL and try again.")

                    imdb_rating = random_movie_detail.find('span', class_='ipl-rating-star__rating').text.strip()
                    runtime = random_movie_detail.find('span', class_='runtime').text.strip()
                    year = random_movie_detail.find('span', class_='lister-item-year').text.strip()
                    genres = random_movie_detail.find('span', class_='genre').text.strip()
                    user_rating = self.checkRatings(title, title_type)

                    # Update self.result_label with the recommendation
                    self.result_label.setText(f"<a href=\"{url}\"><h1>{title}</h1></a><br>"
                                              f"<b>Title Type:</b> {title_type}<br>"
                                              f"<b>IMDb Rating:</b> {imdb_rating}<br>"
                                              f"<b>Runtime:</b> {runtime}<br>"
                                              f"<b>Episode Count:</b> {number_of_episodes}<br>"
                                              f"<b>Year:</b> {year}<br>"
                                              f"<b>Genres:</b> {genres}<br>"
                                              f"<b>Director/Creator:</b> {directors}<br><br>"
                                              f"{user_rating}")

                else:
                    # If there are no filtered movie details, show an error message
                    self.result_label.setText("No title matches your criteria. Try again with different filters.")

                    # Reset the poster_label
                    self.poster_label.clear()

            else:
                # If there are no movie details, show an error message
                self.result_label.setText("No title matches your criteria. Try again with different filters.")
        else:
            self.result_label.setText(f"Failed to retrieve the list. Check the URL and try again.")
            return

    ## IF A WATCHLIST, DOWNLOAD THE CSV FILE AND SELECT A MOVIE/SERIES RANDOMLY ##
    def watchlist_random(self, url, min_rating, selected_genre, max_runtime, selected_type, max_episodes):
        # If there are any episode filters, call list_random() instead
        if max_episodes != 0:
            # Delete 'export' from the URL
            url = url.replace("export", "")
            self.list_random(url, min_rating, selected_genre, max_runtime, selected_type, max_episodes)
            return

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
            self.update_result_label(3)
            app.processEvents()

            # Filter the CSV data by minimum rating, maximum runtime and selected genre
            csv_data = [item for item in csv_data if 'IMDb Rating' in item and item['IMDb Rating'] and float(item['IMDb Rating']) >= min_rating]

            if selected_genre != "All Genres":
                csv_data = [item for item in csv_data if selected_genre in item['Genres']]

            if max_runtime != 0:
                csv_data = [item for item in csv_data if 'Runtime (mins)' in item and item['Runtime (mins)'] and int(item['Runtime (mins)']) <= max_runtime]

            if selected_type != "All Types":
                csv_data = [item for item in csv_data if selected_type in item['Title Type']]

            # Check if there's data in the CSV file after filtering
            if csv_data:
                self.update_result_label(4)
                app.processEvents()
                # Randomly select a row from the CSV data
                random_item = random.choice(csv_data)

                # Check if the user has rated the movie/series before
                user_rating = self.checkRatings(random_item['Title'], random_item['Title Type'])

                # To get the title type and the poster, we need to scrape the movie's/series' own page
                # Send an HTTP GET request to fetch the list page
                second_response = requests.get(random_item['URL'], headers=headers)

                # Check if the request was successful
                if second_response.status_code == 200:
                    self.update_result_label(5)
                    app.processEvents()
                    # Parse the HTML content of the page
                    second_soup = BeautifulSoup(second_response.content, 'html.parser')

                    director_details = second_soup.select("div.ipc-metadata-list-item__content-container")
                    if director_details:
                        directors = random_item['Directors'] if random_item['Directors'] != "" else director_details[0].select_one("a.ipc-metadata-list-item__list-content-item--link").text.strip()

                    # If the title is not a TV series, do not get the number of episodes
                    if random_item["Title Type"] == "tvSeries" or random_item["Title Type"] == "tvMiniSeries":
                        episode_details = second_soup.find('span', class_='ipc-title__subtext')

                        if episode_details:
                            number_of_episodes = int(episode_details.text.strip())

                    else:
                        number_of_episodes = 0

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

                            elif self.theme == "dark":
                                self.star_color = "white"
                                self.change_star_color(self.star_color)

                        self.star_icon_label = QLabel(self.poster_label)
                        self.star_icon_label.setPixmap(self.star_icon_pixmap)
                        self.star_icon_label.move(10, 10)
                        self.star_icon_label.show()

                        # When clicked, save the movie/series' title and URL to a CSV file name "favorites.csv" and change the color of the star icon to yellow
                        # When clicked again, remove the movie/series from the CSV file and change the color of the star icon to white or black depending on the theme
                        self.star_icon_label.mousePressEvent = lambda event: self.save_favorite(random_item['Title'], random_item['URL'])

                    description_details = second_soup.select("span.sc-466bb6c-0")

                    if description_details:
                        description = description_details[0].text.strip()
                        self.description_label.setText(f"{description}")

                    # Extract and print the desired columns
                    self.result_label.setText(f"<a href=\"{random_item['URL']}\"><h1>{random_item['Title']}</h1></a><br>"
                                              f"<b>Title Type:</b> {random_item['Title Type']}<br>"
                                              f"<b>IMDb Rating:</b> {random_item['IMDb Rating']}<br>"
                                              f"<b>Runtime:</b> {random_item['Runtime (mins)']}<br>"
                                              f"<b>Episode Count:</b> {number_of_episodes}<br>"
                                              f"<b>Year:</b> {random_item['Year']}<br>"
                                              f"<b>Genres:</b> {random_item['Genres']}<br>"
                                              # Use csv to get the directors, if empty, use the scraped data
                                              f"<b>Director/Creator:</b> {directors}<br><br>"
                                              f"{user_rating}")

                else:
                    print("\nFailed to retrieve the list. Check the URL and try again.")

            else:
                # If there are no filtered movie details, show an error message
                self.result_label.setText(f"No title matches your criteria. Try again with different filters.")

                # Reset the poster_label
                self.poster_label.clear()
                print("The CSV file is empty.")
                return


    ## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
    def checkRatings(self, title, title_type):


        # Define the destination file path where you want to save the CSV file
        self.ratings_csv = 'ratings.csv'

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

    # Get more details about the movie/series
    def more_details(self):
        # Get the title URL from the result_label
        title_url = self.result_label.text().split("<a href=\"")[1].split("\"><h1>")[0]

        # Create a new window to display the details
        self.details_window = DetailsWindow(title_url)
        self.details_window.show()


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
            if self.theme == "light" and self.star_color == "yellow":
                self.star_color = "black"
                self.change_star_color(self.star_color)
            elif self.theme == "dark" and self.star_color == "yellow":
                self.star_color = "white"
                self.change_star_color(self.star_color)

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
        self.star_color = "yellow"
        self.change_star_color(self.star_color)


    # Check if the movie/series is already in the favorites.csv file
    def check_favorites(self, title):
        # Define the destination file path where you want to save the CSV file
        self.favorites_csv = 'favorites.csv'

        # Check if the file exists
        if not os.path.isfile(self.favorites_csv):
            print("'favorites.csv' does not exist.")
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
        self.update_result_label(2)
        app.processEvents()

        # Get the text from the QLineEdit
        list_link = self.custom_list.text()

        # Call the list_random function with the input
        self.list_random(list_link, self.min_rating, self.selected_genre, self.max_runtime, self.selected_type, self.max_episodes)

    def show_filters(self):
        if self.filters_container.isHidden():
            self.filters_container.show()
        else:
            self.filters_container.hide()

    def apply_filters(self):
        # Retrieve selected minimum rating and genre
        self.min_rating = self.rating_slider.value() / 2.0
        self.selected_genre = self.genre_combo.currentText()
        self.max_runtime = self.runtime_slider.value()
        self.max_episodes = self.episodes_slider.value()

        if self.title_type_combo.currentText() != "All Types":
            match(self.title_type_combo.currentText()):
                case "Movies":
                    self.selected_type = "movie"
                case "TV Series":
                    self.selected_type = "tvSeries"
                case "TV Episodes":
                    self.selected_type = "tvEpisode"
                case "TV Mini-Series":
                    self.selected_type = "tvMiniSeries"
                case "Shorts":
                    self.selected_type = "short"
                case "TV Movies":
                    self.selected_type = "tvMovie"
                case "TV Specials":
                    self.selected_type = "tvSpecial"
                case "Videos":
                    self.selected_type = "video"
                case "Video Games":
                    self.selected_type = "videoGame"
                case "Podcasts":
                    self.selected_type = "podcastSeries"
                case "Podcast Episodes":
                    self.selected_type = "podcastEpisode"
                case "TV Mini-Series":
                    self.selected_type = "tvMiniSeries"
                case "TV Shorts":
                    self.selected_type = "tvShort"
                case "Documentaries":
                    self.selected_type = "documentary"
                case "Music Videos":
                    self.selected_type = "musicVideo"

        # Display the applied filters
        self.result_label.setText(f"<h3>Applied Filters:</h3><br>"
                                  f"Type: {self.title_type_combo.currentText()}<br>"
                                  f"Minimum Rating: {self.min_rating}<br>"
                                  f"Genre: {self.selected_genre}<br>"
                                  f"Maximum Runtime: {self.max_runtime}<br>"
                                  f"Maximum Episodes: {self.max_episodes}")

        # Hide the filters container after applying filters
        self.filters_container.hide()

    # Update the rating label when the slider value changes
    def update_rating_label(self):
        if self.rating_slider.value() == 0:
            self.rating_label.setText(f"Minimum Rating: No Limit")
        else:
            self.rating_label.setText(f"Minimum Rating: {self.rating_slider.value() / 2.0}")

    # Update the runtime label when the slider value changes
    def update_runtime_label(self):
        if self.runtime_slider.value() == 0:
            self.runtime_label.setText(f"Maximum Runtime: No Limit")
        else:
            self.runtime_label.setText(f"Maximum Runtime: {self.runtime_slider.value()}")

    # Update the episodes label when the slider value changes
    def update_episodes_label(self):
        if self.episodes_slider.value() == 0:
            self.episodes_label.setText(f"Maximum Episodes: No Limit")
        else:
            self.episodes_label.setText(f"Maximum Episodes: {self.episodes_slider.value()}")

    # Update the result label to inform the user that the program is working
    def update_result_label(self, flag):
        match(flag):
            case 0:
                self.result_label.setText("Our chefs are crafting a watchlist recommendation for you...<br><br>")
                return
            case 1:
                self.result_label.setText("We're preparing a delightful recommendation from your list...<br><br>")
                return
            case 2:
                self.result_label.setText("A custom recommendation is on its way, tailored just for you...<br><br>")
                return
            case 3:
                self.result_label.setText("Our chefs are adding filters to enhance your selection's flavor...<br><br>")
                return
            case 4:
                self.result_label.setText("We're handpicking a special title for you...<br><br>")
                return
            case 5:
                self.result_label.setText("Your perfect dish is ready to be served! Enjoy your meal!<br><br>")
                return
            case 6:
                self.result_label.setText("Creating a culinary masterpiece takes time. Please be patient!<br><br>")
                return
            case 7:
                self.result_label.setText("We're curating a special menu just for you...<br><br>")
                return
            case _:
                self.result_label.setText(flag)



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

        if self.star_color != "yellow" or self.star_color == "white":
            self.star_color = "black"
            self.change_star_color(self.star_color)

    # Change the theme to dark
    def dark_theme(self):
        app.setPalette(dark_palette)
        self.theme == "dark"

        if self.star_color != "yellow" or self.star_color == "black":
            self.star_color = "white"
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

        # Change the cursor to a wait cursor
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create and display the statistics dialog
        statistics_window = StatisticsWindow(ratings_csv_data)
        statistics_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()



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
                    "<h3>Version 3.6.5</h3>"
                    "<b>Created by:</b> İbrahim Soner İNAN<br><br>"
                    "<a href='https://github.com/isonerinan'>GitHub</a><br><br>"
                    "<a href='https://www.linkedin.com/in/isonerinan'>LinkedIn</a><br><br>"
                    "<a href='https://www.instagram.com/isonerinan'>Instagram</a><br><br>"
                    "<a href='https://www.twitter.com/isonerinan'>Twitter</a>")
        msg.exec_()

    # Show the now watching dialog
    def now_watching(self):
        # Create and display the now watching dialog
        now_watching_window = NowWatchingWindow()
        now_watching_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

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
    app.setFont(QFont("Roboto"))

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
