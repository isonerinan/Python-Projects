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

def download_chess_com_game_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "User-Agent": f"username: {username}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        archives = response.json()["archives"]
        return archives
    else:
        print(f"Failed to fetch game archives. Status code: {response.status_code}")
        return None

def download_chess_com_games_from_archive(archive_url, username):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": f"username: {username}"
        }

    response = requests.get(archive_url, headers=headers)

    if response.status_code == 200:
        games = response.json()
        return games
    else:
        print(f"Failed to fetch games from archive. Status code: {response.status_code}")
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

def stats_rapid_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_blitz_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_bullet_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_classical_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_correspondence_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_ultrabullet_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        return

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

def stats_all_lichess(games, username, account_choice):
    # Check if the user wants to see stats for Lichess
    if account_choice != 1 and account_choice != 2:
        print(account_choice != 1 and account_choice != 2)
        return

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

def download_lichess_games(lichess_username, lichess_token, account_choice):
    # Check if the user wants to download games from Lichess.org
    if account_choice != 1 and account_choice != 2:
        return

    print("Downloading games from Lichess.org.")
    # Retrieve and process games from Lichess.org
    lichess_games = get_lichess_games(lichess_username, lichess_token)
    save_games(lichess_games, lichess_username + "_lichess")

    lichess_game_count = len(lichess_games)
    print(f"Total games (Lichess): {lichess_game_count}")
def download_chess_com_games(chess_com_username, account_choice):
    # Check if the user wants to download games from Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    print("Downloading games from Chess.com.")
    # Retrieve and process games from Chess.com
    archives = download_chess_com_game_archives(chess_com_username)

    if archives is not None:
        chess_com_games = {"games": []}

        for archive_url in archives:
            # Download games from the archive
            temp_games = download_chess_com_games_from_archive(archive_url, chess_com_username)

            # Append games to the list in temp_games
            chess_com_games["games"].extend(temp_games["games"])

        # Save the merged games to a file
        save_games(chess_com_games, chess_com_username + "_chess_com")

        chess_com_game_count = len(chess_com_games["games"])
        print(f"Total games (Chess.com): {chess_com_game_count}")

    else:
        print("No archives found.")

def stats_all_chess_com(chess_com_games, chess_com_username, account_choice):
    # Check if the user wants to see stats for Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    pass

def stats_rapid_chess_com(chess_com_games, chess_com_username, account_choice):
    # Check if the user wants to see stats for Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    pass

def stats_blitz_chess_com(chess_com_games, chess_com_username, account_choice):
    # Check if the user wants to see stats for Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    pass

def stats_bullet_chess_com(chess_com_games, chess_com_username, account_choice):
    # Check if the user wants to see stats for Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    pass

def stats_daily_chess_com(chess_com_games, chess_com_username, account_choice):
    # Check if the user wants to see stats for Chess.com
    if account_choice != 1 and account_choice != 3:
        return

    pass


def main():
    load_dotenv()

    # Replace these with your actual usernames and tokens
    lichess_username = os.getenv("LICHESS_USERNAME")
    lichess_token = os.getenv("LICHESS_API_TOKEN")
    chess_com_username = os.getenv("CHESS_COM_USERNAME")

    # Main loop
    while True:
        # Ask the user which account they want to see stats for
        print("Which account would you like to see stats for?"
              "\n1. All accounts"
              "\n2. Lichess"
              "\n3. Chess.com"
              "\n4. Exit")
        account_choice = int(input("Enter the number of your choice: "))

        if account_choice == 1 or account_choice == 2 or account_choice == 3:
            download_lichess_games(lichess_username, lichess_token, account_choice)
            download_chess_com_games(chess_com_username, account_choice)
            try:
                print("Loading Lichess games...")
                lichess_games = load_games(lichess_username + "_lichess")
            except:
                print("No Lichess games found.")

            try:
                print("Loading Chess.com games...")
                chess_com_games = load_games(chess_com_username + "_chess_com")
            except:
                print("No Chess.com games found.")


        elif account_choice == 4:
            quit()

        else:
            print("Invalid choice. Please try again.")
            continue

        # Inner loop
        while True:
            # Ask the user for their desired stats
            print("Which stats would you like to see?"
                  "\n1. All"
                  "\n2. Rapid"
                  "\n3. Blitz"
                  "\n4. Bullet"
                  "\n5. Classical (Lichess only)"
                  "\n6. Correspondence/Daily"
                  "\n7. Ultrabullet (Lichess only)"
                  "\n8. Change accounts"
                  "\n9. Exit")
            stats_choice = int(input("Enter the number of your choice: "))

            match (stats_choice):
                case 1:
                    stats_all_lichess(lichess_games, lichess_username, account_choice)
                    stats_all_chess_com(chess_com_games, chess_com_username, account_choice)
                case 2:
                    stats_rapid_lichess(lichess_games, lichess_username, account_choice)
                    stats_rapid_chess_com(chess_com_games, chess_com_username, account_choice)
                case 3:
                    stats_blitz_lichess(lichess_games, lichess_username, account_choice)
                    stats_blitz_chess_com(chess_com_games, chess_com_username, account_choice)
                case 4:
                    stats_bullet_lichess(lichess_games, lichess_username, account_choice)
                    stats_bullet_chess_com(chess_com_games, chess_com_username, account_choice)
                case 5:
                    stats_classical_lichess(lichess_games, lichess_username, account_choice)
                case 6:
                    stats_correspondence_lichess(lichess_games, lichess_username, account_choice)
                    stats_daily_chess_com(chess_com_games, chess_com_username, account_choice)
                case 7:
                    stats_ultrabullet_lichess(lichess_games, lichess_username, account_choice)
                case 8:
                    break
                case 9:
                    quit()
                case _:
                    print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
