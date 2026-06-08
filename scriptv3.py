import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import spotipy
from google import genai
from dotenv import load_dotenv

# Added Visualization Libraries
import matplotlib.pyplot as plt
import seaborn as sns

client_Id = os.environ.get("client_Id")
client_secret = os.environ.get("client_secret")
redirect_uri = "http://127.0.0.1:8888/callback"

# Initializing the Spotify client
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=client_Id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-read-private,playlist-read-collaborative,user-library-read"
))

def list_playlists():
    offset = 0
    playlist_name = []
    tracks = []
    playlist_id = []
    owner = []
    public = []

    while True:
        playlists_response = sp.current_user_playlists(limit=50, offset=offset)
        playlists = playlists_response["items"]

        if not playlists:
            break

        for playlist in playlists:
            if playlist:
                playlist_name.append(playlist["name"])
                tracks.append(playlist["items"]["total"])
                playlist_id.append(playlist["id"])
                public.append(playlist["public"])
                owner.append(playlist["owner"]["display_name"])
            else:
                continue
        if playlists_response["next"] == None:
            break

        offset += 50    

    playlist_list = {
        "Name": playlist_name,
        "Tracks": tracks,
        "Playlist_Id": playlist_id,
        "Owner": owner,
        "Public": public
    }   

    playlists_df = pd.DataFrame(playlist_list)
    playlists_df.index = playlists_df.index + 1
    print(playlists_df)
    while True:
        index_input = input("\nEnter the row number of the playlist to analyze: ")
        try:
            idx = int(index_input)
            if idx in playlists_df.index:
                selected_playlist = playlists_df.loc[idx]
                print(f"\n✅ Selected: '{selected_playlist['Name']}'")
                return selected_playlist["Playlist_Id"]
            else:
                print(f"❌ Invalid row number. Please choose a number between 1 and {len(playlists_df)}.")
        except ValueError:
            print("❌ Input error. Please type a valid integer number.")

def playlist_Id_extract():  
    url = input("Enter Playlist Link here: ")
    if "/playlist/" in url:
        playlist_id = url[url.find("/playlist/"):].replace("/playlist/", "").split("?")[0]
        return playlist_id
    else:
        print("\n❌ Invalid Spotify Playlist URL provided.")
        return 

def get_playlist(playlist_id):
    offset = 0
    track_name = []
    album_name = []
    track_length = []
    artist = []
    track_ids = []
    release_date = []
    added_at_date = []
    try:
        while(True):
            playlist = sp.playlist_items(playlist_id=playlist_id, limit=50, offset=offset)
            items = playlist["items"]

            if not items:
                break
        
            for item in items:
                if item['item']:
                    track_name.append(item['item']['name'])
                    album_name.append(item['item']['album']['name'])
                    track_length.append(item['item']['duration_ms'])
                    artist.append(item['item']['artists'][0]['name'])
                    track_ids.append(item['item']['id'])   
                    release_date.append(item['item']['album']['release_date'])
                    added_at_date.append(item['added_at'])
                else:
                    continue   
            if(playlist['next'] == None):
                break

            offset += 50

        data = {
            "Track": track_name,
            "Artist": artist,
            "Album": album_name,
            "Duration": track_length,
            "ID": track_ids,
            "Release Date": release_date,
            "Added At": added_at_date
        }    

        df = pd.DataFrame(data)
        df.index = df.index + 1
        df.to_csv("PlaylistData.csv")
        return(df)
    
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403:
            print("\n🔒 Spotify API Restriction (HTTP 403):")
            print("Due to Spotify's security policies, you can only analyze playlists you own or collaborate on.")
            print("To analyze an external playlist, please open Spotify, right-click the playlist, ")
            print("and click 'Create duplicate / Add to your library' first!")
            return None
        else:
            print(f"❌ A Spotify API error occurred: {e}")
            return None

