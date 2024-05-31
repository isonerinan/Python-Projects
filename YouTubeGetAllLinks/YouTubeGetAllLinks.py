# Python code to retrieve all video links from a YouTube channel, including shorts

import requests
import re
import json

# Function to retrieve all video links from a YouTube channel, including shorts
def get_playlists(user_id):
    # Define the base URL for the YouTube Data API
    base_url = "https://www.googleapis.com/youtube/v3/channels"

    # Define the parameters for the API request
    params = {
        "key": "AIzaSyDp0XVmXH5viKBlMxlf2hbqJrAiDVM5VjQ",
        "id": user_id,
        "part": "contentDetails"
    }



    # Make the API request to retrieve the channel's content details
    response = requests.get(base_url, params=params)
    data = response.json()

    print(data)

    # Extract the playlist ID from the response
    playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Define the base URL for the YouTube Data API to retrieve playlist items
    playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"

    # Define the parameters for the API request to retrieve playlist items
    playlist_params = {
        "key": "AIzaSyDp0XVmXH5viKBlMxlf2hbqJrAiDVM5VjQ",
        "playlistId": playlist_id,
        "maxResults": "50",
        "part": "snippet"
    }

    # Make the API request to retrieve the playlist items, if there are more than 50 videos in the playlist, you can use the nextPageToken to retrieve the next page of results
    video_links = []

    while True:
        response = requests.get(playlist_url, params=playlist_params)
        data = response.json()

        for item in data["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            video_links.append(video_link)

        if "nextPageToken" in data:
            playlist_params["pageToken"] = data["nextPageToken"]
        else:
            break

    return video_links

# Example usage
user_id = "UCZyzVES_TmEsSIjsb6Vytpw"
video_links = get_playlists(user_id)
for link in video_links:
    print(link)