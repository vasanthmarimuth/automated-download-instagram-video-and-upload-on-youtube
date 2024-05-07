import instaloader
import os
import shutil
import csv
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Function to download the Nth video from Instagram
def download_nth_instagram_video(profile_name, n):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, profile_name)

    posts = profile.get_posts()
    count = 0

    for post in posts:
        if post.is_video:
            count += 1
            if count == n:
                L.download_post(post, target=profile_name)
                print(f"Video {n} downloaded successfully.")
                break

    if count < n:
        print(f"This profile has less than {n} videos.")

# Function to get the first line from a text file with specific encoding
def get_first_line_from_text_file(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as text_file:
        first_line = text_file.readline().strip()  # Read the first line and remove any leading/trailing whitespace
    return first_line

# Function to check if a line exists in the CSV file
def line_exists_in_csv(text_line, csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if text_line in row:
                return True
    return False

# Function to write the first line from the text file into a CSV file if the line doesn't exist in the CSV file
def write_if_line_not_in_csv(txt_file_path, csv_file_path):
    text_first_line = get_first_line_from_text_file(txt_file_path)

    if not line_exists_in_csv(text_first_line, csv_file_path):
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([text_first_line])
            print("First line from the text file has been written to the CSV file.")

            # Upload video to YouTube
            video_path = os.path.join(os.path.dirname(txt_file_path), os.path.splitext(os.path.basename(txt_file_path))[0] + ".mp4")
            video_title, video_description = get_video_info_from_text_file(txt_file_path)
            upload_video(video_path, video_title, video_description)

def get_video_info_from_text_file(txt_file_path):
    video_title, video_description = "", ""
    with open(txt_file_path, 'r', encoding='utf-8') as text_file:
        lines = text_file.readlines()
        video_title = lines[0].strip()
        video_description = lines[1].strip() if len(lines) > 1 else ""
    return video_title, video_description

# Function to authenticate with YouTube API
def authenticate():
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    CLIENT_SECRETS_FILE = "client_secrets.json"  # Your client secrets file

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Function to upload a video to YouTube
def upload_video(video_file, title, description):
    credentials = authenticate()

    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": title,
            "description": description
        },
        "status": {
            "privacyStatus": "public"  # Set the privacy status to public
        }
    }

    try:
        response = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=video_file
        ).execute()

        print("Video upload successful! Video ID:", response['id'])
        return True

    except HttpError as e:
        print("An HTTP error occurred:", e)
        return False

# Set Instagram profile and the Nth video to download
profile_name = "channel_name"
nth_video = "video_number"

# Download Nth video from Instagram
download_nth_instagram_video(profile_name, nth_video)

# Process the downloaded folder
downloaded_folder_path = profile_name
txt_files_list = [f for f in os.listdir(downloaded_folder_path) if f.endswith('.txt')]

if txt_files_list:
    for file in txt_files_list:
        txt_file_path = os.path.join(downloaded_folder_path, file)
        csv_file_path = 'files/output_csv_file.csv'  # Replace this with your CSV file path

        write_if_line_not_in_csv(txt_file_path, csv_file_path)

        # Delete the downloaded folder after processing
        shutil.rmtree(os.path.abspath(downloaded_folder_path))
else:
    print("No .txt files found in the specified directory.")
