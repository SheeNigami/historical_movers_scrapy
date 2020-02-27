import scrapy
import json
import logging

from waybackmachine_historical_movers.items import Ticker


class MoversSpider(scrapy.Spider):
    name = "movers_scraper"

    def start_requests(self):
        start_urls = [
            'https://thestockmarketwatch.com/markets/pre-market/today.aspx',
            'https://thestockmarketwatch.com/markets/after-hours/trading.aspx'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        if 'pre-market' in response.request.url:
            session = 'premarket'
        else:
            session = 'after-hours'

        for movers in response.css('table#tblForDesktop > tr:nth-child(1) > td'):
            move = movers.css('h3 > a::text').get()
            mover = movers.css('div > table')
            for row in mover.css('tr')[1:]:
                change_pct = float(row.css('td.tdChangePct > div::text').get().replace('%', '').replace('-', ''))
                last = float(row.css('td.tdChange > div.lastPrice::text').get())
                symb = row.css('td.tdSymbol > a::text').get()
                company = row.css('td.tdCompany > a::text').get()
                volume = int(row.css('td.tdVolume::text').get())

                if change_pct > 10.0 and volume > 25000:
                    finviz_url = 'https://finviz.com/quote.ashx?t='+symb
                    snapshots_url = 'http://web.archive.org/cdx/search/cdx?url={}&output=json&fl=timestamp'\
                                    .format(finviz_url)
                    ticker = Ticker()
                    ticker['datetime'] = response.meta['wayback_machine_time']
                    ticker['session'] = session
                    ticker['mover'] = move
                    ticker['symb'] = symb
                    ticker['change_pct'] = change_pct
                    ticker['last'] = last
                    ticker['company'] = company
                    ticker['volume'] = volume

                    yield scrapy.Request(url=snapshots_url,
                                         dont_filter=True, callback=self.parse_cdx,
                                         cb_kwargs=dict(target_time=response.meta['wayback_machine_time'],
                                                        finviz_url=finviz_url, ticker=ticker))

    def compare_cdx(self, times, target):
        for timestamp in times[1:]:
            actual = int(timestamp[0])
            if actual > int(target):
                return actual
        return int(times[-1][0])

    def parse_cdx(self, response, target_time, finviz_url, ticker):
        try:
            data = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            # forbidden by robots.txt
            data = []
        if len(data) != 0:
            closest_time = self.compare_cdx(data, target_time.strftime("%Y%d%m%H%M%S"))
        else:
            closest_time = -1

        # send another request to get finviz data with closest time
        snapshot_url = 'http://web.archive.org/web/{timestamp}id_/{original}'.format(timestamp=closest_time, original=finviz_url)

        yield scrapy.Request(url=snapshot_url, dont_filter=True, callback=self.parse_finviz, cb_kwargs=dict(ticker=ticker))

    def parse_finviz(self, response, ticker):
        company_type = response.css('td.fullview-links')[1]
        sector = company_type.css('a::text')[0].get()
        industry = company_type.css('a::text')[1].get()

        info_table = response.css('table.snapshot-table2')
        insider_own = info_table.css('tr:nth-child(1) > td:nth-child(8) > b::text').get()
        shs_outstanding = info_table.css('tr:nth-child(1) > td:nth-child(10) > b::text').get()
        market_cap = info_table.css('tr:nth-child(2) > td:nth-child(2) > b::text').get()
        shs_float = info_table.css('tr:nth-child(2) > td:nth-child(10) > b::text').get()
        income = info_table.css('tr:nth-child(3) > td:nth-child(2) > b::text').get()
        short_float_check = info_table.css('tr:nth-child(3) > td:nth-child(10) > b')
        if len(short_float_check.css('span')) != 0:
            short_float = short_float_check.css('span::text').get()
        else:
            short_float = info_table.css('b::text').get()
        short_ratio = short_float_check.css('tr:nth-child(4) > td:nth-child(10) > b::text').get()

        ticker['sector'] = sector
        ticker['industry'] = industry
        ticker['insider_own'] = insider_own
        ticker['shs_outstanding'] = shs_outstanding
        ticker['market_cap'] = market_cap
        ticker['shs_float'] = shs_float
        ticker['income'] = income
        ticker['short_float'] = short_float
        ticker['short_ratio'] = short_ratio

        yield ticker

