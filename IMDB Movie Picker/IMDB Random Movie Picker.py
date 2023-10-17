import requests
from bs4 import BeautifulSoup
import csv
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}


### Function Definitions ###
## IF A REGULAR LIST, SCRAPE THE WEB PAGE AND SELECT A MOVIE/SERIES RANDOMLY ##
def list_random(list_link):
    # Define the URL of your IMDb list
    list_url = list_link

    # Send an HTTP GET request to fetch the list page
    response = requests.get(list_url, headers = headers)

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
            second_response = requests.get(url, headers = headers)

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


            else:
                print("\nFailed to retrieve the list. Check the URL and try again.")

            imdb_rating = random_movie_detail.find('span', class_='ipl-rating-star__rating').text.strip()
            runtime = random_movie_detail.find('span', class_='runtime').text.strip()
            year = random_movie_detail.find('span', class_='lister-item-year').text.strip()
            genres = random_movie_detail.find('span', class_='genre').text.strip()

            # Print the extracted information
            print(f"\nTitle: {title}")
            print(f"URL: {url}")
            print(f"Title Type: {title_type}")
            print(f"IMDb Rating: {imdb_rating}")
            print(f"Runtime: {runtime}")
            print(f"Year: {year}")
            print(f"Genres: {genres}")
            print(f"Director/Creator: {directors}")

            checkRatings(title, title_type)

        else:
            print("\nNo movie details found on the list page. Check the HTML structure or the URL.")
    else:
        print("\nFailed to retrieve the list. Check the URL and try again.")
        return


## IF A WATCHLIST, DOWNLOAD THE CSV FILE AND SELECT A MOVIE/SERIES RANDOMLY ##
def watchlist_random():
    # URL of the IMDb watchlist export page
    url = 'https://www.imdb.com/list/ls507767575/export'

    # Define the destination file path where you want to save the CSV file
    watchlist_csv = 'watchlist.csv'

    # Send an HTTP GET request to the URL0
    response = requests.get(url, headers = headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the content of the response
        content = response.text

        # Save the content to the destination file
        with open(watchlist_csv, 'w', encoding='utf-8') as file:
            file.write(content)
    else:
        print("\nFailed to download the CSV file. Check the URL or make sure your watchlist is public and try again.")
        return

    # Read the CSV file and store its data in a list of dictionaries
    csv_data = []
    with open(watchlist_csv, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            csv_data.append(row)

    # Check if there's data in the CSV file
    if csv_data:
        # Randomly select a row from the CSV data
        random_item = random.choice(csv_data)

        # Extract and print the desired columns
        print(f"\nTitle: {random_item['Title']}")
        print(f"URL: {random_item['URL']}")
        print(f"Title Type: {random_item['Title Type']}")
        print(f"IMDb Rating: {random_item['IMDb Rating']}")
        print(f"Runtime (mins): {random_item['Runtime (mins)']}")
        print(f"Year: {random_item['Year']}")
        print(f"Genres: {random_item['Genres']}")
        print(f"Release Date: {random_item['Release Date']}")
        print(f"Director/Creator: {random_item['Directors']}")

        checkRatings(random_item['Title'], random_item['Title Type'])


    else:
        print("The CSV file is empty.")
        return


## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
def checkRatings(title, title_type):
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
                print(f"\nYou have rated {title_type} '{title}' with a rating of {your_rating}/10 on {date_rated}.")
                return  # Exit the function once a match is found

        # If no match is found, print a message
        print(f"\nYou have not rated {title_type} '{title}'.")

    else:
        print("The CSV file is empty.")
        return


###########################################################################################################
###########################################################################################################

status = 0

## ASK USER TO PICK A LIST
while True:

    # Replace this URL with the IMDb user lists URL
    url = 'https://www.imdb.com/user/ur135017478/lists'

    # Send an HTTP GET request to fetch the IMDb user lists page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all list names
        list_items = soup.find_all('li', class_='ipl-zebra-list__item user-list')

        # Pythons lists to store IMDB list names and links
        list_names = []
        list_links = []

        print("0. Watchlist")

        for index, item in enumerate(list_items, start=1):
            list_name = item.find('a', class_='list-name').text.strip()
            list_names.append(list_name)
            href = item.find('a', class_='list-name')['href']  # href attributes look like "/list/ls561499946/"
            list_link = f'https://www.imdb.com{href}'  # Construct the full link
            list_links.append(list_link)
            print(f"{index}. {list_name}")

        # Ask the user to input an integer to choose a list
        selected_index = input(f"Enter the number of the IMDb list (\"Q\" to try another list): ")

        if selected_index.lower() == "q":
            status = 2
            selected_list_link = input("Enter the URL of the list: ")

            custom_response = requests.get(selected_list_link, headers=headers)
            # Check if the request was successful
            if custom_response.status_code == 200:
                # Parse the HTML content of the page
                custom_soup = BeautifulSoup(custom_response.content, 'html.parser')

                # Extract the movie or TV series details from the list
                selected_list_name = custom_soup.select_one('.list-name').text.strip()

            print(f"selected list: {selected_list_name}")
            list_random(selected_list_link)

        elif 0 <= int(selected_index) <= len(list_items):
            if int(selected_index) == 0:
                status = 0
                watchlist_random()
            else:
                status = 1
                selected_list_name = list_names[int(selected_index) - 1]
                selected_list_link = list_links[int(selected_index) - 1]
                print(f"selected list: {selected_list_name}")
                list_random(selected_list_link)
        else:
            print("Invalid input.")

    else:
        print("Failed to retrieve the IMDb user lists page. Check the URL and try again.")


    ## ASK USER IF THEY WANT ANOTHER RECOMMENDATION
    while True:
        if status == 0:
            retry = input("\nDidn't like it? Press any key to get another recommendation from your watchlist."
                          "\nPress 0 to select another list."
                          "\nPress \"Q\" to quit.\n")

            if retry.lower() == "q":
                raise SystemExit

            elif retry == "0":
                break

            else:
                watchlist_random()

        elif status == 1:
            retry = input(f"\nDidn't like it? Press any key to get another recommendation from {selected_list_name}."
                          "\nPress 0 to select another list."
                          "\nPress \"Q\" to quit.\n")

            if retry.lower() == "q":
                raise SystemExit

            elif retry == "0":
                break

            else:
                list_random(selected_list_link)

        elif status == 2:
            retry = input(f"\nDidn't like it? Press any key to get another recommendation from {selected_list_name}."
                          "\nPress 0 to select another list."
                          "\nPress \"Q\" to quit.\n")

            if retry.lower() == "q":
                raise SystemExit

            elif retry == "0":
                break

            else:
                list_random(selected_list_link)