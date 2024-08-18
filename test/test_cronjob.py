from cronjob import updateFeeds
from db import Database
from unittest.mock import MagicMock


class MockResponse():
    def __init__(self, content) -> None:
        self.content = content


def test_updateFeeds(monkeypatch):
    mock_response_content = "<rss>Mocked RSS Content</rss>"

    def getAllPodcastMock(*args, **kwargs):
        return [
            type('', (object,),
                 {"url": "TEST1",
                  "episodes": [
                      type('', (object,), {"xml": "EpisodeXML1"}),
                      type('', (object,), {"xml": "EpisodeXML"}),
                  ],
                  "customPodcasts": [
                      type('', (object,), {"dateToPostAt": "FakeJsonList",
                                           "freq": 1,
                                           "interval": 2,
                                           "amount": 3}),
                  ],
                  }),

            type('', (object,),
                 {"url": "TEST2",
                  "episodes": [
                      type('', (object,), {"xml": "EpisodeXML"}),
                      type('', (object,), {"xml": "EpisodeXML1"}),
                      type('', (object,), {"xml": "EpisodeXML2"}),
                  ]}),
            type('', (object,),
                 {"url": "TEST3",
                  "episodes": [
                      type('', (object,), {"xml": "EpisodeXML1"}),
                      type('', (object,), {"xml": "EpisodeXMLElse"}),
                  ],
                  "customPodcasts": [
                      type('', (object,), {"dateToPostAt": "FakeJsonList",
                                           "freq": 1,
                                           "interval": 2,
                                           "amount": 3}),
                  ],
                  }),
        ]

    refreshEntityMock = MagicMock()

    updateEpisodeContentMock = MagicMock()

    addLatestEpisodeMock = MagicMock()

    def loadsMock(*args, **kwargs):
        return ["Date1", "Date2"]

    def dumpsMock(*args, **kwargs):
        return '["Date1", "Date2"]'

    def mock_get(*args, **kwargs):
        return MockResponse(mock_response_content.encode())

    def mock_extractContent(*args, **kwargs):
        return ("Useless", ["Episode1", "Episode2", "EpisodeXML"])

    def mock_extractLatestEpisode(*args, **kwargs):
        return "EpisodeXML2"

    def mock_extractTitleFromEpisode(*args, **kwargs):
        for arg in args:
            if arg == "EpisodeXMLElse":
                return "Title2"
        return "Title"

    def mock_parse(*args, **kwargs):
        return args

    def mock_dateListRRule(*args, **kwargs):
        return "NewRRule"

    monkeypatch.setattr(Database, "getAllPodcasts", getAllPodcastMock)
    monkeypatch.setattr(Database, "refreshEntity", refreshEntityMock)
    monkeypatch.setattr(Database, "updateEpisodeContent",
                        updateEpisodeContentMock)
    monkeypatch.setattr(Database, "addLatestEpisode", addLatestEpisodeMock)
    monkeypatch.setattr("cronjob.loads", loadsMock)
    monkeypatch.setattr("cronjob.dumps", dumpsMock)
    monkeypatch.setattr("cronjob.get", mock_get)
    monkeypatch.setattr("cronjob.extractContents", mock_extractContent)
    monkeypatch.setattr("cronjob.extractLatestEpisode",
                        mock_extractLatestEpisode)
    monkeypatch.setattr("cronjob.extractTitleFromEpisode",
                        mock_extractTitleFromEpisode)
    monkeypatch.setattr("cronjob.parse", mock_parse)
    monkeypatch.setattr("cronjob.dateListRRule", mock_dateListRRule)

    updateFeeds()

    refreshEntityMock.assert_called()
    updateEpisodeContentMock.assert_called()
    addLatestEpisodeMock.assert_called()
    assert refreshEntityMock.call_count == 3
    assert updateEpisodeContentMock.call_count == 6
    assert addLatestEpisodeMock.call_count == 1