def playlist_analysis(PlaylistData):
    total_tracks = len(PlaylistData)
    total_duration_in_minutes = (PlaylistData["Duration"].sum()) / (1000 * 60)
    average_track_duration_in_minutes = total_duration_in_minutes / total_tracks
    total_unique_artists = PlaylistData["Artist"].nunique()   
    total_unique_album = PlaylistData["Album"].nunique()
    longest_song = PlaylistData.loc[PlaylistData["Duration"].idxmax(), "Track"]
    shortest_song = PlaylistData.loc[PlaylistData["Duration"].idxmin(), "Track"]
    top_5_artists = PlaylistData["Artist"].value_counts().head(5)
    top_5_str = ", ".join([f"{artist} ({count})" for artist, count in top_5_artists.items()])
    
    top_share = (PlaylistData["Artist"].value_counts(normalize=True) * 100).head(5)
    share_str = ", ".join([f"{artist} ({pct:.1f}%)" for artist, pct in top_share.items()])
    release_years = pd.to_datetime(PlaylistData["Release Date"], format='mixed').dt.year   
    added_date = pd.to_datetime(PlaylistData["Added At"], format='mixed')
    oldest_Song = PlaylistData.loc[release_years.idxmin(), "Track"]
    newest_Song = PlaylistData.loc[release_years.idxmax(), "Track"]
    decades = (release_years // 10) * 10
    top_decades = decades.value_counts().idxmax()
    addition_months = added_date.dt.to_period('M')
    peak_addition_period = addition_months.value_counts().idxmax()
    peak_period_str = peak_addition_period.strftime('%B %Y')

    data = {
        "Total Tracks": total_tracks,
        "Total Duration (Mins)": round(total_duration_in_minutes, 2),
        "Avg Track Duration (Mins)": round(average_track_duration_in_minutes, 2),
        "Unique Artists": total_unique_artists,
        "Unique Albums": total_unique_album,
        "Longest Song": longest_song,
        "Shortest Song": shortest_song,
        "Top 5 Artists": top_5_str,
        "Top Artist Share": share_str,
        "Oldest Released Song": oldest_Song,
        "Newest Released Song": newest_Song,
        "Dominant Music Era": int(top_decades),
        "Peak Fixation Month": peak_period_str
    }

    df = pd.DataFrame.from_dict(data, orient='index', columns=["Analysis Results"])
    print("\n" + "="*50)
    print(" 📊   PLAYLIST STRUCTURAL METADATA ANALYSIS")
    print("="*50)
    print(df.to_string())
    print("="*50)
    return df

# NEW: Data Visualization Function
def plot_playlist_insights(PlaylistData):
    print("\n📈 GENERATING VISUAL DATA DASHBOARD...")
    
    # Setting up look and feel
    sns.set_theme(style="darkgrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🎵 Playlist Insights & Timeline Analysis 🎵', fontsize=20, fontweight='bold', y=0.98)

    # 1. BAR CHART: Top 5 Artists
    top_artists = PlaylistData["Artist"].value_counts().head(5)
    sns.barplot(x=top_artists.values, y=top_artists.index, ax=axes[0, 0], palette="viridis")
    axes[0, 0].set_title("Top 5 Artists (Track Count)", fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel("Number of Tracks")

    # 2. PIE CHART: Era / Decades Breakdown
    release_years = pd.to_datetime(PlaylistData["Release Date"], format='mixed').dt.year
    decades = ((release_years // 10) * 10).astype(int).astype(str) + "s"
    era_counts = decades.value_counts()
    
    axes[0, 1].pie(era_counts, labels=era_counts.index, autopct='%1.1f%%', startangle=140, 
                  colors=sns.color_palette("pastel"))
    axes[0, 1].set_title("Dominant Music Eras (Decades)", fontsize=14, fontweight='bold')

    # 3. LINE GRAPH: Song Addition Timeline (Over Time Analysis)
    added_dates = pd.to_datetime(PlaylistData["Added At"], format='mixed').dt.to_period('M').sort_values()
    timeline_counts = added_dates.value_counts().sort_index()
    # Convert period index back to timestamp strings for matplotlib compatibility
    timeline_x = timeline_counts.index.astype(str)
    
    axes[1, 0].plot(timeline_x, timeline_counts.values, marker='o', color='#1DB954', linewidth=2.5)
    axes[1, 0].set_title("Your Listening Fixation Timeline (Songs Added over Time)", fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel("Month / Year")
    axes[1, 0].set_ylabel("Tracks Added")
    axes[1, 0].tick_per_axis = 5
    axes[1, 0].set_xticklabels(timeline_x, rotation=45, ha='right')

    # 4. HISTOGRAM/DENSITY: Track Duration Distribution
    durations_mins = PlaylistData["Duration"] / (1000 * 60)
    sns.histplot(durations_mins, kde=True, ax=axes[1, 1], color='purple', bins=15)
    axes[1, 1].set_title("Track Length Distribution", fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel("Duration (Minutes)")
    axes[1, 1].set_ylabel("Count")

    plt.tight_layout()
    
    # Save chart dashboard locally
    plt.savefig("playlist_insights_dashboard.png", dpi=300)
    print("💾 Dashboard saved locally as 'playlist_insights_dashboard.png'")
    
    # Display window
    plt.show()

def playlist_analysis_ai(PlaylistData):
    print("\n🔮 COOKING VIBE CHECK (Please wait a moment)...")
    ai_client = genai.Client()
    
    sample_tracks = []
    for idx, row in PlaylistData.iterrows():
        sample_tracks.append(f"- {row['Track']} by {row['Artist']} (Album: {row['Album']})")
    
    tracks_manifest = "\n".join(sample_tracks)
    
    prompt = f"""
    You are a perceptive music critic and playlist analyst.
    Analyze the playlist itself.
    Focus on recurring emotions, musical identity, aesthetic patterns, listening tendencies, and emotional atmosphere.
    Present interpretations as possibilities rather than facts. Avoid strict claims about demographic details. Do not list songs.
    Tracks to diagnose:
    {tracks_manifest}
    """
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print("\n" + "="*50)
    print(" ✨   VIBE CHECK RESULTS   ✨")
    print("="*50 + "\n")
    print(response.text.strip())
    print("\n" + "="*50)

def main():
    print("""
          1. Analyze My Playlists
          2. Analyze Playlist URL
          """)
    
    choice = int(input("Enter your choice: "))
    if choice == 1:
        playlist_id = list_playlists()
    elif choice == 2:
        playlist_id = playlist_Id_extract()
    else:
        print("Invalid Choice t-t")    

    if playlist_id:
        print("\n" + "="*20)
        print(" ✨   PLAYLIST   ✨")
        print("="*20 + "\n")
        PlaylistData = get_playlist(playlist_id)
        
        if PlaylistData is not None:
            playlist_analysis(PlaylistData)
            plot_playlist_insights(PlaylistData)  # Visual dashboard trigger
            playlist_analysis_ai(PlaylistData)

if __name__ == "__main__":
    main()