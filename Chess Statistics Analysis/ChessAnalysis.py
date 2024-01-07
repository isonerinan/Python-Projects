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
    #print(response.text)

    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        try:
            games = [json.loads(line) for line in response.text.split('\n') if line.strip()]
            #print("Successfully fetched games!")
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

    if len(rapid_games) == 0:
        print("No rapid games found.")
        return {"rapid_games": 0, "rapid_wins": 0, "rapid_draws": 0, "rapid_losses": 0}

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

    rapid_win_percentage = rapid_wins / len(rapid_games) * 100
    rapid_loss_percentage = rapid_losses / len(rapid_games) * 100
    rapid_draw_percentage = rapid_draws / len(rapid_games) * 100

    print(f"Rapid Games: {len(rapid_games)}")
    print(f"Rapid Wins: {rapid_wins} ({rapid_win_percentage:.2f}%)")
    print(f"Rapid Losses: {rapid_losses} ({rapid_loss_percentage:.2f}%)")
    print(f"Rapid Draws: {rapid_draws} ({rapid_draw_percentage:.2f}%)")

    return {"rapid_games": len(rapid_games), "rapid_wins": rapid_wins, "rapid_draws": rapid_draws, "rapid_losses": rapid_losses}

def stats_blitz(games, username):
    blitz_wins = 0
    blitz_losses = 0
    blitz_draws = 0
    blitz_win_percentage = 0
    blitz_loss_percentage = 0
    blitz_draw_percentage = 0

    blitz_games = [game for game in games if game["speed"] == "blitz"]

    if len(blitz_games) == 0:
        print("No blitz games found.")
        return {"blitz_games": 0, "blitz_wins": 0, "blitz_draws": 0, "blitz_losses": 0}

    for game in blitz_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                blitz_wins += 1
            elif game["winner"] != user_color:
                blitz_losses += 1

        except:
            blitz_draws += 1

    blitz_win_percentage = blitz_wins / len(blitz_games) * 100
    blitz_loss_percentage = blitz_losses / len(blitz_games) * 100
    blitz_draw_percentage = blitz_draws / len(blitz_games) * 100

    print(f"Blitz Games: {len(blitz_games)}")
    print(f"Blitz Wins: {blitz_wins} ({blitz_win_percentage:.2f}%)")
    print(f"Blitz Losses: {blitz_losses} ({blitz_loss_percentage:.2f}%)")
    print(f"Blitz Draws: {blitz_draws} ({blitz_draw_percentage:.2f}%)")

    return {"blitz_games": len(blitz_games), "blitz_wins": blitz_wins, "blitz_draws": blitz_draws, "blitz_losses": blitz_losses}

def stats_bullet(games, username):
    bullet_wins = 0
    bullet_losses = 0
    bullet_draws = 0
    bullet_win_percentage = 0
    bullet_loss_percentage = 0
    bullet_draw_percentage = 0

    bullet_games = [game for game in games if game["speed"] == "bullet"]

    if len(bullet_games) == 0:
        print("No bullet games found.")
        return {"bullet_games": 0, "bullet_wins": 0, "bullet_draws": 0, "bullet_losses": 0}

    for game in bullet_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                bullet_wins += 1
            elif game["winner"] != user_color:
                bullet_losses += 1

        except:
            bullet_draws += 1

    bullet_win_percentage = bullet_wins / len(bullet_games) * 100
    bullet_loss_percentage = bullet_losses / len(bullet_games) * 100
    bullet_draw_percentage = bullet_draws / len(bullet_games) * 100

    print(f"Bullet Games: {len(bullet_games)}")
    print(f"Bullet Wins: {bullet_wins} ({bullet_win_percentage:.2f}%)")
    print(f"Bullet Losses: {bullet_losses} ({bullet_loss_percentage:.2f}%)")
    print(f"Bullet Draws: {bullet_draws} ({bullet_draw_percentage:.2f}%)")

    return {"bullet_games": len(bullet_games), "bullet_wins": bullet_wins, "bullet_draws": bullet_draws, "bullet_losses": bullet_losses}

def stats_classical(games, username):
    classical_wins = 0
    classical_losses = 0
    classical_draws = 0
    classical_win_percentage = 0
    classical_loss_percentage = 0
    classical_draw_percentage = 0

    classical_games = [game for game in games if game["speed"] == "classical"]

    if len(classical_games) == 0:
        print("No classical games found.")
        return {"classical_games": 0, "classical_wins": 0, "classical_draws": 0, "classical_losses": 0}

    for game in classical_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                classical_wins += 1
            elif game["winner"] != user_color:
                classical_losses += 1

        except:
            classical_draws += 1

    classical_win_percentage = classical_wins / len(classical_games) * 100
    classical_loss_percentage = classical_losses / len(classical_games) * 100
    classical_draw_percentage = classical_draws / len(classical_games) * 100

    print(f"Classical Games: {len(classical_games)}")
    print(f"Classical Wins: {classical_wins} ({classical_win_percentage:.2f}%)")
    print(f"Classical Losses: {classical_losses} ({classical_loss_percentage:.2f}%)")
    print(f"Classical Draws: {classical_draws} ({classical_draw_percentage:.2f}%)")

    return {"classical_games": len(classical_games), "classical_wins": classical_wins, "classical_draws": classical_draws, "classical_losses": classical_losses}

