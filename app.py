import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import spotipy
from google import genai
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# Load Environment Variables safely
load_dotenv()

# ──────────────────────────────────────────────────────────────────────────
#  PAGE CONFIGURATION & PREMIUM STYLING INFRASTRUCTURE
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Psychefy", page_icon="🎵", layout="wide")

# Modern Spotify-esque Cyberpunk Dark CSS Injection
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
:root {
    --bg:        #0A0A0F;
    --surface:   #12121A;
    --surface2:  #1A1A26;
    --border:    rgba(255,255,255,0.07);
    --green:     #1DB954;
    --violet:    #8B5CF6;
    --pink:      #EC4899;
    --text:      #F0EFF4;
    --muted:     #7A798A;
    --radius:    14px;
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main .block-container {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.psychefy-hero {
    background: linear-gradient(135deg, #0A0A0F 0%, #1A0A2E 50%, #0A0F1E 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.psychefy-hero::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(29,185,84,0.18) 0%, transparent 70%);
}
.hero-eyebrow {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--green);
    font-weight: 600; margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem; font-weight: 700;
    line-height: 1.1; color: var(--text);
    margin: 0 0 0.6rem;
    background: linear-gradient(135deg, #F0EFF4 0%, #1DB954 60%, #8B5CF6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem; color: var(--muted);
    font-weight: 300; position: relative; z-index: 1;
}

.section-label {
    display: flex; align-items: center; gap: 0.6rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem; font-weight: 600;
    color: var(--text); margin: 2.5rem 0 1.2rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.7rem;
}
.section-label span.pill {
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 99px;
    background: rgba(29,185,84,0.15); color: var(--green);
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem; margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--green), var(--violet));
}
.metric-label {
    font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem; font-weight: 700; color: var(--text);
    line-height: 1.1;
}

.meta-table {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden;
    margin-bottom: 2rem;
}
.meta-row {
    display: flex; justify-content: space-between;
    padding: 0.75rem 1.6rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
}
.meta-row:last-child { border-bottom: none; }
.meta-key { color: var(--muted); font-weight: 500; }
.meta-val { color: var(--text); font-weight: 500; text-align: right; max-width: 65%; }

.vibe-card {
    background: linear-gradient(135deg, #1A0A2E 0%, #0A1A1A 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: var(--radius);
    padding: 2rem 2.4rem;
    position: relative; overflow: hidden;
}
.vibe-text {
    font-size: 1rem; line-height: 1.8;
    color: rgba(240,239,244,0.88); font-weight: 300;
}

.stRadio > label { display: none !important; }
div[role="radiogroup"] { display: flex; gap: 0.5rem; }
div[role="radiogroup"] > label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 99px !important;
    padding: 0.4rem 1.2rem !important;
    cursor: pointer !important;
    font-size: 0.88rem !important; color: var(--muted) !important;
    transition: all 0.2s !important;
}
div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(29,185,84,0.15) !important;
    border-color: var(--green) !important;
    color: var(--green) !important;
}

.stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important; font-size: 0.9rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(29,185,84,0.12) !important;
}

.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1DB954, #17a349) !important;
    border: none !important;
    border-radius: 99px !important;
    color: #0A0A0F !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 2rem !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

.stDownloadButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 99px !important;
    color: var(--text) !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    border-color: var(--green) !important; color: var(--green) !important;
}

.profile-pic {
    border-radius: 50%; width: 90px; height: 90px;
    object-fit: cover; display: block; margin: 0 auto 0.8rem;
    border: 2px solid var(--green);
    box-shadow: 0 0 20px rgba(29,185,84,0.3);
}
.user-greeting {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem; font-weight: 600; color: var(--text);
    text-align: center; margin-bottom: 0.2rem;
}
.user-sub {
    font-size: 0.78rem; color: var(--muted);
    text-align: center; margin-bottom: 1.5rem;
}
.sidebar-divider {
    border: none; border-top: 1px solid var(--border);
    margin: 1rem 0;
}

