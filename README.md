# Crypto Notify
## Overview 
The application scrapes Coinbase every hour and processes the web page to see if new crypto currencies are listed on Coinbase. If they are, the server sends a notification via email (using Gmail as the provider).

## External python libraries used
- BeautifulSoup
- Pandas
- APScheduler
- Cloudscraper
