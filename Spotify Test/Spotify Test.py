import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from dotenv import load_dotenv  # Make sure to install the python-dotenv package

# Load environment variables from file
load_dotenv('credentials.env')

# Get environment variables (You have to create a Spotify app and get your own credentials)
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

# Initialize the Spotify API client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                              scope='playlist-read-private'))


# Function to get all playlist tracks and their details
def get_all_playlist_tracks(playlist_id):
    tracks = []
    offset = 0
    limit = 100  # Maximum number of tracks to retrieve per request

    while True:
        results = sp.playlist_items(playlist_id, offset=offset, limit=limit)
        if not results['items']:
            break
        for item in results['items']:
            track = item['track']
            tracks.append({
                'Track Name': track['name'],
                'Artist(s)': ', '.join([artist['name'] for artist in track['artists']]),
                'Album': track['album']['name'],
                'Release Date': track['album']['release_date'],
                'Popularity': track['popularity'],
                'Duration (ms)': track['duration_ms'],
                'Genres': ', '.join([genre for genre in sp.artist(track['artists'][0]['uri'])['genres']]),
            })

        offset += limit

    return tracks


# Function to analyze a playlist
def analyze_playlist(playlist_id):
    playlist = sp.playlist(playlist_id)
    playlist_name = playlist['name']
    print(f'Analyzing playlist: {playlist_name}')

    tracks = get_all_playlist_tracks(playlist_id)

    # Create a DataFrame from the tracks data
    df = pd.DataFrame(tracks)

    # Analyze and print some statistics
    num_tracks = len(df)
    total_popularity = df['Popularity'].sum()
    average_popularity = df['Popularity'].mean()
    average_duration = df['Duration (ms)'].mean()
    top_release_date = df['Release Date'].value_counts().idxmax()
    # Sum the years and divide by the number of tracks to get the average year (note: this is a weighted average)
    average_release_date = df['Release Date'].apply(lambda x: int(x[:4])).sum() / num_tracks
    top_genres = df['Genres'].value_counts().idxmax()

    print(f'Number of tracks: {num_tracks}')
    print(f'Total popularity score: {total_popularity}')
    print(f'Average popularity score: {average_popularity:.2f}%')
    print(f'Average duration: {int(average_duration / 60000)}:{int(average_duration / 1000 % 60)}')
    print(f'Most common release year: {top_release_date}')
    print(f'Average release year: {average_release_date:.2f}')
    print(f'Most common genres: {top_genres}')

    # You can perform more analysis on the DataFrame here

    # Optionally, you can save the DataFrame to a CSV file
    df.to_csv(f'{playlist_name}_analysis.csv', index=False)
    print(f'Analysis saved to {playlist_name}_analysis.csv')


if __name__ == "__main__":
    # Replace 'your_playlist_id' with the ID of the playlist you want to analyze
    playlist_id = input("Enter playlist URL: ")
    analyze_playlist(playlist_id)