/* Fixes vanishing toggle icon arrow issue by safely managing header elements */
[data-testid="stHeader"] {
    background-color: transparent !important;
}
[data-testid="stHeaderDecoration"] {
    display: none !important;
}
footer { 
    visibility: hidden; 
}
.stDeployButton { 
    display: none !important; 
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
#  SPOTIFY API CORE INTEGRATION & AUTHENTICATION LOGIC
# ──────────────────────────────────────────────────────────────────────────
client_Id = os.environ.get("client_Id")
client_secret = os.environ.get("client_secret")
redirect_uri = "http://127.0.0.1:8888/callback"

@st.cache_resource
def get_spotify_client():
    if not client_Id or not client_secret:
        return None
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_Id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-read-private,playlist-read-collaborative,user-library-read"
    ))

sp = get_spotify_client()

if not sp:
    st.error("❌ Spotify API Credentials missing! Please verify your environment variables or .env file mapping.")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────
#  SIDEBAR PROFILE DISCOVERY RENDERER
# ──────────────────────────────────────────────────────────────────────────
try:
    user_info = sp.current_user()
    user_name = user_info.get("display_name", "Spotify User")
    followers_count = user_info.get("followers", {}).get("total", 0)

    images = user_info.get("images", [])
    pfp_url = images[0]["url"] if images else "https://www.scdn.co/images/talk/default-avatar.png"

    with st.sidebar:
        st.markdown(f'<img src="{pfp_url}" class="profile-pic">', unsafe_allow_html=True)
        st.markdown(f'<div class="user-greeting">{user_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-sub">{followers_count:,} followers · Connected 🟢</div>', unsafe_allow_html=True)
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:.6rem;">About Psychefy</div>
        <div style="font-size:.83rem;color:#7A798A;line-height:1.6;">
            Psychefy deconstructs your listening habits, timelines, and sonic attributes to decode your curation identity and produce an AI vibe portrait.
        </div>
        """, unsafe_allow_html=True)
except Exception:
    st.sidebar.error("Could not load Spotify Profile data.")


# ──────────────────────────────────────────────────────────────────────────
#  BRAND HERO HEADER RENDERING
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="psychefy-hero">
    <div class="hero-eyebrow">Playlist Intelligence Engine</div>
    <div class="hero-title">Psychefy</div>
    <div class="hero-sub">Decode the acoustics and emotional atmosphere behind your music. Structural metadata analytics, era timelines, and AI portraits.</div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
#  CORE RE-ENGINEERED PIPELINE FUNCTIONS (PRESERVING INITIAL ALGORITHMS)
# ──────────────────────────────────────────────────────────────────────────
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
    return pd.DataFrame(playlist_list)


def playlist_Id_extract(url):
    if "/playlist/" in url:
        playlist_id = url[url.find("/playlist/"):].replace("/playlist/", "").split("?")[0]
        return playlist_id
    return None


@st.cache_data
def get_playlist(playlist_id):
    offset = 0
    track_name = []
    album_name = []
    track_length = []
    artist = []
    track_ids = []
    release_date = []
    added_at_date = []
    cover_art = []
    try:
        while True:
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
                    
                    if item['item']['album']['images']:
                        cover_art.append(item['item']['album']['images'][0]['url'])
                    else:
                        cover_art.append("")
                else:
                    continue   
            if playlist['next'] == None:
                break

            offset += 50

        data = {
            "Track": track_name,
            "Artist": artist,
            "Album": album_name,
            "Duration": track_length,
            "ID": track_ids,
            "Release Date": release_date,
            "Added At": added_at_date,
            "Cover Art": cover_art
        }    

        df = pd.DataFrame(data)
        df.index = df.index + 1
        df.to_csv("PlaylistData.csv")
        return df
    
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403:
            st.error("🔒 **Spotify API Restriction (HTTP 403):** Due to developer dashboard access policies, you can only parse playlists you explicitly own or collaborate on. Duplicate external user lists into your library first!")
            return None
        else:
            st.error(f"❌ A Spotify API error occurred: {e}")
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

    playlist_meta_data = {
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
    return playlist_meta_data


def playlist_analysis_ai(PlaylistData):
    try: 
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
        return response.text
    except Exception as e:
        return f"Could not generate AI insights. Error: {e}"


def data_visualization(PlaylistData):
    bg = "#0A0A0F"
    surface = "#12121A"
    border = "#1E1E2E"
    text = "#F0EFF4"
    muted = "#7A798A"
    green = "#1DB954"
    violet = "#8B5CF6"
    pink = "#EC4899"
    amber = "#F59E0B"

    plt.rcParams.update({
        "figure.facecolor": bg,
        "axes.facecolor": surface,
        "axes.edgecolor": border,
        "axes.labelcolor": muted,
        "axes.titlecolor": text,
        "xtick.color": muted,
        "ytick.color": muted,
        "text.color": text,
        "grid.color": border,
        "grid.linewidth": 0.6,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.patch.set_facecolor(bg)
    fig.suptitle("Playlist Analytics Dashboard Insights", fontsize=16, fontweight="bold",
                 color=text, y=0.98, x=0.02, ha="left")

    # 1. BAR CHART: Top 10 Artists
    ax = axes[0, 0]
    top_artists = PlaylistData["Artist"].value_counts().head(10)
    colors = [green if i == 0 else violet if i < 3 else "#3D3D5C" for i in range(len(top_artists))]
    bars = ax.barh(top_artists.index[::-1], top_artists.values[::-1], color=colors[::-1], height=0.6)
    
    for bar, val in zip(bars, top_artists.values[::-1]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', fontsize=9, color=muted)
    ax.set_title("Top 10 Tracked Artists", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Tracks Added", fontsize=9)
    ax.set_xlim(0, top_artists.values.max() * 1.15)

    # 2. PIE CHART: Era Donut
    ax = axes[0, 1]
    release_years = pd.to_datetime(PlaylistData["Release Date"], format='mixed').dt.year
    decades = ((release_years // 10) * 10).astype(int).astype(str) + "s"
    era_counts = decades.value_counts().sort_index()
    palette = [green, violet, pink, amber, "#06B6D4", "#F97316"][:len(era_counts)]
    
    wedges, texts, autotexts = ax.pie(
        era_counts, labels=era_counts.index, autopct='%1.0f%%',
        startangle=140, colors=palette,
        wedgeprops=dict(width=0.55, edgecolor=bg, linewidth=2),
        pctdistance=0.75,
    )
    for t in texts: t.set(color=muted, fontsize=9)
    for a in autotexts: a.set(color=bg, fontsize=8, fontweight="bold")
    ax.set_title("Dominant Music Eras (Decades)", fontsize=12, fontweight="bold", pad=12)

    # 3. LINE GRAPH: Song Addition Timeline
    ax = axes[1, 0]
    added_dates = pd.to_datetime(PlaylistData["Added At"], format='mixed').dt.to_period('M').sort_values()
    timeline = added_dates.value_counts().sort_index()
    x = range(len(timeline))
    
    ax.fill_between(x, timeline.values, alpha=0.15, color=green)
    ax.plot(x, timeline.values, color=green, linewidth=2.2, marker='o', markersize=4, markerfacecolor=green)
    
    peak_idx = timeline.values.argmax()
    ax.annotate(f"Peak: {timeline.index[peak_idx]}",
                xy=(peak_idx, timeline.values[peak_idx]),
                xytext=(peak_idx + 0.5, timeline.values[peak_idx] + 0.3),
                fontsize=8, color=green,
                arrowprops=dict(arrowstyle='->', color=green, lw=1))
    
    ax.set_xticks(list(x)[::max(1, len(x)//6)])
    ax.set_xticklabels([str(timeline.index[i]) for i in list(x)[::max(1, len(x)//6)]], rotation=35, ha='right', fontsize=8)
    ax.set_title("Listening Fixation Timeline", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Tracks Added", fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    # 4. HISTOGRAM/DENSITY: Track Duration Distribution
    ax = axes[1, 1]
    durations = PlaylistData["Duration"] / (1000 * 60)
    ax.hist(durations, bins=15, color=violet, edgecolor=bg, linewidth=0.5, alpha=0.85)
    mean_d = durations.mean()
    ax.axvline(mean_d, color=green, linewidth=1.5, linestyle='--')
    ax.text(mean_d + 0.1, ax.get_ylim()[1] * 0.9, f"Avg: {mean_d:.1f}m", color=green, fontsize=8)
    
    ax.set_title("Track Length Distribution", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Duration (Minutes)", fontsize=9)
    ax.set_ylabel("Count", fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    plt.tight_layout(pad=2.5)
    return fig


# ──────────────────────────────────────────────────────────────────────────
#  MAIN DASHBOARD FLOW INFRASTRUCTURE
# ──────────────────────────────────────────────────────────────────────────
def main():
    st.markdown('<div style="font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:.6rem;">Select Playlist Synchronization Vector</div>', unsafe_allow_html=True)

    choice = st.radio("", ("Analyze My Playlists", "Analyze Playlist URL"), horizontal=True)
    playlist_id = None

    if choice == "Analyze My Playlists":
        with st.spinner("Fetching your Spotify account playlists...."):
            try:
                playlist_list = list_playlists()
                if not playlist_list.empty:
                    playlist_options = playlist_list.set_index("Name")["Playlist_Id"].to_dict()
                    selected_playlist_name = st.selectbox("Select a Playlist to analyze:", list(playlist_options.keys()))
                    playlist_id = playlist_options[selected_playlist_name]
                else:   
                    st.warning("No playlists parsed from your account metadata profile.")
            except Exception as e:
                st.error(f"Failed to access your playlists: {e}")  
    else:
        url_input = st.text_input("Enter Playlist Link here:", placeholder="https://open.spotify.com/playlist/...")
        if url_input:
            extracted_id = playlist_Id_extract(url_input)
            if extracted_id:
                playlist_id = extracted_id
            else:
                st.error("❌ Invalid Spotify Playlist URL format.")           

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if playlist_id:
        if st.button("🚀 Run Comprehensive Analysis", type="primary"):
            with st.spinner("Processing tracks, cover arts, and metric evaluations..."):
                PlaylistData = get_playlist(playlist_id)

                if PlaylistData is not None and not PlaylistData.empty:
                    st.success(f"✅ Complete Playlist Data synchronized! ({len(PlaylistData)} tracks processed)")
                
                    # ────────────── SECTION-1: METRICS ──────────────
                    st.markdown('<div class="section-label">📊 Structural Metrics <span class="pill">Overview</span></div>', unsafe_allow_html=True)
                    metrics = playlist_analysis(PlaylistData)
                    
                    st.markdown(f"""
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-label">Total Tracks</div>
                            <div class="metric-value">{metrics["Total Tracks"]}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Duration</div>
                            <div class="metric-value">{metrics["Total Duration (Mins)"]}<span style="font-size:1rem;color:var(--muted)"> min</span></div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Unique Artists</div>
                            <div class="metric-value">{metrics["Unique Artists"]}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Dominant Era</div>
                            <div class="metric-value">{metrics["Dominant Music Era"]}s</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    meta_rows = ""
                    for k, v in metrics.items():
                        meta_rows += f"""
                        <div class="meta-row">
                            <span class="meta-key">{k}</span>
                            <span class="meta-val">{v}</span>
                        </div>"""
                    st.markdown(f'<div class="meta-table">{meta_rows}</div>', unsafe_allow_html=True)

                    # ────────────── SECTION-2: TRACKLIST ──────────────
                    st.markdown('<div class="section-label">🎵 Tracklist & Cover Art Details <span class="pill">All Songs</span></div>', unsafe_allow_html=True)
                    
                    tracklist_html = """
                    <style>
                        /* Sleek Custom Scrollbar Integration */
                        ::-webkit-scrollbar {
                            width: 8px;
                        }
                        ::-webkit-scrollbar-track {
                            background: #12121A;
                            border-radius: 14px;
                        }
                        ::-webkit-scrollbar-thumb {
                            background: #2A2A36;
                            border-radius: 10px;
                        }
                        ::-webkit-scrollbar-thumb:hover {
                            background: #1DB954;
                        }

                        .tracklist-wrap {
                            background: #12121A; border: 1px solid rgba(255,255,255,0.07);
                            border-radius: 14px; overflow: hidden; font-family: 'Inter', sans-serif;
                            color: #F0EFF4;
                        }
                        .tracklist-header {
                            display: grid; grid-template-columns: 45px 60px 2.5fr 2fr 2fr;
                            gap: 1rem; padding: 0.75rem 1.4rem; background: #1A1A26;
                            font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em;
                            text-transform: uppercase; color: #7A798A; border-bottom: 1px solid rgba(255,255,255,0.07);
                        }
                        .track-row {
                            display: grid; grid-template-columns: 45px 60px 2.5fr 2fr 2fr;
                            gap: 1rem; padding: 0.6rem 1.4rem; align-items: center;
                            border-bottom: 1px solid rgba(255,255,255,0.07); transition: background 0.15s;
                        }
                        .track-row:last-child { border-bottom: none; }
                        .track-row:hover { background: #1A1A26; }
                        .track-num { font-size: 0.8rem; color: #7A798A; font-variant-numeric: tabular-nums; text-align: center; }
                        .track-name { font-weight: 600; font-size: 0.9rem; color: #F0EFF4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                        .track-meta { font-size: 0.85rem; color: #7A798A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                    </style>
                    <div class="tracklist-wrap">
                        <div class="tracklist-header">
                            <div style="text-align: center;">#</div>
                            <div>Cover</div>
                            <div>Title</div>
                            <div>Artist</div>
                            <div>Album</div>
                        </div>
                    """
                    
                    for idx, row in PlaylistData.iterrows():
                        if row.get("Cover Art"):
                            cover_html = f'<img src="{row["Cover Art"]}" width="40" height="40" style="border-radius:4px;object-fit:cover;">'
                        else:
                            cover_html = '<span style="font-size: 1.2rem; display: block; text-align: center;">🎵</span>'
                            
                        tracklist_html += f"""
                        <div class="track-row">
                            <div class="track-num">{idx}</div>
                            <div>{cover_html}</div>
                            <div class="track-name">{row['Track']}</div>
                            <div class="track-meta">{row['Artist']}</div>
                            <div class="track-meta">{row['Album']}</div>
                        </div>
                        """
                    tracklist_html += "</div>"
                    
                    # Native Streamlit HTML renderer encapsulation prevents string layout leaks
                    st.components.v1.html(
                        f"""
                        <div style="height: 480px; overflow-y: auto; padding-right: 4px;">
                            {tracklist_html}
                        </div>
                        """, 
                        height=480, 
                        scrolling=False
                    )

                    # ────────────── SECTION-3: VISUALIZATIONS ──────────────
                    st.markdown('<div class="section-label">📈 Data Visualization Dashboard <span class="pill">Visualized</span></div>', unsafe_allow_html=True)
                    analytics_fig = data_visualization(PlaylistData)
                    st.pyplot(analytics_fig)
                    
                    # ────────────── SECTION-4: AI ENGINE ──────────────
                    st.markdown('<div class="section-label">🔮 AI Vibe Check Insight Profile <span class="pill">Powered by Gemini</span></div>', unsafe_allow_html=True)
                    
                    with st.spinner("Consulting the musical oracle..."):
                        vibe_feedback = playlist_analysis_ai(PlaylistData)
                        
                    st.markdown(f"""
                    <div class="vibe-card">
                        <div class="vibe-text">{vibe_feedback}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
                    
                    # File System Export Component
                    st.download_button(
                        label="📥 Download Playlist Dataset (CSV)",
                        data=PlaylistData.to_csv().encode('utf-8'),
                        file_name="PlaylistData.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No tracking values could be retrieved for this target list selection.")


if __name__ == "__main__":
    main()