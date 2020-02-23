# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Ticker(Item):
    datetime = Field()
    session = Field()
    mover = Field()

    symb = Field()
    company = Field()
    sector = Field()
    industry = Field()
    market_cap = Field()
    income = Field()
    insider_own = Field()
    shs_outstanding = Field()
    shs_float = Field()
    short_float = Field()
    short_ratio = Field()
    last = Field()
    volume = Field()
    changePct = Field()

