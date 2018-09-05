from django.core.management.base import BaseCommand
from django.conf import settings
import json

class Command(BaseCommand):

    help = 'pulls prices and stores them in a DB'

    def handle(self, *args, **options):
        from history.poloniex import poloniex
        from history.models import Price
        import time

        poo = poloniex(settings.API_KEY, settings.API_SECRET)
        price = poo.returnTicker()
        price = json.dumps(price)
        price = json.loads(price)
        for ticker in price:
            try:
                print(ticker)
                this_price = ticker['last_traded_price']
                this_volume = float(ticker['volume_24h']) * float(this_price)
                the_str = str(ticker['currency_pair_code']) + ',' + str(time.time()) + ',' + str(this_price) + ", " + str(this_volume)
                print("(pp)"+the_str)
                p = Price()
                p.price = this_price
                p.volume = this_volume
                p.lowestask = ticker['high_market_ask']
                p.highestbid = ticker['low_market_bid']
                p.symbol = str(ticker['currency_pair_code'])
                p.created_on_str = str(p.created_on)
                p.save()
            except Exception as e:
                print(e)