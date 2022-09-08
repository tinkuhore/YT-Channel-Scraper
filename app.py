from flask import Flask, render_template, request
from flask_cors import cross_origin
from util import YTChannelScraper
import pandas as pd


app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/scraper', methods=['POST', 'GET'])  # route to show the video details in a web UI
@cross_origin()
def index():

    if request.method == 'POST':
        try:
            search = request.form.get('search')
            n = int(request.form.get('n'))
            #MySQL Inputs
            host = request.form.get('host')
            user = request.form.get('user')
            passwd = request.form.get('passwd')
            #MongoDB Inputs
            username = request.form.get('username')
            password = request.form.get('password')

            x = YTChannelScraper(search, n)
            f_output = x.final_output()


            mdf = pd.DataFrame(f_output)

            # To store data in MySQL
            # x.mysql_dumping(mdf, host, user, passwd, n)

            # To store data in MongoDB
            x.mongodb_dumping(mdf, username, password, n)

            return render_template('results.html', reviews=f_output, n=n)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'



    else:
        return render_template('index.html')


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
