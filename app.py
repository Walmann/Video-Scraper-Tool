import json
import yt_dlp
import os
import sys

import pathlib
import argparse
from git.repo import Repo

# TODO Auto update on start of script? Git pull or something.
repo = Repo('./')
print("Checking for updates...")
gitFetch = repo.remotes.origin.fetch()

xxx = repo.index.diff(None)

for item in repo.index.diff(None):
    print(item.a_path)

debugScript = False


# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
# parser.add_argument("-h", "--help", help="Show Help")
parser.add_argument("-rootdl", "--RootDownloadFolder", help='Root folder for all downloads. Example: "H:\\Shares\\Vaulter\\001 - Video" Remember to double backslash')
parser.add_argument("-debug", "--Debug", action='store_true', help="Enable debug")
parser.add_argument("-cat", "--Category", help="Only download from this selection inside ThingsToDownload.json. Useful for debugging.")


# Read arguments from command line
args = parser.parse_args()

# if args.Output:
#     print("Displaying Output as: %s" % args.DownloadRoot)
if args.RootDownloadFolder:
    Save_Location = args.RootDownloadFolder
else:
    Save_Location = input("Enter input for RootDownloadFolder. Remember double backslash")

if not args.Debug == None:
    debugScript = args.Debug

URLS = json.load(open("./ThingsToDownload.json", encoding="UTF8"))

setDownloadLocation = ""


def logToFile(text, clearlog=False):
    if clearlog:
        with open("LogFile.log", "w+") as logFile:
            logFile.write("")
    with open("LogFile.log", "a+", encoding=("utf-8")) as logFile:
        logFile.write(text+"\n")


def my_hook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading {}".format(file_tuple[1]))
    if d['status'] == 'downloading':
        print("File: "+d['filename'] + d['_percent_str'] + "Time left: " + d['_eta_str'])
        # print("\r")
    else:
        print("No process logg")


def writeOutput(msg):
    # TODO RegEx Matching.

    logToFile(msg)

    printText = True
    messagesToSkip = [
        ": Downloading instalments JSON page",
        ": Downloading serie JSON",
        ": NRK said: Kommer ",
        ": NRK said: Kommer om",
        " has already been downloaded",
        "[download] Downloading playlist:",
        "[download] Finished downloading playlist:",
        "[hlsnative] Downloading m3u8 manifest",
        "[hlsnative] Total fragments:",
        "[info]",
        "[info]",
        "[NRKTVSeries] Playlist",
        "Downloading m3u8 information",
        "Downloading manifest JSON",
        "Downloading metadata JSON",
        "Downloading programs JSON",
        "Ikke tilgjengelig lenger",
        "Possible MPEG-TS in MP4 container or malformed AAC timestamps. Install ffmpeg to fix this automatically",
        "[download] 100%"
    ]
    messagesToKeepSameLine = [
        "[download]  ",
        # "[download] 100%",
        " (frag ",
    ]
    messagesToKeepNewLine = [
        "[download] Downloading video",
        "Now downloading: ",
        "[download] Destination: "
    ]
    doneSearching = False
    while doneSearching == False:
        for message in messagesToSkip:
            if message in msg:
                if not debugScript:
                    printText = False
                doneSearching = True

            # TODO !!!!!! cut off the print() by using print("TEXT")[os.get_terminal_size()]

        for message in messagesToKeepNewLine:
            if message in msg:
                if not debugScript:
                    printText = False
                print(msg)
                doneSearching = True

        for message in messagesToKeepSameLine:
            if message in msg:
                if not debugScript:
                    printText = False
                print(str(msg).ljust(os.get_terminal_size()[1]), end="\r")
                # sys.stdout.write("\r"+str(msg).ljust(os.get_terminal_size()[1]))
                # sys.stdout.write("\r"+msg)
                # sys.stdout.flush()
                doneSearching = True

        if printText:
            print(msg, end="\n")
            # print("\n"+msg+"\n")
        doneSearching = True
        pass


