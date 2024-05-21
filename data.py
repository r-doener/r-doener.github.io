import praw
import sqlite3

from doener_functions import *

conn = sqlite3.connect(db_file)

### reddit praw init
reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent=reddit_user_agent,
)

##### begin
subreddit = reddit.subreddit("doener")

counter = 0  ### just for progress viewing
lon, lat = 0
for submission in subreddit.new(limit=limit):  # hot, top, new, rising,
    counter = counter + 1
    print(counter)
    if is_new(conn, submission.id):

        match = re.search(r'\d{1,2}(?:[.,]\d{0,2})?\s*(?:€|Euro)', submission.title, re.IGNORECASE)
        if match:
            price = match.group()
        else:
            match = re.search(r'\d{1,2}(?:[.,]\d{0,2})?\s*(?:€|Euro)', submission.selftext, re.IGNORECASE)
            if match:
                price = match.group()
            else:
                price = "-"

        # bewertungen

        match = re.search(r'\d{1,2}(?:[.,]\d{1,2})?\s*(?:/|von)\s*\d{1,2}', submission.title, re.IGNORECASE)
        if match:
            rating = match.group()
        else:
            match = re.search(r'\d{1,2}(?:[.,]\d{1,2})?\s*(?:/|von)\s*\d{1,2}', submission.selftext, re.IGNORECASE)
            if match:
                rating = match.group()
            else:
                rating = "-"

        if price != 0 or rating != 0:
            resultat = get_bing_coords(submission.title[:150])

            error = False
            if resultat is not False and (resultat['resourceSets'][0]['estimatedTotal'] > 0):
                lon, lat = resultat['resourceSets'][0]['resources'][0]['point']['coordinates']

            else:
                if hasattr(submission, "selftext") and len(submission.selftext) > 5:
                    resultat = get_bing_coords(submission.selftext[:150])
                    if resultat:
                        if len(resultat['resourceSets']) > 0:
                            lon, lat = resultat['resourceSets'][0]['resources'][0]['point']['coordinates']
                        else:
                            error = True
                else:
                    error = True

            text = str(submission.selftext)

            image = placholder_img
            image_ns = ""
            if hasattr(submission, "preview"):
                try:
                    image = submission.preview["images"][0]["resolutions"][1]["url"]
                except:
                    image = placholder_img

            else:

                if "gallery" in submission.url:
                    image = ""
                    if hasattr(submission, "gallery_data"):
                        ids = [i['media_id'] for i in submission.gallery_data['items']]
                        url = submission.media_metadata[ids[0]]['p'][0]['u']
                        image = url.split("?")[0].replace("preview", "i")

                else:
                    image = placholder_img
                    continue  #### if no pictur, throw away (discussions, polls etc.) #todo: insert id to not double crawl

            date = submission.created_utc
            if not error: ## if no coordinates - throw way
               with conn:
                    values = (
                    submission.id, submission.title, rating, find_number(price), lon, lat, str(submission.author), date,
                    image, text, image_ns, str(submission.permalink))
                    insert_value(conn, values)
            else:
                with conn:
                    values = (
                    submission.id, submission.title, rating, find_number(price), "0", "0", str(submission.author), date,
                    image, text, image_ns, str(submission.permalink)) # coodinaten 0
                    insert_value(conn, values)
            print(values)
    conn.commit()  # save to db


update_google_coord(conn) ### erst später dazu gekommen, vorher muss bing zeug laufen muss umgebaut werden

conn.close()