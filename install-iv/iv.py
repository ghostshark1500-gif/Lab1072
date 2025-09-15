#!/usr/bin/env python3
import sys
import shutil
import yt_dlp
import subprocess
from colorama import Fore, Style, init

init(autoreset=True)
VERSION = "0.0.7"

def check_ffmpeg_mpv():
    if shutil.which("ffmpeg") is None:
        print(f"{Fore.LIGHTRED_EX}❌ ffmpeg tidak ditemukan! Install: pkg install ffmpeg -y")
        sys.exit(1)
    if shutil.which("mpv") is None:
        print(f"{Fore.LIGHTRED_EX}❌ mpv tidak ditemukan! Install: pkg install mpv -y")
        sys.exit(1)

def show_help():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
iv version-{VERSION}

Menginstall audio dan video menjadi lebih mudah dengan iv.
Bisa memutar/install audio/video dari YouTube, TikTok, Instagram, Facebook, LK21.

OPTIONS
  -h   --help          bantuan
  -f   --format        format output
 AUDIO:
    [.mp3, .m4a, .opus, .aac, .wav]
  -a   --abr           kualitas audio [64,128,192 kbps] [default 128]

 VIDEO:
    [.mp4, .mkv, .avi, .mov, .wmv, .flv, .webm]
  -q   --quality       kualitas video [144p, 240p, 360p, 480p, 540p, 720p, 1080p]
  -l   --list-formats  tampilkan semua format
  -sr  --search        mencari audio/video interaktif
  --min-duration       durasi minimal (detik)
  --max-duration       durasi maksimal (detik)
  --max-results        jumlah hasil search [1-20] default 10

