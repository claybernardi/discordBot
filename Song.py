from yt_dlp import YoutubeDL

class Song():
    def __init__(self, user, url, id):
        YDL_OPTIONS = {
            'format': '(bestvideo+bestaudio/bestvideo)[protocol!*=http_dash_segments]/bestvideo+bestaudio/best',
            'noplaylist': 'True',
        }
        self.user = user
        self.id = id
        if "youtube.com/" in url:
            self.link = url
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
        elif "youtu.be" in url:
            self.link= url
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
        elif "soundcloud" in url:
            self.link=url
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
        else:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
                self.link = info.get('webpage_url', None)
        for format in info['formats']:
            if "https://i.ytimg" not in format['url']:
                if "https://manifest.googlevideo.com/api/manifest/dash/" not in format['url']:
                    self.URL = format['url']
                    break
            # self.URL = info['formats'][3]['url']
        self.title = info.get('title', None)
        self.length = int(info.get('duration', None))
        self.link = info.get('webpage_url', None)
        if self.URL is None:
            for format in info['formats']:
                print(format['url'])
            raise TypeError("Unsupported Format")
    def duration_string(self):
        length = '['
        if self.length > 3600:
            length += f"{int(self.length / 3600)}:"
        if self.length > 60:
            min = int(self.length/60) % 60
            if min < 10:
                if min == 0:
                    length += "00:"
                length += f"0{min}:"
            else:
                length += f"{min}:"
        else:
            length += "00:"
        secs = self.length % 60
        if secs < 10:
            length += "0"

        length += f"{self.length % 60}]"
        return length
