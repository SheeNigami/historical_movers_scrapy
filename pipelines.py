# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class WaybackmachineHistoricalMoversPipeline(object):

    def open_spider(self, spider):
        self.pregain = open('', 'w')
        self.preloss = open('', 'w')
        self.aftergain = open('', 'w')
        self.afterloss = open('', 'w')

    def close_spider(self, spider):
        self.pregain.close()
        self.preloss.close()
        self.aftergain.close()
        self.afterloss.close()

    def process_item(self, item, spider):
        datetime = item.get('datetime')
        # Change datetime to date of market
        if item.get('session') == 'pre-market':
            if item.get('mover'):

            else:
        else:
            if item.get('mover'):

            else:
