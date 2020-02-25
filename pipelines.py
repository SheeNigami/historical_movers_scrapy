# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter
import datetime


class WaybackmachineHistoricalMoversPipeline(object):
    Types = ['premarket-gainers', 'premarket-losers', 'after-hours-gainers', 'after-hours-losers']

    def open_spider(self, spider):
        self.files = dict([(name, open('./scraped/'+name+'.csv', 'wb+')) for name in self.Types])
        self.exporters = dict([(name, CsvItemExporter(self.files[name], include_headers_line=True)) for name in self.Types])
        for exporter_key in self.exporters.keys():
            self.exporters[exporter_key].fields_to_export = ['datetime', 'symb', 'company', 'sector', 'industry',
                                                             'market_cap', 'income', 'insider_own', 'shs_outstanding',
                                                             'shs_float', 'short_float', 'short_ratio', 'last',
                                                             'volume', 'change_pct']

        [e.start_exporting() for e in self.exporters.values()]

    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        if item.get('session') == 'premarket':
            # Get datetime and figure out what date to log
            item_datetime = item.get('datetime')
            if item_datetime.time() < datetime.time(9, 30, 0):
                item['datetime'] = item_datetime.date() - datetime.timedelta(days=1)
                item['datetime'] = item_datetime.strftime("%Y-%m-%d")
            else:
                item['datetime'] = item_datetime.strftime("%Y-%m-%d")

            # Write appropriate file
            if item.get('mover') == 'Top Gaining Stocks':
                self.exporters['premarket-gainers'].export_item(item)
            else:
                self.exporters['premarket-losers'].export_item(item)
        else:
            # Get datetime and figure out what date to log
            item_datetime = item.get('datetime')
            if item_datetime.time() < datetime.time(21, 30, 0):
                item['datetime'] = item_datetime.date().strftime("%Y-%m-%d")
            else:
                item['datetime'] = item_datetime.date() - datetime.timedelta(days=1)
                item['datetime'] = item_datetime.strftime("%Y-%m-%d")

            # Write appropriate file
            if item.get('mover') == 'Top Gaining Stocks':
                self.exporters['after-hours-gainers'].export_item(item)
            else:
                self.exporters['after-hours-losers'].export_item(item)
        return item
