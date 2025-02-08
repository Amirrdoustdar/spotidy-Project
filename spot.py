from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import defaultdict
import re
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Spotify API Configuration
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Email Configuration
EMAIL_USER = os.getenv("EMAIL_USER")  # Your email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Your email password or app-specific password
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtp.gmail.com")  # SMTP server (e.g., smtp.gmail.com)
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))  # SMTP port (e.g., 587 for TLS)

# Check required Spotify credentials
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    print("❌ Missing Spotify API credentials! Set SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI as environment variables.")
    exit(1)

# Check required Email credentials
if not EMAIL_USER or not EMAIL_PASSWORD:
    print("❌ Missing email credentials! Set EMAIL_USER and EMAIL_PASSWORD as environment variables.")
    exit(1)

# Extract Playlist ID from URL
def extract_playlist_id(link):
    pattern = r'playlist/([a-zA-Z0-9]+)'
    match = re.search(pattern, link)
    return match.group(1) if match else None

# Fetch Playlist Tracks with Caching
def get_playlist_tracks(sp, playlist_id):
    tracks = []
    try:
        results = sp.playlist_tracks(playlist_id)
        while results:
            tracks.extend(results['items'])
            if results['next']:
                results = sp.next(results)
            else:
                break
    except Exception as e:
        print(f"❌ Error fetching playlist tracks: {e}")
        return []
    return tracks

# Analyze Duplicate Tracks
def analyze_duplicates(tracks):
    track_counter = defaultdict(int)
    duplicates = {}
    
    for item in tracks:
        track = item.get('track')
        if not track or 'name' not in track or 'artists' not in track:
            continue  # Skip invalid or removed tracks
        
        key = f"{track['name']} - {track['artists'][0]['name']}"
        track_counter[key] += 1
    
    for track, count in track_counter.items():
        if count > 1:
            duplicates[track] = count
    
    return duplicates

# Save Report to File with a unique filename for each playlist
def save_report(duplicates, playlist_id, filename_prefix="duplicates_report"):
    if not duplicates:
        print("No duplicates to save.")
        return

    filename = f"{filename_prefix}_{playlist_id}.csv"
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Track", "Count"])
            for track, count in duplicates.items():
                writer.writerow([track, count])
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")

# Send Email with Duplicates Report
def send_email(user_email, duplicates, playlist_link):
    if not duplicates:
        print("No duplicates to send in email.")
        return

    subject = "Duplicate Tracks Report from Your Spotify Playlist"
    body = f"Here is the list of duplicate tracks found in your playlist: {playlist_link}\n\n"
    for track, count in duplicates.items():
        body += f"🎵 {track}: {count} times\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, user_email, msg.as_string())
        print(f"📧 Email sent successfully to {user_email}.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Remove Duplicates from Playlist with snapshot_id handling
def remove_duplicates(sp, playlist_id, duplicates, all_tracks):
    if not duplicates:
        print("No duplicates to remove.")
        return

    print("\n⚠️ Do you want to remove duplicate tracks from the playlist?")
    confirmation = input("Type 'yes' to proceed: ").strip().lower()
    if confirmation != "yes":
        print("Operation canceled.")
        return

    try:
        # Get initial snapshot id of the playlist
        playlist_info = sp.playlist(playlist_id)
        snapshot = playlist_info['snapshot_id']
        for track_name in duplicates:
            tracks_to_remove = [
                item['track']['uri']
                for item in all_tracks 
                if item.get('track') and f"{item['track']['name']} - {item['track']['artists'][0]['name']}" == track_name
            ]
            # Remove all but the first occurrence if duplicates exist
            if len(tracks_to_remove) > 1:
                response = sp.playlist_remove_all_occurrences_of_items(
                    playlist_id, tracks_to_remove[1:], snapshot_id=snapshot
                )
                if response and 'snapshot_id' in response:
                    snapshot = response['snapshot_id']
        print("Duplicates removed successfully!")
    except Exception as e:
        print(f"❌ Error removing duplicates: {e}")

# Main Execution
def main():
    try:
        scope = "playlist-modify-public playlist-modify-private"
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=scope
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return

    try:
        playlist_links = input("Enter Spotify Playlist URLs (separated by commas): ").strip().split(',')
        playlist_links = [link.strip() for link in playlist_links]

        for link in playlist_links:
            playlist_id = extract_playlist_id(link)
            if not playlist_id:
                print(f"❌ Invalid link: {link}")
                continue

            all_tracks = get_playlist_tracks(sp, playlist_id)
            if not all_tracks:
                print(f"⚠️ No tracks found or error retrieving playlist: {link}")
                continue

            duplicates = analyze_duplicates(all_tracks)

            print(f"\nResults for playlist: {link}")
            if not duplicates:
                print("🎉 No duplicate tracks found!")
            else:
                print(f"🔥 Found {len(duplicates)} duplicate tracks:")
                for track, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
                    print(f"🎵 {track}: {count} times")

            save_report(duplicates, playlist_id)

            user_email = input("\nEnter your email to receive the duplicates report (or press Enter to skip): ").strip()
            if user_email:
                send_email(user_email, duplicates, link)

            remove_duplicates(sp, playlist_id, duplicates, all_tracks)

    finally:
        if 'sp' in locals():
            del sp
        if 'auth_manager' in locals():
            del auth_manager

if __name__ == "__main__":
    main()

