import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import spotipy
from google import genai
from dotenv import load_dotenv

client_Id=os.environ.get("client_Id")
client_secret=os.environ.get("client_secret")
redirect_uri="http://127.0.0.1:8888/callback"


#Initializing the Spotify client
sp=Spotify(auth_manager=SpotifyOAuth(

    client_id=client_Id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-read-private,playlist-read-collaborative,user-library-read"

))

def list_playlists():
    offset=0
    playlist_name=[]
    tracks=[]
    playlist_id=[]
    owner=[]
    public=[]

    while True:
        playlists_response=sp.current_user_playlists(limit=50,offset=offset)
        playlists=playlists_response["items"]

        if not playlists:
            break

        for playlist in playlists:
            if playlist:
                #print(playlist["name"])
                #print(playlist["id"])
                #print(playlist["items"]["total"])
                playlist_name.append(playlist["name"])
                tracks.append(playlist["items"]["total"])
                playlist_id.append(playlist["id"])
                public.append(playlist["public"])
                owner.append(playlist["owner"]["display_name"])
            else:
                continue
        if playlists_response["next"]==None:
            break

        offset+=50    

    playlist_list={
        "Name":playlist_name,
        "Tracks":tracks,
        "Playlist_Id":playlist_id,
        "Owner":owner,
        "Public":public
    }   

    playlists_df=pd.DataFrame(playlist_list)
    playlists_df.index=playlists_df.index+1
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

def playlist_Id_extract():  #Scraps Playlist Id from URLs/Links

    url=input("Enter Playlist Link here: ")
    if "/playlist/" in url:
        playlist_id=url[url.find("/playlist/"):].replace("/playlist/","").split("?")[0]
        #print(play_list_id)
        return playlist_id
    else:
        print("\n❌ Invalid Spotify Playlist URL provided.")
        return 

def get_playlist(playlist_id):
    offset=0
    track_name=[]
    album_name=[]
    track_length=[]
    artist=[]
    track_ids=[]
    release_date=[]
    added_at_date=[]
    try:
        while(True):
            playlist = sp.playlist_items(playlist_id=playlist_id,limit=50,offset=offset)
            items=playlist["items"]

            if not items:
                break
        
            for item in items:
                if item['item']:
                    #print(item)
                    track_name.append(item['item']['name'])
                    album_name.append(item['item']['album']['name'])
                    track_length.append(item['item']['duration_ms'])
                    artist.append(item['item']['artists'][0]['name'])
                    track_ids.append(item['item']['id'])   
                    release_date.append(item['item']['album']['release_date'])
                    added_at_date.append(item['added_at'])
                else:
                    continue   
            if(playlist['next']==None):
                break

            offset+=50

        
        data={
            "Track":track_name,
            "Artist":artist,
            "Album":album_name,
            "Duration":track_length,
            "ID":track_ids,
            "Release Date":release_date,
            "Added At":added_at_date,
        }    

        df=pd.DataFrame(data)
        df.index=df.index+1
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
    print(PlaylistData)
    total_tracks=len(PlaylistData)
    total_duration_in_minutes=(PlaylistData["Duration"].sum())/(1000*60)
    average_track_duration_in_minutes=total_duration_in_minutes/total_tracks
    total_unique_artists=PlaylistData["Artist"].nunique()   
    total_unique_album=PlaylistData["Album"].nunique()
    longest_song = PlaylistData.loc[PlaylistData["Duration"].idxmax(), "Track"]
    shortest_song = PlaylistData.loc[PlaylistData["Duration"].idxmin(), "Track"]
    top_5_artists = PlaylistData["Artist"].value_counts().head(5)
    top_5_str = ", ".join([f"{artist} ({count})" for artist, count in top_5_artists.items()])
    artist_percentages = PlaylistData["Artist"].value_counts(normalize=True) * 100

    top_share = (PlaylistData["Artist"].value_counts(normalize=True) * 100).head(5)
    share_str = ", ".join([f"{artist} ({pct:.1f}%)" for artist, pct in top_share.items()])
    release_years=pd.to_datetime(PlaylistData["Release Date"],format='mixed').dt.year   
    added_date=pd.to_datetime(PlaylistData["Added At"],format='mixed')
    oldest_Song=PlaylistData.loc[release_years.idxmin(),"Track"]
    newest_Song=PlaylistData.loc[release_years.idxmax(),"Track"]
    decades=(release_years//10)*10
    top_decades=decades.value_counts().idxmax()
    addition_months=added_date.dt.to_period('M')
    peak_addition_period=addition_months.value_counts().idxmax()
    peak_period_str=peak_addition_period.strftime('%B %Y')


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
        "Oldest Released Song":oldest_Song,
        "Newest Released Song":newest_Song,
        "Dominant Music Era": int(top_decades),
        "Peak Fixation Month": peak_period_str

    }

    df=pd.DataFrame.from_dict(data,orient='index',columns=["Analysis Results"])
    #print(df.to_string())
    #return df
    print("\n" + "="*50)
    print(" 📊   PLAYLIST STRUCTURAL METADATA ANALYSIS")
    print("="*50)
    print(df.to_string())
    print("="*50)
    return df


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

    Focus on:
    - recurring emotions
    - musical identity
    - aesthetic patterns
    - listening tendencies
    - emotional atmosphere

    Support observations using evidence from recurring artists, albums, eras, and themes.

    Present interpretations as possibilities rather than facts.

    Avoid making confident claims about:
    - age
    - career
    - relationships
    - mental health
    - personal circumstances

    Do not list songs.

    Provide a cohesive narrative describing the playlist's overall identity, mood, and artistic character.
    Tracks to diagnose:
    {tracks_manifest}
    """
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print("\n" + "="*50)
    print(" ✨  VIBE CHECK RESULTS   ✨")
    print("="*50 + "\n")
    print(response.text.strip())
    print("\n" + "="*50)

def data_visualization(PlaylistData):
    pass


def main():

    print("""
          1. Analyze My Playlists
          2. Analyze Playlist URL
          """)
    
    choice=int(input("Enter your choice: "))
    if choice==1:
        playlist_id=list_playlists()

    elif choice==2:
        playlist_id=playlist_Id_extract()

    else:
        print("Invalid Choice t-t")    

    if playlist_id:
        print("\n" + "="*20)
        print(" ✨  PLAYLIST   ✨")
        print("="*20 + "\n")
        PlaylistData = get_playlist(playlist_id)
        
        # Guard clause: only analyze if data was successfully fetched
        if PlaylistData is not None:
            playlist_analysis(PlaylistData)
            playlist_analysis_ai(PlaylistData)

    
main()