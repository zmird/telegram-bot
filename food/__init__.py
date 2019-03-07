from .model import *
from .helper import help
from .scraper import scrape, generate_csv, insert_in_database, read_csv

from os import listdir
import re

"""
for f in listdir("food/webpages"):
    if re.search(".*.html", f):
        results = scrape("food/webpages/{file_name}".format(file_name=f))
        generate_csv(results['name'], results['address'], results['menu'])
        insert_in_database(results['name'], results['address'], results['menu'])
"""

for f in listdir("food/data"):
    if re.search(".*.csv", f):
        results = read_csv("food/data/{}".format(f))
        insert_in_database(results['name'], results['address'], results['menu'])


Restaurant.update({Restaurant.selected: True}).where(Restaurant.name == "Pizzeria Vesuvia").execute()
