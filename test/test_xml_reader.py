from lxml import etree
from xml.etree import ElementTree as ET


from datetime import datetime
from freezegun import freeze_time

from utils.xml_reader import createPodcast, extractContents, extractLatestEpisode, extractTitleFromEpisode, isValidXML
import pytest


@freeze_time("2024-08-09 03:03:03")
def test_createPodcast():
    podcastContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
    </channel>
</rss>"""
    listEpisode = [
        """<item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>
            
            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>
            
            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>
            
            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>
            
            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>
            
            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>
            
            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>
            
            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>
            
            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>
            
            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>
            
            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>"""
    ]
    parsedDates = [
        datetime(2024, 8, 5),
        datetime(2024, 8, 6),
        datetime(2024, 8, 7),
        datetime(2024, 8, 8),
        datetime(2024, 8, 9)
    ]
    expectedCreatedFeed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title><![CDATA[Custom Frequency of Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>
            
            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>
            
            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>
            
            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>
            
            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>
            
            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""

    parser = etree.XMLParser(remove_blank_text=True)
    test = createPodcast(
        podcastContent=podcastContent,
        amount=1,
        listEpisodes=listEpisode,
        parsedDates=parsedDates
    )

    expected = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(expectedCreatedFeed.encode('UTF-8'), parser=parser))),
        xml_declaration=True, encoding="unicode")
    real = ET.tostring(ET.fromstring(
        etree.tostring(etree.XML(test.encode("UTF-8"), parser=parser))),
        xml_declaration=True, encoding="unicode")
    assert real == expected


def test_extractContents():
    expectedPodcastContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
    </channel>
</rss>"""
    expectedListEpisode = [
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>
            
            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>
            
            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>
            
            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>
            
            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>
            
            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>
            
            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>
            
            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>
            
            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>
            
            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>
            
            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>""",

    ]
    xmlContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
        
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>

            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>

            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>

            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>

            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>

            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>

            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>

            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>

            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>

            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>

            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""

    parser = etree.XMLParser(remove_blank_text=True)

    realPodcastContent, realListEpisode = extractContents(xmlContent)

    expectedListEpisode = [ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(ep.encode('UTF-8'), parser=parser))), encoding="unicode")
        for ep in expectedListEpisode]

    realListEpisode = [ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(ep.encode('UTF-8'), parser=parser))), encoding="unicode")
        for ep in realListEpisode]

    expectedPodcastContent = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(expectedPodcastContent.encode('UTF-8'), parser=parser))),
        xml_declaration=True, encoding="unicode")

    realPodcastContent = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(realPodcastContent.encode('UTF-8'), parser=parser))),
        xml_declaration=True, encoding="unicode")

    assert realPodcastContent == expectedPodcastContent
    assert realListEpisode == expectedListEpisode


def test_extractLatestEpisode():
    expectedEpisode = """<item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>
            
            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>"""

    xmlContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
        
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>

            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>

            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>

            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>

            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>

            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>

            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>

            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>

            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>

            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>

            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""

    parser = etree.XMLParser(remove_blank_text=True)

    expectedEpisode = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(expectedEpisode.encode('UTF-8'), parser=parser))), encoding="unicode")

    realEpisode = extractLatestEpisode(xmlContent)

    realEpisode = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(realEpisode.encode('UTF-8'), parser=parser))), encoding="unicode")

    assert realEpisode == expectedEpisode


def test_extractTitleFromEpisode():
    episodeContent = """<item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>
            
            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>"""

    expectedTitle = "Lorem ipsum 2024-08-09T00:00:00Z"
    realTitle = extractTitleFromEpisode(episodeContent)
    assert realTitle == expectedTitle


@freeze_time("2024-08-08 03:03:03")
def test_createPodcast_dateBeforeEndOfParsedList():
    podcastContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
    </channel>
</rss>"""
    listEpisode = [
        """<item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>
            
            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>
            
            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>
            
            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>
            
            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>
            
            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>
            
            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>
            
            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>
            
            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>
            
            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>""",
        """<item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>
            
            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>"""
    ]
    parsedDates = [
        datetime(2024, 8, 5),
        datetime(2024, 8, 6),
        datetime(2024, 8, 7),
        datetime(2024, 8, 8),
        datetime(2024, 8, 9)
    ]
    expectedCreatedFeed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title><![CDATA[Custom Frequency of Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>
            
            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>
            
            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>
            
            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>
            
            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""

    parser = etree.XMLParser(remove_blank_text=True)
    test = createPodcast(
        podcastContent=podcastContent,
        amount=1,
        listEpisodes=listEpisode,
        parsedDates=parsedDates
    )

    expected = ET.tostring(ET.fromstring(etree.tostring(
        etree.XML(expectedCreatedFeed.encode('UTF-8'), parser=parser))),
        xml_declaration=True, encoding="unicode")
    real = ET.tostring(ET.fromstring(
        etree.tostring(etree.XML(test.encode("UTF-8"), parser=parser))),
        xml_declaration=True, encoding="unicode")
    assert real == expected


def test_isValidXML():
    xmlContent = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title><![CDATA[Lorem ipsum feed for an interval of 1 days with 10 item(s)]]></title>
        <description><![CDATA[This is a constantly updating lorem ipsum feed]]></description>
        <link>http://example.com/</link>
        <generator>RSS for Node</generator>
        <lastBuildDate>Fri, 09 Aug 2024 05:35:40 GMT</lastBuildDate>
        <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        <copyright><![CDATA[Michael Bertolacci, licensed under a Creative Commons Attribution 3.0 Unported License.]]></copyright>
        
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-09T00:00:00Z]]></title>
            <description><![CDATA[Consequat non amet laborum qui exercitation tempor consequat sit mollit.]]></description>
            <link>http://example.com/test/1723161600</link>
            <guid isPermaLink="true">http://example.com/test/1723161600</guid>

            <pubDate>Fri, 09 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-08T00:00:00Z]]></title>
            <description><![CDATA[Nisi eu do aliquip esse non dolor ut voluptate nulla voluptate enim reprehenderit labore consequat.]]></description>
            <link>http://example.com/test/1723075200</link>
            <guid isPermaLink="true">http://example.com/test/1723075200</guid>

            <pubDate>Thu, 08 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-07T00:00:00Z]]></title>
            <description><![CDATA[Deserunt anim aliquip ea ipsum duis laboris reprehenderit adipisicing.]]></description>
            <link>http://example.com/test/1722988800</link>
            <guid isPermaLink="true">http://example.com/test/1722988800</guid>

            <pubDate>Wed, 07 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-06T00:00:00Z]]></title>
            <description><![CDATA[Id velit tempor qui culpa consequat cillum reprehenderit nisi officia eu sint irure reprehenderit.]]></description>
            <link>http://example.com/test/1722902400</link>
            <guid isPermaLink="true">http://example.com/test/1722902400</guid>

            <pubDate>Tue, 06 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-05T00:00:00Z]]></title>
            <description><![CDATA[Veniam consequat reprehenderit laboris Lorem proident ullamco quis laborum.]]></description>
            <link>http://example.com/test/1722816000</link>
            <guid isPermaLink="true">http://example.com/test/1722816000</guid>

            <pubDate>Mon, 05 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-04T00:00:00Z]]></title>
            <description><![CDATA[Officia enim et ullamco aliquip dolor consequat.]]></description>
            <link>http://example.com/test/1722729600</link>
            <guid isPermaLink="true">http://example.com/test/1722729600</guid>

            <pubDate>Sun, 04 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-03T00:00:00Z]]></title>
            <description><![CDATA[Elit irure sint in proident fugiat ea reprehenderit voluptate dolore duis aute.]]></description>
            <link>http://example.com/test/1722643200</link>
            <guid isPermaLink="true">http://example.com/test/1722643200</guid>

            <pubDate>Sat, 03 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-02T00:00:00Z]]></title>
            <description><![CDATA[Et ex id Lorem aliquip.]]></description>
            <link>http://example.com/test/1722556800</link>
            <guid isPermaLink="true">http://example.com/test/1722556800</guid>

            <pubDate>Fri, 02 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-08-01T00:00:00Z]]></title>
            <description><![CDATA[Voluptate proident ex fugiat nulla.]]></description>
            <link>http://example.com/test/1722470400</link>
            <guid isPermaLink="true">http://example.com/test/1722470400</guid>

            <pubDate>Thu, 01 Aug 2024 00:00:00 GMT</pubDate>
        </item>
        <item>
            <title><![CDATA[Lorem ipsum 2024-07-31T00:00:00Z]]></title>
            <description><![CDATA[Eiusmod minim nisi sint tempor eiusmod anim officia.]]></description>
            <link>http://example.com/test/1722384000</link>
            <guid isPermaLink="true">http://example.com/test/1722384000</guid>

            <pubDate>Wed, 31 Jul 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""
    isValidXML(xmlContent)


def test_isValidXML_Fail_Not_RSS():
    xmlContent = """<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->
</urlset>"""
    with pytest.raises(Exception):
        isValidXML(xmlContent)


def test_isValidXML_Fail_Not_XML():
    xmlContent = """
<!DOCTYPE html>
<html>
<head>
    <title>Lorem Ipsum</title>
</head>
<body>
    <h1>Lorem Ipsum</h1>
    <p>Lorem ipsum dolor sit amet, <b>consectetur adipiscing elit.</b></p>
    <p>Integer nec odio. Praesent libero. <br /> Sed cursus ante dapibus diam.</p>
    <img src="image.jpg" alt="Sample image" />
    &copy; 2024 All rights reserved.
</body>
</html>
"""
    with pytest.raises(ET.ParseError):
        isValidXML(xmlContent)
