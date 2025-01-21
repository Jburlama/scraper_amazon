from seleniumbase import SB
from bs4 import BeautifulSoup, SoupStrainer
from tqdm import tqdm
import pandas as pd
import argparse
import os

my_parser = argparse.ArgumentParser(description="Return list of items from Amazon.com")
my_parser.add_argument("search", metavar="search", type=str, help="The item to search, Use + for spaces | Usage: python3 main.py <search>")
args = my_parser.parse_args()

search = args.search

items = []
page_nbr = 1

with SB(uc=True, incognito=True, ad_block=True) as sb:
	url = f"https://www.amazon.com/s?k={search}"
	sb.activate_cdp_mode(url)

	while (True):
		sb.sleep(2)
		soup = BeautifulSoup(sb.cdp.get_page_source(), "lxml", parse_only=SoupStrainer("div", {"class": "sg-col-inner"}))
		articles = soup.find_all("div", {"class": "sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"})
		pbar = tqdm(total=len(articles), desc=f"Scraping page {page_nbr}...")
		for article in articles:
			title = article.find("h2", {"class": "a-size-medium a-spacing-none a-color-base a-text-normal"}).text.strip()
			link = "https://www.amazon.com" + article.find("a", {"class": "a-link-normal s-line-clamp-2 s-link-style a-text-normal"})["href"]
			try:
				stars = article.find("span", {"class": "a-icon-alt"}).text.strip().split(" ")[0]
			except:
				stars = 0
			try:
				reviews = article.find("span", {"class": "a-size-base s-underline-text"}).text.strip()
			except:
				reviews = 0
			try:
				price = float(article.find("span", {"class": "a-price"}).text.strip().strip("$").split("$")[0].replace(",",""))
			except:
				price = 0
		
			items.append({
				"title": title,
				"stars": stars,
				"reviews": reviews,
				"price": price,
				"link": link
			})
			pbar.update(1)

		pbar.close()
		sb.cdp.sleep(1)
		page_nbr += 1
		if (soup.find("a", {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator"})):
			sb.cdp.click(".s-pagination-next")
		else:
			break

df = pd.DataFrame(items)
print(df.head())

if not os.path.isdir("csv"):
	os.mkdir("csv")

df.to_csv(f"csv/{search}.csv", index=False)

print("All Pages Done!")
