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
            if i == 0 and index == 0:
                channel.append(ET.fromstring(listEpisodes[i+index]))
            else:
                channel.insert(-(i+1+index-1), ET.fromstring(
                    listEpisodes[i+index]))
        index += amount

    return ET.tostring(root, xml_declaration=True, encoding="unicode")
