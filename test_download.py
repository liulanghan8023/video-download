import unittest
import requests

class TestVideoApiService(unittest.TestCase):

    def setUp(self):
        pass

    def test_download(self):
        url = f"http://localhost:8000/download"
        data = {
            "base_path": "./",
            "product": "呀",
            "urls": ["https://v.douyin.com/L4FJNR3/", "https://v.douyin.com/idLUJW0sPG8/"]
        }
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    unittest.main()