def stats_correspondence(games, username):
    correspondence_wins = 0
    correspondence_losses = 0
    correspondence_draws = 0
    correspondence_win_percentage = 0
    correspondence_loss_percentage = 0
    correspondence_draw_percentage = 0

    correspondence_games = [game for game in games if game["speed"] == "correspondence"]

    if len(correspondence_games) == 0:
        print("No correspondence games found.")
        return {"correspondence_games": 0, "correspondence_wins": 0, "correspondence_draws": 0, "correspondence_losses": 0}

    for game in correspondence_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                correspondence_wins += 1
            elif game["winner"] != user_color:
                correspondence_losses += 1

        except:
            correspondence_draws += 1

    correspondence_win_percentage = correspondence_wins / len(correspondence_games) * 100
    correspondence_loss_percentage = correspondence_losses / len(correspondence_games) * 100
    correspondence_draw_percentage = correspondence_draws / len(correspondence_games) * 100

    print(f"Correspondence Games: {len(correspondence_games)}")
    print(f"Correspondence Wins: {correspondence_wins} ({correspondence_win_percentage:.2f}%)")
    print(f"Correspondence Losses: {correspondence_losses} ({correspondence_loss_percentage:.2f}%)")
    print(f"Correspondence Draws: {correspondence_draws} ({correspondence_draw_percentage:.2f}%)")

    return {"correspondence_games": len(correspondence_games), "correspondence_wins": correspondence_wins, "correspondence_draws": correspondence_draws, "correspondence_losses": correspondence_losses}

def stats_ultrabullet(games, username):
    ultrabullet_wins = 0
    ultrabullet_losses = 0
    ultrabullet_draws = 0
    ultrabullet_win_percentage = 0
    ultrabullet_loss_percentage = 0
    ultrabullet_draw_percentage = 0

    ultrabullet_games = [game for game in games if game["speed"] == "ultrabullet"]

    if len(ultrabullet_games) == 0:
        print("No ultrabullet games found.")
        return {"ultrabullet_games": 0, "ultrabullet_wins": 0, "ultrabullet_draws": 0, "ultrabullet_losses": 0}

    for game in ultrabullet_games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                ultrabullet_wins += 1
            elif game["winner"] != user_color:
                ultrabullet_losses += 1

        except:
            ultrabullet_draws += 1

    ultrabullet_win_percentage = ultrabullet_wins / len(ultrabullet_games) * 100
    ultrabullet_loss_percentage = ultrabullet_losses / len(ultrabullet_games) * 100
    ultrabullet_draw_percentage = ultrabullet_draws / len(ultrabullet_games) * 100

    print(f"Ultrabullet Games: {len(ultrabullet_games)}")
    print(f"Ultrabullet Wins: {ultrabullet_wins} ({ultrabullet_win_percentage:.2f}%)")
    print(f"Ultrabullet Losses: {ultrabullet_losses} ({ultrabullet_loss_percentage:.2f}%)")
    print(f"Ultrabullet Draws: {ultrabullet_draws} ({ultrabullet_draw_percentage:.2f}%)")

    return {"ultrabullet_games": len(ultrabullet_games), "ultrabullet_wins": ultrabullet_wins, "ultrabullet_draws": ultrabullet_draws, "ultrabullet_losses": ultrabullet_losses}

def stats_all(games, username):
    wins = 0
    losses = 0
    draws = 0
    win_percentage = 0
    loss_percentage = 0
    draw_percentage = 0

    if len(games) == 0:
        print("No games found.")
        return {"games": 0, "wins": 0, "draws": 0, "losses": 0}

    for game in games:
        if game["players"]["white"]["user"]["name"] == username:
            user_color = "white"
        elif game["players"]["black"]["user"]["name"] == username:
            user_color = "black"

        try:
            if game["winner"] == user_color:
                wins += 1
            elif game["winner"] != user_color:
                losses += 1

        except:
            draws += 1

    win_percentage = wins / len(games) * 100
    loss_percentage = losses / len(games) * 100
    draw_percentage = draws / len(games) * 100

    print(f"All Games: {len(games)}")
    print(f"Wins: {wins} ({win_percentage:.2f}%)")
    print(f"Losses: {losses} ({loss_percentage:.2f}%)")
    print(f"Draws: {draws} ({draw_percentage:.2f}%)")

    return {"games": len(games), "wins": wins, "draws": draws, "losses": losses}


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

    # Main loop
    while True:
        if lichess_games is not None:
            # Ask the user for their desired stats
            print("Which stats would you like to see?"
                  "\n1. All"
                  "\n2. Rapid"
                  "\n3. Blitz"
                  "\n4. Bullet"
                  "\n5. Classical"
                  "\n6. Correspondence"
                  "\n7. Ultrabullet"
                  "\n8. Exit")
            stats_choice = input("Enter the number of your choice: ")

            match(stats_choice):
                case "1":
                    stats_all(lichess_games, lichess_username)
                case "2":
                    stats_rapid(lichess_games, lichess_username)
                case "3":
                    stats_blitz(lichess_games, lichess_username)
                case "4":
                    stats_bullet(lichess_games, lichess_username)
                case "5":
                    stats_classical(lichess_games, lichess_username)
                case "6":
                    stats_correspondence(lichess_games, lichess_username)
                case "7":
                    stats_ultrabullet(lichess_games, lichess_username)
                case "8":
                    break
                case _:
                    print("Invalid choice. Please try again.")

        else:
            print("No Lichess games found.")
            break

if __name__ == "__main__":
    main()
