from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd

class YouTubeScraper:
    def __init__(self, url, progress_callback=None):
        self.url = url
        self.driver = webdriver.Chrome()
        self.master_list = []
        self.progress_callback = progress_callback

    def scrape(self):
        self.driver.get(self.url)
        time.sleep(5)
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        videos = soup.find_all("div", {"id": "dismissible"})
        total_videos = len(videos)
        for index, video in enumerate(videos):
            # ... scraping logic ...
            if self.progress_callback:
                self.progress_callback((index + 1) / total_videos * 100)  # Update progress as a percentage

        for video in videos:
            data_dict = {}
            data_dict['video_title'] = video.find("a", {"id", "yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media"}).text
            data_dict['video_url'] = "https://www.youtube.com/" + video.find("a", {"id": "video-title-link"})["href"]
            metablock = video.find("div", {"id": "metadata-line"})
            clean_metablock = metablock.find_all("span")
            data_dict['video_views'] = clean_metablock[0].text
            data_dict['video_age'] = clean_metablock[1].text
            self.master_list.append(data_dict)

    def convert_views(self, df):
        try:
            if "K" in df["video_views"]:
                views = float(df["video_views"].split('K')[0]) * 1000
                return int(views)
            elif "M" in df["video_views"]:
                views = float(df["video_views"].split('M')[0]) * 1000000
                return int(views)
            else:
                # If "K" or "M" is not present, simply convert the original view_str to an integer
                return int(df["video_views"].strip("views"))
        except ValueError:
            # Handle the case where the conversion fails
            return int(df["video_views"].strip("views"))

    def process_data(self):
        self.scrape()
        youtube_df = pd.DataFrame(self.master_list)
        youtube_df["CLEAN_VIEWS"] = youtube_df.apply(self.convert_views, axis=1)
        youtube_df["CLEAN_VIEWS"].fillna(-1, inplace=True)
        youtube_df["CLEAN_VIEWS"] = youtube_df["CLEAN_VIEWS"].astype(int)
        return youtube_df

    def save_to_csv(self, filename):
        youtube_df = self.process_data()
        youtube_df.to_csv(filename, index=False)


if __name__ == "__main__":
    url = input("Enter the YouTube channel URL: ")
    # Extract a clean version of the URL to use as the filename
    filename = url.replace("https://www.youtube.com/@", "").replace("/", "_") + ".csv"
    scraper = YouTubeScraper(url)
    scraper.save_to_csv(filename)

