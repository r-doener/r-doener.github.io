import googlemaps
import re
import requests

from doenerconfig import *


### insert into db
def insert_value(conn, value):
    sql = ''' INSERT OR IGNORE INTO doener (id, title, rating, price, lon, lat, author, date_created, picture, selftext, image_ns, permalink)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, value)


def update_g_loc(conn, lat, lon, r_id):
    cur = conn.cursor()
    sql = 'UPDATE doener SET g_lat = ?, g_lon = ?, g_crawled = TRUE WHERE id = ?'
    cur.execute(sql, (lat, lon, r_id))
    print((lat, lon, r_id))
    conn.commit()


# check if doener is already cached
def is_new(conn, reddit_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM doener WHERE id=?", (reddit_id,))
    result = cur.fetchone()
    if result:
        print("alt")
        return False
    else:
        print("-->>> neu")
        return True


### find price
def find_number(input_string):
    pattern = r"[-+]?\d*\.\d+|[-+]?\d+,\d+|[-+]?\d+"
    matches = re.findall(pattern, input_string)
    if matches:
        return float(matches[0].replace(',', '.'))
    else:
        return None


#### find location
def get_bing_coords(query):
    url = "http://dev.virtualearth.net/REST/v1/Locations"
    params = {
        "q": query,
        "maxResults": 2,
        "inclnb": 0,
        "ur": "DE",
        "ul": "51.27,9.87",
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.ok == True:
        return response.json()
    else:
        return False


def update_google_coord(conn, value=False):
    cur = conn.cursor()
    cur.execute("SELECT id,title, selftext FROM doener where g_lon  = 0 and g_crawled = False")
    rows = cur.fetchall()
    print(len(rows))

    gmaps = googlemaps.Client(key=google_api_key)
    i = 0
    regex = r'\d{1,2}(?:[.,]\d{0,2})?\s*(?:€|Euro)' ### preise aus dem google query filtern -> das mag google nicht, findet orte teilweise nicht
    for row in rows:
        string = re.sub(regex, '', row[1], flags=re.IGNORECASE) #todo: beitragstext durch die api jagen falls immernoch kein result
        places_fields = ("geometry", "name")
        locationbias1 = "43.4, 1.4"
        locationbias2 = "54.5, 14.4"
        # result = gmaps.find_place(row[1] + " " + row[2][:70],"textquery",places_fields,"rectangle:" + locationbias1 + "," + locationbias2)
        result = gmaps.find_place(string, "textquery", places_fields,
                                  "rectangle:" + locationbias1 + "," + locationbias2)

        if result["status"] != "ZERO_RESULTS" and result["status"] == "OK":
            i = i + 1
            # print(result['candidates'][0]['geometry']['location'])
            update_g_loc(conn, result['candidates'][0]['geometry']['location']['lat'],
                         result['candidates'][0]['geometry']['location']['lng'], str(row[0]))
        else:
            update_g_loc(conn, 0,
                         0, str(row[0]))

    return True
