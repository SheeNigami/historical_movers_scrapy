# historical_movers_scrapy

1) Extract top gaining and losing stocks on stockmarketwatch.com top gainers/losers in premarket/aftermarket ( ./spiders/movers_scraper.py, parse() )

2) Using waybackmachine middleware we intercept requests and responses to download snapshots of the site from 20 June 2016 onwards before running the spider (middlewares.py)
(middleware courtesy of https://github.com/sangaline/scrapy-wayback-machine with some modifications)

3) For each ticker scraped, call cdx api of waybackmachine for finviz site of the ticker to see dates where site is changed ( ./spiders/movers_scraper.py, parse_cdx() )

4) Get the closest date where finviz site is updated and scrape required data from waybackmachine archive of finviz site (or current site if closest) for ticker ( ./spiders/movers_scraper.py, parse_finviz() )

5) Store all scraped info along with session and move info as Ticker item (items.py)

6) For each item, check session and move and write to appropriate csv using CSVItemExporter alone with correct date to be determined based on session and time (pipelines.py)


Results:

Scraped ~3500 premarket winners and losers each, 550 after hours winners and losers each
