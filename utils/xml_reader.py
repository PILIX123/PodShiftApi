from xml.etree import ElementTree as ET
from datetime import datetime


def createPodcast(podcastContent: str, parsedDates: list[datetime], amount: int, listEpisodes: list[str]) -> str:
    root = ET.fromstring(podcastContent)
    channel = root.find("channel")
    channel.find("title").text = f"Custom Frequency of {
        channel.find("title").text}"
    index = 0
    for date in parsedDates:
        if date > datetime.now():
            break
        for i in range(amount):
            channel.insert(-(i+1+index), ET.fromstring(
                listEpisodes[i+index].xml))
        index += amount

    return ET.tostring(root, encoding="unicode")
