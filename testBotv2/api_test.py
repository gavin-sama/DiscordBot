import pytest
from unittest.mock import patch
import requests

@patch("requests.get")
def test_shazam_api_success(mock_get):
    # mock api response
    mock_response = {
        "tracks": {
            "hits": [
                {
                    "track": {
                        "title": "Blinding Lights",
                        "subtitle": "The Weeknd"
                    }
                }
            ]
        }
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # mock api call
    url = "https://shazam8.p.rapidapi.com/track/search"
    headers = {"X-RapidAPI-Key": "mock_key", "X-RapidAPI-Host": "shazam8.p.rapidapi.com"}
    params = {"query": "Blinding Lights"}
    response = requests.get(url, headers=headers, params=params)

    # assertions
    assert response.status_code == 200
    data = response.json()
    assert data["tracks"]["hits"][0]["track"]["title"] == "Blinding Lights"
    assert data["tracks"]["hits"][0]["track"]["subtitle"] == "The Weeknd"

@patch("requests.get")
def test_shazam_api_no_tracks(mock_get):
    # mock api no results response
    mock_response = {"tracks": {"hits": []}}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # mock api call
    url = "https://shazam8.p.rapidapi.com/track/search"
    headers = {"X-RapidAPI-Key": "mock_key", "X-RapidAPI-Host": "shazam8.p.rapidapi.com"}
    params = {"query": "Unknown Song"}
    response = requests.get(url, headers=headers, params=params)

    #assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["tracks"]["hits"]) == 0