class loggerOutputs:

    def error(msg):
        logToFile(msg)
        writeOutput(msg=msg)

    def warning(msg):
        logToFile(msg)
        writeOutput(msg=msg)
        pass

    def debug(msg):
        logToFile(msg)
        writeOutput(msg=msg)


logToFile("", clearlog=True)
for page_Entry in URLS:
    # if not page_Entry == args.Category:
    if args.Category and not args.Category == page_Entry:
        continue
    
    page = URLS[page_Entry]

    for entries in page:
        logToFile("\n\n" + str(entries))
        print("\n\nNow downloading: " + str(entries))
        download_URL = URLS[page_Entry][entries][0]
        sub_folder = ""
        try:
            sub_folder = URLS[page_Entry][entries][2] + "\\"
        except:
            sub_folder = ""

        # Create SaveLocation:
        if URLS[page_Entry][entries][1] == "S":
            temp_Save_Location = Save_Location+"\\003 - Serier\\" + sub_folder
        elif URLS[page_Entry][entries][1] == "M":
            temp_Save_Location = Save_Location+"\\002 - Film\\" + sub_folder
        elif URLS[page_Entry][entries][1] == "NRKA":
            temp_Save_Location = Save_Location+"\\004 - NRK Arkivet\\" + sub_folder
        elif URLS[page_Entry][entries][1] == "YTChannels":
            temp_Save_Location = Save_Location+"\\006 - Youtube Kanaler\\" + sub_folder
        elif URLS[page_Entry][entries][1] == "YTPlaylist":
            temp_Save_Location = Save_Location+"\\006 - Youtube Spillelister\\" + sub_folder
        else:
            temp_Save_Location = Save_Location+"\\SORTERES\\"

        # TODO: Check if temp_Save_Location exists.
        if not os.path.exists(temp_Save_Location):
            pathlib.Path(temp_Save_Location).mkdir(parents=True, exist_ok=True)

        # Create ydl_opts defaults:
        ydl_opts = {
            # "simulate": True,
            "quiet": True,
            # "verbose": True,
            # "no_verbose_header": True,
            # "format": "bestvideo",
            # "ignore_no_formats_error": True,
            # "progress": True,
            # "progress_hooks": [my_hook],
            "ignoreerrors": True,
            "no_warnings:": True,
            # "extract_flat": True,
            'prefer_ffmpeg': True,
            # "ffmpeg_location": "dep/ffmpeg.exe",
            "concurrent_fragment_downloads": 4,
            "writedescription": True,
            "writeinfojson": True,
            "writethumbnail": True,
            "writesubtitles": True,
            "allsubtitles": True,
            "writeannotation": True,
            "external_downloader_args": ['-loglevel quiet', '-hide_banner', '-N 6'],
            "extractor_retries": 10,
            "retries": 10,
            "logger": loggerOutputs,
            "consoletitle": True,
            "download_archive": temp_Save_Location + "\\Videos.json"
        }

        if page_Entry == "nrk":
            # NRK always have the episode number in the Episode title, so no eposide_number needed.
            ydl_opts.update({
                "outtmpl": temp_Save_Location + "\\%(series)s\\%(season)s\\%(episode)s\\%(episode)s.%(ext)s"
            })

        elif page_Entry == "youtube":
            ydl_opts.update({
                "outtmpl": temp_Save_Location +"\\%(uploader)s\\%(upload_date>%Y-%m-%d)s - %(title)s - %(id)s.%(ext)s"
            })

        # Create list over downloaded media in current category:
        if debugScript:
            ydl_opts.update({
                "force_write_download_archive": True,
                "download_archive": temp_Save_Location,
                "simulate": True
            })

        #Make sure download_archive exists:
        if not os.path.exists(ydl_opts["download_archive"]):
            pathlib.Path(ydl_opts["download_archive"]).mkdir(parents=True, exist_ok=True)

        print()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(download_URL)
        print("")
