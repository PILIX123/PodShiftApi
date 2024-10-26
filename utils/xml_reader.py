from xml.etree import ElementTree as ET
from datetime import datetime


def createPodcast(
    podcastContent: str,
    parsedDates: list[datetime],
    amount: int,
    listEpisodes: list[str],
) -> str:
    root = ET.fromstring(podcastContent)
    channel = root.find("channel")
    channel.find("title").text = (
        f"Custom Frequency of {
        channel.find("title").text}"
    )
    index = 0
    for date in parsedDates:
        if date > datetime.now():
            break
        for i in range(amount):
            if i == 0 and index == 0:
                channel.append(ET.fromstring(listEpisodes[i + index]))
            else:
                channel.insert(-(i + index), ET.fromstring(listEpisodes[i + index]))
        index += amount

    return ET.tostring(root, xml_declaration=True, encoding="unicode")


def isValidXML(xml: str) -> None:
    try:
        content = ET.fromstring(xml)
        rss = content.tag == "rss"
        if not rss:
            raise Exception
    except:
        raise


def extractContents(podcastContent: str) -> tuple[str, list[str]]:
    root = ET.fromstring(podcastContent)
    channel = root.find("channel")
    episodesXMLList = []
    for item in channel.findall("item"):
        episodesXMLList.append(ET.tostring(item, encoding="unicode"))
        channel.remove(item)
    podcastXML = ET.tostring(root, encoding="unicode")

    return podcastXML, episodesXMLList


def extractLatestEpisode(podcastContent: str) -> str:
    root = ET.fromstring(podcastContent)
    channel = root.find("channel")
    latestEpisode = channel.find("item")

    return ET.tostring(latestEpisode, encoding="unicode")


def extractTitleFromEpisode(episodeContent: str) -> str:
    item = ET.fromstring(episodeContent)
    title = item.find("title").text
    return title
