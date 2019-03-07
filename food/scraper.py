import urllib.request, csv, re
from common import logger
from .model import Restaurant, Category, Item
from bs4 import BeautifulSoup
#from http.cookiejar import CookieJar
from slugify import slugify


def insert_in_database(restaurant_name, address, menu):
    restaurant = Restaurant.select().where(Restaurant.name == restaurant_name)
    if not restaurant:
        restaurant = Restaurant.insert(
            name=restaurant_name,
            address=address,
            slug=slugify(restaurant_name)
        ).execute()
        for category_name, items in menu.items():
            category = Category.select().where((Category.name == category_name) & (Category.restaurant == restaurant))
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
    with open("food/data/{slug}.csv".format(slug=restaurant_slug), "w") as f:
        f.write("# Restaurant: {name}\n# Address: {address}\n".format(name=restaurant, address=address))
        fieldnames=["category", "name", "description", "price"]
        csv_writer = csv.DictWriter(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        #csv_writer.writeheader()
        for category in menu.keys():
            for item in menu[category]:
                csv_writer.writerow({
                    "category": category,
                    "name": item["name"],
                    "description": item["description"],
                    "price": item["price"]
                })


def read_csv(file_csv):
    f = open(file_csv, 'r')
    name, address, *rest = f.readlines()
    data = {
        "name": name.split(":")[1].strip(),
        "address": address.split(":")[1].strip(),
        "menu": {}
    }
    f.close()

    with open(file_csv, 'r') as f:
        fieldnames=["category", "name", "description", "price"]
        csv_reader = csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        for row in csv_reader:
            if "#" in row["category"]:
                continue

            item = {
                "name": row["name"],
                "description": row["description"],
                "price": float(row["price"])
            }
            if row["category"] not in data["menu"]:
                data["menu"][row["category"]] = [item]
            else:
                data["menu"][row["category"]].append(item)
            
        return data


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
                    
            try:
                menu[category].append({
                    "name": get_attribute(".product-title"),
                    "description": get_attribute(".product-description"),
                    "price": float(re.findall("[-+]?[0-9]*\.?[0-9]+", get_attribute(".product-price").replace(',', '.'))[0])
                })
            except:
                logger.debug("Failed to extract item information from page...")

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
            try:
                menu[category].append({
                    "name": get_attribute(".product-title"),
                    "description": get_attribute(".product-description"),
                    "price": float(re.findall("[-+]?[0-9]*\.?[0-9]+", get_attribute(".product-price").replace(',', '.'))[0])
                })
            except:
                logger.debug("Failed to extract item information from page...")

    #print_menu(menu)
    return {
        'name': name,
        'address': address,
        'menu': menu
    }