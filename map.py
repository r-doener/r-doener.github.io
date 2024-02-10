from flask import Flask, render_template
from doenerconfig import *
import sqlite3
from datetime import datetime

app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')


@app.route('/')
def home():
    now = datetime.now()
    conn = sqlite3.connect(db_file)

    cur = conn.cursor()

    if maps_data == "google":
        cur.execute("SELECT id,title,rating,price,g_lat,g_lon,author,date_created,picture,selftext,image_ns,permalink, strftime('%d.%m.%Y', datetime(date_created, 'unixepoch')) as form_date FROM doener where g_lat not null order by date_created desc")
    elif maps_data == "bing":
        cur.execute("SELECT id,title,rating,price,lon,lat,author,date_created,picture,selftext,image_ns,permalink, strftime('%d.%m.%Y', datetime(date_created, 'unixepoch')) as form_date FROM doener order by date_created desc")
    else: #mixed
        cur.execute("SELECT id, title, rating, price, CASE WHEN g_lat = 0 THEN lon ELSE g_lat END AS selected_lat, CASE WHEN g_lon = 0 THEN lat ELSE g_lon END AS selected_lon, author, date_created, picture, selftext, image_ns, permalink, strftime('%d.%m.%Y', datetime(date_created, 'unixepoch')) AS form_date FROM doener WHERE g_lat IS NOT NULL ORDER BY date_created DESC;")

    rows = cur.fetchall()
    conn.close()

    # todo: fix dat shit ###################################
    prices_all_count = 0
    prices_all_sum = 0
    prices_24_count = 0
    prices_24_sum = 0
    prices_23_count = 0
    prices_23_sum = 0
    prices_22_count = 0
    prices_22_sum = 0
    prices_21_count = 0
    prices_21_sum = 0
    for row in rows:

        if row[3] is not None:
            created = datetime.utcfromtimestamp(row[7])
            d = created.day
            m = created.month
            y = created.year

            ### allltime prices
            prices_all_count = prices_all_count + 1
            prices_all_sum = prices_all_sum + row[3]
            # print(y)
            # print(y)
            # yearly prices
            if y == 2024:
                # print(y)
                # print(clean_price + 1222222)
                prices_24_count = prices_24_count + 1
                prices_24_sum = prices_24_sum + row[3]

            if y == 2023:
                # print(clean_price)
                prices_23_count = prices_23_count + 1
                prices_23_sum = prices_23_sum + row[3]

            if y == 2022:
                prices_22_count = prices_22_count + 1
                prices_22_sum = prices_22_sum + row[3]

            if y == 2021:
                prices_21_count = prices_21_count + 1
                prices_21_sum = prices_21_sum + row[3]

            # print(clean_price)
            # print(date)

    prices_all_median = round(prices_all_sum / prices_all_count, 2)
    prices_24_median = round(prices_24_sum / prices_24_count, 2)

    prices_23_median = round(prices_23_sum / prices_23_count, 2)

    try:
        prices_22_median = round(prices_22_sum / prices_22_count, 2)
    except:
        prices_22_median = 1
    try:
        prices_21_median = round(prices_21_sum / prices_21_count, 2)
    except:
        prices_21_median = 1



    # todo: print directly to file print(render_template("index.html", rows=rows, prices_all_median=prices_all_median, prices_24_median=prices_24_median, prices_23_median=prices_23_median, prices_22_median=prices_22_median, prices_21_median=prices_21_median, now=now))
    return render_template("index.html", rows=rows, prices_all_median=prices_all_median,
                           prices_24_median=prices_24_median, prices_23_median=prices_23_median,
                           prices_22_median=prices_22_median, prices_21_median=prices_21_median, now=now, maps_data=maps_data)


if __name__ == '__main__':
    app.run(debug=True)

    # todo:
    # v.redd.it -> play button
    # irgendwo ist nen lon / lat dreher drin den ich dreckig einfach irgendwoe wieder gedreht habe
