from flask import Flask, render_template, request
from flask_cors import cross_origin
from util import YTChannelScraper
import time
from datetime import datetime
import pandas as pd
import mysql.connector
import pymongo
import base64
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/scraper', methods=['POST', 'GET'])  # route to show the video details in a web UI
@cross_origin()
def index():
    start = time.time()
    if request.method == 'POST':
        try:
            search = request.form.get('search')
            n = int(request.form.get('n'))

            x = YTChannelScraper(search, n)

            channel_url = x.get_channel_link()
            channel_name = x.channel_name(channel_url)
            video_links = x.get_video_title_links_thumb(f"{channel_url}/videos", n=n)

            f_output = {'Title': [], "Video Link": [], "Thumbnail Link": [],
                        'Total Likes': [], 'Total Comments': [], 'Comment Content': []}
            for count in range(0, n):
                print('video ', count + 1, ' processing...')
                video_link = video_links[count]["Video URL"]

                if video_link != "Failed!":
                    try:
                        f_output['Title'].append(video_links[count]["Title"])
                        f_output["Video Link"].append(video_link)
                        f_output["Thumbnail Link"].append(video_links[count]['Thumbnail Link'])
                        print("Title, Video link and Thumbnail Link appended.")
                    except Exception as e:
                        print("Error4 : ", e)

                    try:
                        f_output['Total Likes'].append(x.like(video_link))
                        f_output['Total Comments'].append(x.comment(video_link))
                        print("Likes and Comment count appended.")
                    except Exception as e:

                        print("Error5 : ", e)

                    try:
                        f_output['Comment Content'].append(x.all_comments(video_link))
                        print("Comment content appended.")
                    except Exception as e:
                        print("Error6 : ", e)

                    print("_" * 100, '\n')
                else:
                    print("Failed!")
                    f_output['Title'].append("Failed!")
                    f_output["Video Link"].append("Failed!")
                    f_output["Thumbnail Link"].append("Failed!")
                    f_output['Total Likes'].append("Failed!")
                    f_output['Total Comments'].append("Failed!")
                    f_output['Comment Content'].append([["Failed!", "No Comments Extracted."]])

            # To store data in MySQL
            mdf = pd.DataFrame(f_output)
            df = mdf.drop(['Comment Content'], axis=1)
            df.insert(0, 'YoutuberName', channel_name)
            try:
                st = time.time()
                mydb = mysql.connector.connect(
                    host=request.form.get('host'),
                    user=request.form.get('user'),
                    passwd=request.form.get('passwd'),
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

            # To store data in MongoDB

            df2 = mdf.drop(['Title', 'Total Likes', 'Total Comments', 'Comment Content'], axis=1)

            try:
                st = time.time()
                client = pymongo.MongoClient(
                    f"mongodb+srv://{request.form.get('username')}:{request.form.get('password')}@cluster0.4augg9h.mongodb.net/?retryWrites=true&w=majority")

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
                    mongo_dict = {'_id': channel_name + "||" + str(datetime.now())[:19]}
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

            # Calculate total time taken by the program
            print('\n', '*' * 25, '\n', f"Total time taken = {round((time.time() - start) / 60, 2)} mins.", '\n',
                  '*' * 25, )

            return render_template('results.html', reviews=f_output,
                                   n=n,
                                   channel_url=channel_url,
                                   channel_name=channel_name)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'



    else:
        print(f"time taken = {round((time.time() - start) / 60, 2)} mins")
        return render_template('index.html')


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
