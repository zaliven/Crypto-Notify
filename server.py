from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from time import sleep
from datetime import datetime
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler
import cloudscraper

# For printing colorful messages
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def send_notification(title):
    sent_from = 'X@gmail.com'
    to = ['X@X.com']
    subject = title
    body = 'Message\n'

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    #gmail_user = 'X'
    #gmail_password = 'X'
    gmail_user = 'username@gmail.com'
    gmail_password = 'password'
    
    # ...send email
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()
    server_ssl.login(gmail_user, gmail_password)
    server_ssl.sendmail(sent_from, to, email_text)


def notify_coinbase(df):
    new_coins_detected_str = 'New coins detected: '
    if True in df['is_new'].values:
        for index, row in df[df['is_new'] == True].iterrows():
            send_notification(row['title'])
            new_coins_detected_str += f"\n* {row['title']}"
        # Print new coins message as green text
        new_coins_detected_str = f"{bcolors.OKGREEN}{new_coins_detected_str}{bcolors.OKGREEN}"
    else:
        new_coins_detected_str += 'None'
    return new_coins_detected_str
        


# Check if there are new coins in coinbase (coins launching/becoming available today)
def coinbase_check_new_coins(row):
    result = False
    current_date = datetime.now().strftime("%b %d")
    if row['date'] == current_date and re.search('([A-Z]+).*(?:launch|available)', row['title']):
        result = True
    return result
    

def get_coinbase_df(text):
    soup = BeautifulSoup(text.encode("utf-8"), 'html.parser')
    titles = soup.find_all("h3", {"class": "u-contentSansBold u-lineHeightTightest u-xs-fontSize24 u-paddingBottom2 u-paddingTop5 u-fontSize32"}) 
    titles = [x.text for x in titles]
    timestamps = soup.find_all("time")
    timestamps = [x.text for x in timestamps]
    df = pd.DataFrame({'title' : titles, 'date' : timestamps})
    df['is_new'] = df.apply(lambda x: coinbase_check_new_coins(x), axis=1)
    return df


def get_coinbase_html_text():
    scraper = cloudscraper.create_scraper()
    coinbase_url = 'https://blog.coinbase.com/'
    res = scraper.get(coinbase_url)

    if res.status_code != 200:
        raise Exception("Site couldn't be scraped successfully")

    return res.text


def get_new_coinbase_coins():
    text = get_coinbase_html_text()
    df = get_coinbase_df(text)
    return notify_coinbase(df) # Returns string notifying if there were any new coins


def main():
    try:
        new_coins_detected_str = get_new_coinbase_coins()
    except Exception as e:
        print(e)
    finally:
        print("Finished running job - ", datetime.now().strftime("%d. %B %Y %I:%M:%S %p"))
        print(new_coins_detected_str)


main()
scheduler = BackgroundScheduler()
scheduler.add_job(func=main, trigger="interval", hours=1)
scheduler.start()