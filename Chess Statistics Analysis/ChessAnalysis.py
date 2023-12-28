import os
import requests
from dotenv import load_dotenv
import json

def get_lichess_games(username, token):
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/x-ndjson"}
    parameters = {"rated": "true", "pgnInJson": "true", "clocks":"true", "evals":"true", "opening":"true"}

    response = requests.get(url, headers=headers, params=parameters)

    # Print the raw response content
    print(response.text)

    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        try:
            games = [json.loads(line) for line in response.text.split('\n') if line.strip()]
            print("Successfully fetched games!")
            return games
        except Exception as e:
            print(f"Failed to process NDJSON. Error: {e}")
            return None
    else:
        print(f"Failed to fetch games. Status code: {response.status_code}")
        return None

def calculate_elo_change(game, username):
    if game["players"]["white"]["user"]["name"] == username:
        return game["players"]["white"]["ratingDiff"]
    elif game["players"]["black"]["user"]["name"] == username:
        return game["players"]["black"]["ratingDiff"]
    else:
        return 0  # Return 0 if the username is not found in the game

def save_games(games, username):
    with open(f"games_{username}.json", "w") as f:
        json.dump(games, f)

def load_games(username):
    with open(f"games_{username}.json", "r") as f:
        games = json.load(f)
        return games

def stats_rapid(games, username):
    rapid_wins = 0
    rapid_losses = 0
    rapid_draws = 0
    rapid_win_percentage = 0
    rapid_loss_percentage = 0
    rapid_draw_percentage = 0

    rapid_games = [game for game in games if game["speed"] == "rapid"]

    for game in rapid_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                rapid_wins += 1
            elif game["winner"] != user_color:
                rapid_losses += 1

        except:
            rapid_draws += 1

    rapid_win_percentage = rapid_wins / len(rapid_games)
    rapid_loss_percentage = rapid_losses / len(rapid_games)
    rapid_draw_percentage = rapid_draws / len(rapid_games)

    print(f"Rapid Games: {len(rapid_games)}")
    print(f"Rapid Wins: {rapid_wins} ({rapid_win_percentage}%)")
    print(f"Rapid Losses: {rapid_losses} ({rapid_loss_percentage}%)")
    print(f"Rapid Draws: {rapid_draws} ({rapid_draw_percentage}%)")



def main():
    load_dotenv()

    # Replace these with your actual usernames and tokens
    lichess_username = os.getenv("LICHESS_USERNAME")
    lichess_token = os.getenv("LICHESS_API_TOKEN")

    # Retrieve and process games from Lichess.org
    lichess_games = get_lichess_games(lichess_username, lichess_token)
    save_games(lichess_games, lichess_username)

    game_count = len(lichess_games)
    print(f"Total games: {game_count}")

    counter = 0

    if lichess_games is not None:
        print("\nLichess.org Games:")
        for game in lichess_games:
            elo_change = calculate_elo_change(game, lichess_username)
            print(f"Game ID: {game['id']}, Elo Change: {elo_change}")
            counter += 1
            print(f"Game {counter} of {game_count}")

    stats_rapid(lichess_games, lichess_username)

if __name__ == "__main__":
    main()
