import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


ThingsToDownload = {
    "S": [

    ],
    "M": [

    ],
    "NRKA": [

    ]
}

DownloadLinkInfo = {}

for category in ThingsToDownload:
    # DownloadLinkInfo.update(category)
    for link in tqdm(ThingsToDownload[category]):

        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        if "tv.nrk.no" in link:
            if "nrk" not in DownloadLinkInfo.keys():
                DownloadLinkInfo["nrk"] = {}

            # Fetch Title:
            Title = soup.find("meta", property="og:title")  # <meta property="og:title" content="Bjørnis">
            TitleName = Title["content"]

            # Add to dict.
            DownloadLinkInfo["nrk"][TitleName] = [link, category]


DownloadListFile = ""

with open("./ThingsToDownload.json", "r", encoding="UTF8") as DownloadList:
    DownloadListFile = json.load(DownloadList)

    for site in DownloadLinkInfo:
        for program in DownloadLinkInfo[site]:
            DownloadListFile[site][program] = DownloadLinkInfo[site][program]


with open("./ThingsToDownload.json", "w+", encoding="UTF8") as newFile:
    json.dump(DownloadListFile, newFile, indent=4, ensure_ascii=False)
