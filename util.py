from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
import time
import pyshorteners as ps
import mysql.connector
import pymongo
import base64
import requests
import pandas as pd
from urllib.request import urlopen
import boto3  # for AWS S#
from pytube import YouTube  # only to download video


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
                # driver.close()
                data = soup.find("ytd-video-renderer")

                channel = data.find("a", {"class": "yt-simple-endpoint style-scope yt-formatted-string"})
                channel_url = ps.Shortener().tinyurl.short("http://www.youtube.com" + channel.get("href"))
                print("SUCCESS : Channel link generated.")
                return (channel_url)

            except Exception as e:
                print("FAILED to get channel link with Error : ", e)
                return None

        def channel_name(driver, url):
            try:
                driver.get(url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # driver.quit()

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
                # driver.quit()
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

                print('\n', f"SUCCESS : Generated links of {count} videos in {int(time.time() - st)} sec.", '\n')
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
                # driver.close()

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

        def comment(driver, url):
            try:
                st = time.time()

                driver.get(url)
                driver.execute_script(f"window.scrollTo(0,330)")
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                cc = soup.select("#above-the-fold #comment-teaser #count")
                if len(cc) == 0:
                    cc = soup.select("#comments-button #text")

                if cc[0].text >= str(0):
                    print(f"SUCCESS : Comment Count || Time taken : {int(time.time() - st)} sec.")
                    return cc[0].text
            except Exception as e:
                print("Failed : Comment Count with Error -- ", e)
                return 'NAN'

        def all_comments(driver, url):
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
                print('\n', f"{len(comment_output)} comments extracted with name in {int((time.time() - st))} sec.")
                # print(f"S.T.= {int(st1-st)}, E.T.= {st2-st1}, L.P.T={(time.time() - st2)}")
                return comment_output
            except Exception as e:
                print("Error3 : ", e)
                return [["Failed!", "No Comments Extracted."]]

        try:

            start = time.time()

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options) #for Windows OS, mention executable_path here
            driver.maximize_window()

            channel_url = get_channel_link(driver)
            channel_name = channel_name(driver, channel_url)
            video_links = get_video_title_links_thumb(driver, f"{channel_url}/videos", self.n)
            driver.quit()

            f_output = {'Channel Name': [], 'Channel URL': [], 'Title': [], "Video Link": [], "Thumbnail Link": [],
                        'Total Likes': [], 'Total Comments': [], 'Comment Content': []}
            for count in range(0, self.n):
                print('Processing video ', count + 1, '...')
                video_link = video_links[count]["Video URL"]

                if video_link != "Failed!":
                    try:
                        f_output['Channel Name'].append(channel_name)
                        f_output['Channel URL'].append(channel_url)
                        f_output['Title'].append(video_links[count]["Title"])
                        f_output["Video Link"].append(video_link)
                        f_output["Thumbnail Link"].append(video_links[count]['Thumbnail Link'])
                        print("SUCCESS : Title, Video link and Thumbnail Link generated.", '\n')
                    except Exception as e:
                        print("Error4 : ", e)

                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--headless")
                    driver = webdriver.Chrome(options=chrome_options) #for Windows OS, mention executable_path here
                    driver.maximize_window()

                    try:
                        f_output['Total Likes'].append(like(driver, video_link))
                        f_output['Total Comments'].append(comment(driver, video_link))

                    except Exception as e:

                        print("Error5 : ", e)

                    try:
                        f_output['Comment Content'].append(all_comments(driver, video_link))

                    except Exception as e:
                        print("Error6 : ", e)
                    driver.quit()
                    print("_" * 100, '\n')

            print('*' * 25, '\n', f"Total time taken = {round((time.time() - start) / 60, 2)} mins.", '\n',
                  '*' * 25, '\n')
            return f_output

        except Exception as e:
            print("Failed! : Error 7", e)
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
                    v_i = {'Video URL': mdf["Video Link"][i], 'Thumbnail URL': mdf["Thumbnail Link"][i]}

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

    def video_downloader(self, mdf):
        try:
            start = time.time()
            s3 = boto3.resource(
                service_name='s3',
                region_name='us-east-1',
                aws_access_key_id='AKIAX3XU3IZGO4XPNU3J',
                aws_secret_access_key='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')
            print("ASW S3 : Connection Established.")

            try:
                # download and upload
                ind = 1
                for url in mdf["Video Link"]:
                    unshortened_url = urlopen(url).geturl()
                    yt = YouTube(unshortened_url)
                    stream = yt.streams
                    stream_list = list(stream)

                    # set resolution = 240p
                    for i in stream_list:
                        if str(i).find('''mime_type="video/mp4" res="240p"''') >= 0:
                            index = stream_list.index(i)
                            break

                    file_name = f"video_{ind}"
                    stream[index].download(output_path='./video_download', filename=file_name)

                    try:
                        s3.Bucket('yt-channel-scraper').upload_file(Filename=f'video_download/{file_name}',
                                                                    Key=f'video_download/{file_name}')

                        print(f"Video {ind} uploaded to S3 Bucket.")
                    except Exception as e:
                        print(f"Video {ind} Upload Failed with error : ", e)
                    ind += 1
                print('\n', f"Time taken to upload videos :  {round(((time.time() - start) / 60), 2)} min.")
            except Exception as e:
                print("ASW S3 : Video Upload Failed.", e)
        except Exception as e:
            print("ASW S3 : Connection Failed with error : ", e)
