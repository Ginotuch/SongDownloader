import argparse
import sys
import subprocess
import tempfile
import shutil


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Song:
    def __init__(self, artist: str, title: str, url: str):
        self.artist = artist
        self.title = title
        self.url = url

    def __str__(self):
        return 'Song({0}, {1}, {2})'.format(self.artist, self.title, self.url)


class Downloader:
    def download(self, song: Song, audio_format: str):
        pass


class YoutubeDlDownloader(Downloader):
    def download(self, song: Song, audio_format: str):
        with tempfile.TemporaryDirectory() as tmp_dir:
            filename = 'file.{0}'.format(audio_format)
            subprocess.run(['youtube-dl', song.url, '-x', '--audio-format={0}'.format(audio_format), '-o', 'file.dat'],
                           cwd=tmp_dir)
            subprocess.run(['ffmpeg', '-i', filename,
                            '-metadata', 'title={0}'.format(song.title), '-metadata', 'author={0}'.format(song.artist),
                            '-metadata', 'artist={0}'.format(song.artist),
                            '-codec', 'copy', 'file1.{0}'.format(audio_format)], cwd=tmp_dir)
            filename = 'file1.{0}'.format(audio_format)
            shutil.move("{0}/{1}".format(tmp_dir, filename), "./{0}.{1}".format(song.title, audio_format))


class ParsingOptions:
    def __init__(self, delimiter: str, audio_format: str):
        self.delimiter = delimiter
        self.audio_format = audio_format


def setup_args():
    parser = argparse.ArgumentParser(description='Downloads songs from youtube then converts them to specified format.')
    parser.add_argument('--delimiter', help='Specify the input format delimiter', default=',')
    parser.add_argument('--audio-format', help='Specify the resulting audio format', type=str,
                        choices=['aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav'], required=True)
    args = parser.parse_args()
    return ParsingOptions(args.delimiter, args.audio_format)


class Conductor:
    def __init__(self, parsing_options: ParsingOptions, downloader: Downloader):
        self.parsing_options = parsing_options
        self.downloader = downloader

    def parse(self, input_str: str):
        for index, line in enumerate(input_str):
            song = self._parse_line(line, index)
            self.downloader.download(song, self.parsing_options.audio_format)

    def _parse_line(self, line: str, index: int) -> Song:
        splits = line.split(self.parsing_options.delimiter)
        if len(splits) != 3:
            eprint('PARSING: invalid number of arguments on line {0}'.format(index))
            sys.exit(1)
        artist = splits[0]
        title = splits[1]
        url = splits[2]
        return Song(artist, title, url)


if __name__ == '__main__':
    parsing_options = setup_args()
    conductor = Conductor(parsing_options, YoutubeDlDownloader())
    conductor.parse(sys.stdin)
