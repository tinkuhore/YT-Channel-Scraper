from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pyshorteners as ps
import mysql.connector
import pymongo
import base64
import requests
import pandas as pd


class YTChannelScraper:
    def __init__(self, search, n):
        self.search = search
        self.n = n

    def final_output(self):
        def get_channel_link(driver):
            try:
                url = f"https://www.youtube.com/results?search_query={self.search}"

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

        def channel_name(driver, url):
            try:
                driver.get(url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                channel_name = soup.select("#inner-header-container #text")[0].text
                return channel_name

            except:
                return "Failed!"

        def get_video_title_links_thumb(driver, url, n):
            try:
                st = time.time()
                driver.get(url)

                scroll_h = int(n / 10) * 1000 + 500
                for i in list(range(0, scroll_h, 500)):
                    driver.execute_script(f"window.scrollTo( {0 + i},{500 + i}, 'smooth')")
                    time.sleep(1)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()
                v_details = soup.select("#video-title")
                thumbnail = soup.select("#page-manager #contents #items img")

                video_links = []
                count = self.n
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

        def like(driver, url):
            try:
                st = time.time()

                driver.get(url)
                driver.execute_script("window.scrollTo(0,300)")
                time.sleep(1)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.close()

                like = soup.select("ytd-toggle-button-renderer #text")[0].text

                if 'Hide' in like or 'Show' in like:
                    print(f"Success : Like Count || Time taken : {int(time.time() - st)} sec")
                    like = soup.select("ytd-toggle-button-renderer #text")[1].text
                    return like
                else:
                    print(f"Success : Like Count || Time taken : {int(time.time() - st)} sec")
                    return like
            except Exception as e:
                print("Failed : Like Count with Error -- ", e)
                return 'NAN'

        def comment(url):
            try:
                st = time.time()
                options = webdriver.ChromeOptions()
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument('--headless')
                options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
                browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
                browser.get(url)
                browser.execute_script("return scrollBy(0, 1000);")
                subscribe = WebDriverWait(browser, 60).until(
                    EC.visibility_of_element_located((By.XPATH, "//yt-formatted-string[text()='Subscribe']")))
                browser.execute_script("arguments[0].scrollIntoView(true);", subscribe)
                # using xpath and text attribute
                comment_count = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//h2[@id='count']/yt-formatted-string"))).text

                browser.quit()
                cc = comment_count.split(" ")[0]
                if float(cc) >= 0:
                    print(f"SUCCESS : Comment Count || Time taken : {int(time.time() - st)} sec.")
                    return cc
            except Exception as e:
                print("Failed : Comment Count with Error -- ", e)
                return 'NAN'

        def all_comments(driver, url):
            # def scroll_down(driver, sleep: int = 1, scroll_height: int = 200):
            #     prev_h = 0
            #     while True:
            #         height = driver.execute_script("""
            #                 function getActualHeight() {
            #                     return Math.max(
            #                         Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
            #                         Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
            #                         Math.max(document.body.clientHeight, document.documentElement.clientHeight)
            #                     );
            #                 }
            #                 return getActualHeight();
            #             """)
            #         driver.execute_script(f"window.scrollTo({prev_h},{prev_h + scroll_height})")
            #         # fix the time sleep value according to your network connection
            #         time.sleep(sleep)
            #         prev_h += scroll_height
            #         if prev_h >= height:
            #             break

            try:
                st = time.time()

                driver.get(url)
                for i in list(range(0, 10000, 500)):
                    driver.execute_script(f"window.scrollTo( {0 + i},{500 + i}, 'smooth')")
                    time.sleep(1)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                # st1 = time.time()
                commenter = soup.select("#comment #author-text span")
                comment_div = soup.select("#content #content-text")
                comment_list = [x.text for x in comment_div]
                commenter_list = [y.text.replace("\n", "").strip() for y in commenter]

                # st2 = time.time()
                comment_output = []
                for i in range(len(comment_list)):
                    comment_output.append([commenter_list[i], comment_list[i]])
                print(f"{len(comment_output)} comments extracted with name in {int((time.time() - st))} sec.")
                # print(f"S.T.= {int(st1-st)}, E.T.= {st2-st1}, L.P.T={(time.time() - st2)}")
                return comment_output
            except Exception as e:
                print("Error3 : ", e)
                return [["Failed!", "No Comments Extracted."]]

        try:

            start = time.time()

            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
            driver.maximize_window()

            channel_url = get_channel_link(driver)

            video_links = get_video_title_links_thumb(driver,f"{channel_url}/videos", self.n)

            f_output = {'Channel Name': [], 'Channel URL': [], 'Title': [], "Video Link": [], "Thumbnail Link": [],
                        'Total Likes': [], 'Total Comments': [], 'Comment Content': []}
            for count in range(0, self.n):
                print('video ', count + 1, ' processing...')
                video_link = video_links[count]["Video URL"]

                if video_link != "Failed!":
                    try:
                        f_output['Channel Name'].append(channel_name(driver, channel_url))
                        f_output['Channel URL'].append(channel_url)
                        f_output['Title'].append(video_links[count]["Title"])
                        f_output["Video Link"].append(video_link)
                        f_output["Thumbnail Link"].append(video_links[count]['Thumbnail Link'])
                        print("Title, Video link and Thumbnail Link appended.")
                    except Exception as e:
                        print("Error4 : ", e)

                    try:
                        f_output['Total Likes'].append(like(driver, video_link))
                        f_output['Total Comments'].append(comment(video_link))
                        print("Likes and Comment count appended.")
                    except Exception as e:

                        print("Error5 : ", e)

                    try:
                        f_output['Comment Content'].append(all_comments(driver, video_link))
                        print("Comment content appended.")
                    except Exception as e:
                        print("Error6 : ", e)

                    print("_" * 100, '\n')

            print('*' * 25, '\n', f"Total time taken = {round((time.time() - start) / 60, 2)} mins.", '\n',
                  '*' * 25, '\n')
            return f_output

        except:
            print("Failed! : Error 7")
            f_output = {'Channel Name': ["Failed!"], 'Channel URL': ['Failed!'], 'Title': ["Failed!"],
                        "Video Link": ["Failed!"], "Thumbnail Link": ["Failed!"],
                        'Total Likes': ["Failed!"], 'Total Comments': ["Failed!"],
                        'Comment Content': [[["Failed!", "No Comments Extracted."]]]}

            return f_output

    def mysql_dumping(self, mdf, host, user, passwd, n):
        df = mdf.drop(['Channel URL', 'Comment Content'], axis=1)

        try:
            st = time.time()
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                passwd=passwd,
                auth_plugin='mysql_native_password'
            )
            print("MySQL : Connection Established!")

            try:
                cursor = mydb.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS YT_channel_scraper")
                cursor.execute("CREATE TABLE IF NOT EXISTS YT_channel_scraper.youtubers (YoutuberName varchar(100),\
                                                                                        VideoTitle varchar(200),\
                                                                                        VideoURL varchar(30), \
                                                                                        ThumbnailURL varchar(30), \
                                                                                        TotalLikes varchar(30), \
                                                                                        TotalComments varchar(30))")

                query = "INSERT INTO YT_channel_scraper.youtubers (YoutuberName , VideoTitle , VideoURL , " \
                        "ThumbnailURL , TotalLikes , TotalComments ) VALUES (%s,%s,%s,%s,%s,%s) "
                val = []
                for i in range(n):
                    val.append(tuple(df.iloc[i]))

                cursor.executemany(query, val)
                mydb.commit()
                print("Data INSERTED successfully INTO MySQL", '\n', "Database name : YT_channel_scraper", '\n',
                      "Table name : youtubers "
                      )
            except Exception as e:
                print("Failed to insert into MySQL with Error : ", e)
            print(f"Time taken : {round(time.time() - st, 2)} sec")
            print("*" * 30, '\n')
        except Exception as e:
            print("MySQL : Connection Failed! with Error : ", e)

    def mongodb_dumping(self, mdf, username, password, n):
        try:
            st = time.time()
            client = pymongo.MongoClient(
                f"mongodb+srv://{username}:{password}@cluster0.4augg9h.mongodb.net/?retryWrites=true&w=majority")

            if 'YT_Channel_Scraper' not in client.list_database_names():
                mydb = client['YT_Channel_Scraper']
            else:
                mydb = client['YT_Channel_Scraper']

            if 'youtubers' not in mydb.list_collection_names():
                collection = mydb['youtubers']
            else:
                collection = mydb['youtubers']
            print("MongoDB : Connection Established!")
            try:
                mongo_dict = {'_id': mdf['Channel Name'][0] + "||" + str(datetime.now())[:19]}
                for i in range(n):
                    v_i = {}
                    v_i['Video URL'] = mdf["Video Link"][i]
                    v_i['Thumbnail URL'] = mdf["Thumbnail Link"][i]

                    try:
                        img = requests.get(mdf["Thumbnail Link"][i]).content
                        img_b64 = base64.b64encode(img)
                        v_i['Thumbnail Image base64'] = img_b64
                    except:
                        v_i['Thumbnail Image base64'] = "Download FAILED!"

                    # comments with name
                    cmnt_df = pd.DataFrame(mdf['Comment Content'][i],
                                           columns=["Name", "Comment"])

                    comments = {}
                    for j in range(cmnt_df.shape[0]):
                        comments[cmnt_df["Name"][j]] = cmnt_df["Comment"][j]

                    v_i['comments'] = comments

                    mongo_dict[f"Video{i + 1}"] = v_i

                collection.insert_one(mongo_dict)
                print("SUCCESS: Data stored in MongoDB.")
                print(f"Time taken : {round(time.time() - st, 2)} sec.")
                print("*" * 30, '\n')
            except Exception as e:
                print("Failed to insert into MongoDB with Error : ", e)
        except Exception as e:
            print("MongoDB : Connection Failed! with Error : ", e)
