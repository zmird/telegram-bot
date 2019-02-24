import urllib.request, csv
from common import logger
from .model import Restaurant, Category, Item
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar

def print_menu(menu):
    with open("menu.csv", "w") as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for category in menu.keys():            
            for product in menu[category]:
                writer.writerow([
                    category,
                    product["name"],
                    product["description"],
                    product["price"]
                ])


def insert_csv_in_database():
    logger.debug("Inserting data in database....")
    restaurant = Restaurant.select().where(Restaurant.name == "Pizzeria del Rondone")
    if not restaurant:
        restaurant = Restaurant.insert(
            name="Pizzeria del Rondone",
            address="Via del Rondone, Bologna, 40122"
        ).execute()
    with open("pizza/menu.csv") as f:
        csv_reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            category = Category.select().where(Category.name == row[0])
            if not category:
                category = Category.insert(
                    name=row[0],
                    restaurant=restaurant
                ).execute()
            
            Item.insert(
                name=row[1],
                description=row[2],
                price=row[3],
                category=category
            ).execute()


def insert_menu_database(restaurant, address, menu):
    restaurant = Restaurant.select().where(Restaurant.name == restaurant)
    if not restaurant:
        restaurant = Restaurant.insert(
            name=restaurant,
            address=address
        ).execute()
    for category, items in menu.items():
        category = Category.select().where(Category.name == category)
        if not category:
            category = Category.insert(
                name=category,
                restaurant=restaurant
            ).execute()
        for item in items:
            Item.insert(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                category=category
            ).execute()




def scrape(url):
    response = urllib.request.urlopen(url)
    contents = response.read().decode("utf-8")

    # Initialize parser
    soup = BeautifulSoup(contents, 'html.parser')
    menus = soup.find("div", attrs={"class": "menuCard-contents"})
    sections = menus.findAll("section")

    # Scrape menu data
    menu = {}
    for section in sections:
        category = section.select_one("h3").get_text().strip()
        menu[category] = []

        for product in section.findAll("div", attrs={"class": "product"}):
            def get_attribute(selector):
                try:
                    attribute = product.select_one(selector).get_text().strip()
                except:
                    attribute = None
                finally:
                    return attribute

            menu[category].append({
                "name": get_attribute(".product-title"),
                "description": get_attribute(".product-description"),
                "price": get_attribute(".product-price")
            })

    #print_menu(menu)
    return menu