CONTO:
>>> iv -sr "lastchild" --max-results 10 --min-duration 3600
>>> iv -f mp4 -q 240p "link video"
>>> iv -a 64 "link audio" -p
>>> iv "link audio/video" (default mp3 128 kbps)
""")

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', '0 KiB/s')
        eta = d.get('_eta_str', '??:??')
        print(f"{Fore.CYAN}⬇️ {percent} | {speed} | ETA {eta}      ", end="\r")
    elif d['status'] == 'finished':
        print(f"\n{Fore.GREEN}✅ Selesai: {d['filename']}")

def format_duration_hms(seconds):
    if seconds is None:
        return "??:??"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def list_formats(url):
    opts = {"listformats": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def search_youtube_rinci(keyword, max_results=10, min_dur=None, max_dur=None):
    opts = {"quiet": True, "skip_download": True}
    query = f"ytsearch{max_results}:{keyword}"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
        entries = info.get("entries", [])
        filtered = []
        for e in entries:
            dur = e.get("duration", 0)
            if min_dur and dur < min_dur:
                continue
            if max_dur and dur > max_dur:
                continue
            filtered.append(e)
        if not filtered:
            print(f"{Fore.RED}❌ Tidak ada hasil sesuai filter durasi")
            return None
        print(f"{Fore.LIGHTCYAN_EX}Hasil search '{keyword}':")
        for i, e in enumerate(filtered, 1):
            dur_str = format_duration_hms(e.get("duration"))
            print(f"{i}. {e['title']} [{dur_str}]")
        choice_num = input(f"{Fore.LIGHTCYAN_EX}Pilih nomor [1-{len(filtered)}]: ")
        try:
            choice_num = int(choice_num)
            if not (1 <= choice_num <= len(filtered)):
                raise ValueError
            url = filtered[choice_num-1]['webpage_url']
        except:
            print(f"{Fore.LIGHTRED_EC}❌ Pilihan nomor tidak valid")
            return None
        action = input(f"{Fore.LIGHTGREEN_EX}Aksi: [1] Putar audio, [2] Install: ")
        if action == "1":
            return ("play", url)
        elif action == "2":
            return ("download", url)
        else:
            print(f"{Fore.RED}❌ Pilihan aksi tidak valid")
            return None

def pick_format(info, quality):
    formats = [f for f in info['formats'] if f.get('height')]
    if not formats:
        return None
    available = sorted(set(f['height'] for f in formats))
    target = int(quality)
    if target in available:
        chosen = max([f for f in formats if f['height']==target], key=lambda x: x.get('tbr') or 0)
        return chosen['format_id']
    else:
        fallback = max(available)
        chosen = max([f for f in formats if f['height']==fallback], key=lambda x: x.get('tbr') or 0)
        print(f"{Fore.LIGHTYELLOW_EX}⚠️ {target}p tidak ada, fallback {fallback}p")
        return chosen['format_id']

def play_audio(url, abr="128"):
    print(f"{Fore.LIGHTCYAN_EX}▶️ Memutar audio langsung ({abr} kbps)...")
    cmd = ["mpv", "--no-video", "--no-cache", f"--ytdl-format=bestaudio[abr>={abr}]", url]
    subprocess.run(cmd)

def download(url, ext="mp3", quality="720", abr="128"):
    audio_formats = ["mp3","m4a","opus","aac","wav"]
    if shutil.which("aria2c"):
        external_downloader = "aria2c"
        external_args = ["-x16","-k1M"]
    else:
        external_downloader = None
        external_args = None

    common_opts = {
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "continuedl": True,
        "retries": 20,
        "fragment_retries": 20,
        "socket_timeout": 60,
    }
    if external_downloader:
        common_opts["external_downloader"] = external_downloader
        common_opts["external_downloader_args"] = external_args

    try:
        with yt_dlp.YoutubeDL(common_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if ext in audio_formats:
                opts = {
                    **common_opts,
                    "format": "bestaudio/best",
                    "postprocessors": [{"key": "FFmpegExtractAudio","preferredcodec": ext,"preferredquality": abr}],
                }
            else:
                chosen_format = pick_format(info, quality)
                if not chosen_format:
                    print(f"{Fore.LIGHTRED_EX}❌ Tidak ada format video valid")
                    return
                opts = {
                    **common_opts,
                    "format": f"{chosen_format}+bestaudio/best",
                    "merge_output_format": ext,
                }
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([url])
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}❌ Error: {str(e)}")

# ---- Main ----
if __name__ == "__main__":
    check_ffmpeg_mpv()
    if len(sys.argv) < 2 or sys.argv[1] in ["-h","--help"]:
        show_help()
        sys.exit(0)

    url = None
    ext = "mp3"
    quality = "720"
    abr = "128"
    search_mode = False
    min_dur = None
    max_dur = None
    max_results = 10

    # Parse flags
    if "-f" in sys.argv or "--format" in sys.argv:
        idx = sys.argv.index("-f") if "-f" in sys.argv else sys.argv.index("--format")
        ext = sys.argv[idx+1].replace(".","").lower()
    if "-q" in sys.argv or "--quality" in sys.argv:
        idx = sys.argv.index("-q") if "-q" in sys.argv else sys.argv.index("--quality")
        quality = sys.argv[idx+1].replace("p","")
    if "-a" in sys.argv or "--abr" in sys.argv:
        idx = sys.argv.index("-a") if "-a" in sys.argv else sys.argv.index("--abr")
        abr = sys.argv[idx+1]

    # Mode search interaktif
    if "-sr" in sys.argv or "--search" in sys.argv:
        search_mode = True
        idx = sys.argv.index("-sr") if "-sr" in sys.argv else sys.argv.index("--search")
        keyword = sys.argv[idx+1]

        if "--min-duration" in sys.argv:
            min_dur = int(sys.argv[sys.argv.index("--min-duration")+1])
        if "--max-duration" in sys.argv:
            max_dur = int(sys.argv[sys.argv.index("--max-duration")+1])
        if "--max-results" in sys.argv:
            max_results = int(sys.argv[sys.argv.index("--max-results")+1])

        # Hapus flag play agar tidak terbaca sebagai URL
        if "-p" in sys.argv: sys.argv.remove("-p")
        if "--play" in sys.argv: sys.argv.remove("--play")

        result = search_youtube_rinci(keyword, max_results, min_dur, max_dur)
        if result is None:
            sys.exit(1)
        action, url = result
        if action == "play":
            play_audio(url, abr)
        elif action == "download":
            download(url, ext, quality, abr)

    else:
        # Mode biasa (URL langsung)
        url = sys.argv[-1]
        if "-p" in sys.argv or "--play" in sys.argv:
            play_audio(url, abr)
        else:
            download(url, ext, quality, abr)
