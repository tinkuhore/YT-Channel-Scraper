from bs4 import BeautifulSoup
import time
import requests
import os
import pyshorteners as ps
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC




class YTChannelScraper:
    def __init__(self, search, n):
        self.search = search
        self.n = n

    def get_channel_link(self) :
        try:
            url = f"https://www.youtube.com/results?search_query={self.search}"

            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()

            driver.get(url)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.close()
            data = soup.find("ytd-video-renderer")

            channel = data.find("a", {"class": "yt-simple-endpoint style-scope yt-formatted-string"})
            channel_url = ps.Shortener().tinyurl.short("http://www.youtube.com" + channel.get("href"))

            return (channel_url)

        except Exception as e:
            print("FAILED to get channel link with Error : ", e)
            return None


    def channel_name(self, url):
        try:

            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get(url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            channel_name = soup.select("#inner-header-container #text")[0].text
            return channel_name

        except :
            return "Failed!"


    def get_video_title_links_thumb(self,url):
        try:
            st = time.time()
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get(url)
            video_links = []

            for i in list(range(0, 5000, 500)):
                driver.execute_script(f"window.scrollTo( {0 + i},{500 + i}, 'smooth')")
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            v_details = soup.select("#video-title")
            thumbnail = soup.select("#page-manager #contents #items img")

            count=self.n
            for i in range(self.n):
                try:
                    title = v_details[i].text
                except:
                    title = 'Failed!'
                try:
                    video_url = ps.Shortener().tinyurl.short("https://www.youtube.com" + v_details[i]['href'])
                except:
                    count = count - 1
                    video_url = "Failed!"
                try:
                    thumbnail_url = ps.Shortener().tinyurl.short(thumbnail[i + 1]['src'])
                except:
                    thumbnail_url = 'Failed!'

                video_links.append(
                    {'Title': title,
                     'Video URL': video_url,
                     'Thumbnail Link': thumbnail_url})

            print('\n', f"{count} out of {self.n} video links generated in {int(time.time() - st)} sec.", '\n')
            return video_links
        except Exception as e:
            print("Failed to generate video links.", "Error1 : ", e)
            return [{'Title': "Failed!",
                     'Video URL': "Failed!",
                     'Thumbnail Link': "Failed!"}]

    def like(self,url):
        try:
            st= time.time()
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            wd = webdriver.Chrome(executable_path='chromedriver', options=options)
            wd.maximize_window()

            wd.get(url)
            wd.execute_script("window.scrollTo(0,250)")
            time.sleep(1)

            soup = BeautifulSoup(wd.page_source, 'html.parser')
            wd.close()

            like = soup.select("ytd-toggle-button-renderer #text")[0].text
            print(f"Success : Like Count || Time taken : {int(time.time() - st)} sec")

            return like

        except Exception as e:
            print("Failed : Like Count with Error -- ", e)
            return 'NAN'

    def comment(self,url):
        try:
            st=time.time()
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--headless')
            options.add_argument('--window-size=1920,1080')
            driver = webdriver.Chrome(options=options)  #, executable_path=r'chromedriver')
            driver.get(url)
            driver.execute_script("return scrollBy(0, 1000);")
            subscribe = WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, "//yt-formatted-string[text()='Subscribe']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", subscribe)
            # using xpath and text attribute
            comment_count = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//h2[@id='count']/yt-formatted-string"))).text

            driver.quit()
            print(f"SUCCESS : Comment Count || Time taken : {int(time.time() - st)} sec.")
            return comment_count.split(" ")[0]
        except Exception as e:
            print("Failed : Comment Count with Error -- ", e)
            return 'NAN'

    def all_comments(self,url):
        def scroll_down(driver, sleep: int = 1, scroll_height: int = 200):
            prev_h = 0
            while True:
                height = driver.execute_script("""
                        function getActualHeight() {
                            return Math.max(
                                Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                                Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                                Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                            );
                        }
                        return getActualHeight();
                    """)
                driver.execute_script(f"window.scrollTo({prev_h},{prev_h + scroll_height})")
                # fix the time sleep value according to your network connection
                time.sleep(sleep)
                prev_h += scroll_height
                if prev_h >= height:
                    break

        try:
            st = time.time()
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get(url)

            scroll_down(driver, scroll_height=600)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            commenter = soup.select("#comment #author-text span")
            comment_div = soup.select("#content #content-text")
            comment_list = [x.text for x in comment_div]
            commenter_list = [y.text.replace("\n", "").strip() for y in commenter]
            comment_output = []
            for i in range(len(comment_list)):
                comment_output.append([ commenter_list[i] , comment_list[i]])
            print(f"{len(comment_output)} comments extracted with name in {int((time.time() - st))} sec.")
            return comment_output
        except Exception as e:
            print("Error3 : ", e)
            return [["Failed!", "No Comments Extracted."]]

    def get_thumbnail(self,thumbnail_url):
        for i in range(self.n):
            try:
                image = requests.get(thumbnail_url)
            except Exception as e:
                image = ''
                print(f"ERROR - Could not download {thumbnail_url} - {e}")

            folder_path = os.path.join('./Images', '_'.join(self.search.lower().split(' ')))

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            try:
                f = open(os.path.join(folder_path, 'thumbnail' + "_" + str(i + 1)), 'wb')
                f.write(image.content)
                f.close()
                print(f"SUCCESS - saved {thumbnail_url} - as {folder_path}")
            except Exception as e:
                print(f"ERROR - Could not save {thumbnail_url} - {e}")

