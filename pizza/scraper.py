import urllib.request, csv
from common import logger
from .model import Restaurant, Category, Item
from bs4 import BeautifulSoup
#from http.cookiejar import CookieJar
from slugify import slugify

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


def insert_in_database(restaurant_name, address, menu):
    restaurant = Restaurant.select().where(Restaurant.name == restaurant_name)
    if not restaurant:
        restaurant = Restaurant.insert(
            name=restaurant_name,
            address=address,
            slug=slugify(restaurant_name)
        ).execute()
        for category_name, items in menu.items():
            category = Category.select().where(Category.name == category_name)
            if not category:
                category = Category.insert(
                    name=category_name,
                    restaurant=restaurant,
                    slug=slugify(category_name)
                ).execute()
                for item in items:
                    try:
                        Item.insert(
                            name=item["name"],
                            slug=slugify(item["name"]),
                            description=item["description"],
                            price=item["price"],
                            category=category
                        ).execute()
                    except Exception as e:
                        logger.error("Failed to insert item {name}!".format(name=item["name"]))
                        logger.error(e)

def generate_csv(restaurant, address, menu):
    logger.debug("Generating csv file for Restaurant {name}...".format(name=restaurant))
    restaurant_slug = slugify(restaurant)
    with open("pizza/data/{slug}.csv".format(slug=restaurant_slug), "w") as f:
        f.write("# Restaurant: {name}\n# Address: {address}\n".format(name=restaurant, address=address))
        fieldnames=["category", "name", "description", "price"]
        csv_writer = csv.DictWriter(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csv_writer.writeheader()
        for category in menu.keys():
            for item in menu[category]:
                csv_writer.writerow({
                    "category": category,
                    "name": item["name"],
                    "description": item["description"],
                    "price": item["price"]
                })


def scrape_and_download(url):
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


def scrape(html_file):
    contents = open(html_file, 'r')

    # Initialize parser
    soup = BeautifulSoup(contents, 'html.parser')
    name = soup.find("h1", attrs={"class": "infoTextBlock-item-title"}).get_text().strip()
    address = soup.find("p", attrs={"class": "restInfoAddress"}).get_text().strip() 
    address = ' '.join(address.split())

    # Scrape menu data
    menu = {}
    menuCards = soup.find("div", attrs={"class": "menuCard-contents"})
    sections = menuCards.findAll("section")
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
    return {
        'name': name,
        'address': address,
        'menu': menu
    }