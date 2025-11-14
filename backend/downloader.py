import os
import io
import zipfile
import yt_dlp
import shutil
import ssl


ssl._create_default_https_context = ssl._create_unverified_context


QUALITY_OPTIONS = {
    'Best': 'best',
    'Worst': 'worst',
    '480p': 'bestvideo[height<=480]+bestaudio/best',
    '720p': 'bestvideo[height<=720]+bestaudio/best',
    '1080p': 'bestvideo[height<=1080]+bestaudio/best'
}

def get_metadata(url):
    ydl_opts = {"quiet": True, "ignoreerrors": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def get_available_formats(url):
    data = get_metadata(url)
    return data.get("formats", [])


def download_video_or_playlist(url, download_path='downloads',
                               download_type='video', quality='Best',
                               content_type='Single Video', zip_output=False):

    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)

    is_playlist = (content_type == 'Playlist')

    ydl_format = 'bestaudio/best' if download_type == 'audio' else QUALITY_OPTIONS.get(quality, 'best')

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': not is_playlist,
        'quiet': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'no_warnings': True,
        'geo_bypass': True,
        'geo_bypass_country': 'IN',
    }

    if download_type == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    downloaded_filepaths = []
    for root, _, files in os.walk(download_path):
        for file in files:
            downloaded_filepaths.append(os.path.join(root, file))

    if zip_output:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for file_path in downloaded_filepaths:
                z.write(file_path, os.path.basename(file_path))
        zip_buffer.seek(0)
        return zip_buffer

    return downloaded_filepaths
