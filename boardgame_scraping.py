import requests
from bs4 import BeautifulSoup
import time
from time import sleep
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from email.message import EmailMessage
import ssl
import smtplib

my_file = open("wish_list.txt", "r")
my_file_data = my_file.read()
wish_list = my_file_data.split("\n")
my_file.close()
# print(wish_list)

# found_list = []
content = ""

def scrape_games(base_url, query_strings):
    page = 1
    # last_page = 0
    stop = 0
    game_was_found = 0
    # counter = 0
    found_game_list = []
    # while int(page) > int(last_page):
    while stop != 1:
        url = "?page="
        response = requests.get(f"{base_url}{url}{page}{query_strings}")
        print(f"Now scraping {base_url}{url}{page}{query_strings}...")
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("li", class_="zg-product")
        
        for game in games:
            # title = game.find("h2").find("a")["title"]
            # price = float(game.find("div", class_="zg-price-box-now")["data-now"])

            #found_list_temp = find_wish_game(wish_list, get_title(game))
            game_was_found = find_wish_game(wish_list, get_title(game))
            #for found_list_temp_item in found_list_temp:
            if game_was_found == 1:
                found_game_data = get_product_id(game), get_title(game), get_price(game), get_rrp_price(game), get_link(game)
                found_game_list.append(found_game_data)
                # found_game = 1

            # price = get_price(game)
            # rrp_price = get_rrp_price(game)
            # if rrp_price != 0:
            # 	if price / rrp_price < 0.6:
            # 		print(f"""
            # 			This game is good price, 50% cheaper!
            # 			Title: {get_title(game)}
            # 			Price: {get_price(game)}
            # 			RRP Price: {get_rrp_price(game)}
            # 			""")
        # last_page += 1
        # next_btn = soup.find_all(lambda tag: tag.name == 'li' and tag.get('class') == ['auto'])

        ## Find the disabled button
        disabled_btn = soup.find("li", class_="mobile-hidden auto disabled")

        ## To check if the found disabled button is Next button
        ## If yes, it means this is the last page, so put a stop sign
        if disabled_btn:
            next_btn = disabled_btn.findChildren()
            for child in next_btn:
                # print(child.text)
                # print("----")
                if(child.text == "Next"):
                    stop = 1


        page += 1
        # page = next_btn[-1].find("a")["data-page"] if next_btn else 0
        # print(page)
        sleep(4)

    # print(f"\n\nZatu found game list = {found_game_list}")
    
    return found_game_list

def scrape_games_chaos(base_URL):

    # The ChromeDriverManager didn't work since 10 Aug 2024, could be an issue from the official webdriver software
    # s = Service(ChromeDriverManager().install())
    # s = Service("C:\\Windows\\System32\\chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument("-headless")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_experimental_option("detach", True)

    # driver = webdriver.Chrome(service=s, options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(base_URL)
    driver.maximize_window()
    # next_button = driver.find_element("xpath", "//a[contains(@title, 'Next Page')]")

    agreement_button = driver.find_element("xpath", "//span[contains(@class, 'cookie-banner__accept')]")
    agreement_button.click()

    found_game_list = []
    game_was_found = 0

    while (True):

        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            current_page = soup.find("li", class_="page_no sel").find("a")["title"]
            print(f"Now is scraping {base_URL} {current_page}...")
        except:
            print(f"Now is scraping {base_URL} Page 1... \nNo next page button")
        
        games = soup.find_all("div", class_="prod-list__element view_default")

        for game in games:
            game_was_found = find_wish_game(wish_list, get_title_chaos(game))

            if game_was_found == 1:
                found_game_data = get_title_chaos(game), get_price_chaos(game), get_old_price_chaos(game), get_rrp_price_chaos(game), get_save_price_chaos(game), get_link_chaos(game)
                found_game_list.append(found_game_data)

        try:
            next_button = driver.find_element("xpath", "//li[contains(@class, 'next')][.//a]")
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(2)
            next_button.click()
            time.sleep(2)
        except:
            print("Last page reached")
            break

        # time.sleep(1000)

    # print(f"\n\nChaos found game list = {found_game_list}")

    return found_game_list

def get_product_id(game):
    return int(game["data-product-id"])

def get_title(game):
    return game.find("h2").find("a")["title"]

def get_title_chaos(game):
    return game.find("a", class_="prod-el__link")["title"]

def get_price(game):
    return float(game.find("div", class_="zg-price-box-now")["data-now"])

def get_price_chaos(game):
    return game.find("span", class_="prod-el__pricing-price prod-el__pricing-price--sale").get_text()

def get_old_price_chaos(game):
    return game.find("span", class_="prod-el__pricing-small").get_text()

def get_rrp_price(game):
    if game.find("del", class_="zg-price-box-was"):
        rrp_price = float(game.find("del", class_="zg-price-box-was")["data-was"])
        return rrp_price
    else:
        return 0
    
def get_rrp_price_chaos(game):
    ## There are two prices with same span class name, first one is old price, second one is rrp price
    prices = game.find_all("span", class_="prod-el__pricing-small")
    if (len(prices) > 1):
        return prices[1].get_text()
    else:
        return "N/A"
    
def get_save_price_chaos(game):
    return game.find("span", class_="prod-el__pricing-save").get_text()

def get_link(game):
    return game.find("a", class_="zg-product-image")["href"]

def get_link_chaos(game):
    return "https://www.chaoscards.co.uk" + game.find("a", class_="prod-el__link")["href"]

def find_wish_game(wish_list, game):
    game_was_found = 0
    for wish_list_game in wish_list:
        ## The first part is to check if the wish game name is in the retail game name on word basis
        ## The second part is in case the retail game name is with a colon
        if f" {wish_list_game.lower()} " in f" {game.lower()} " or f" {wish_list_game.lower()}:" in f" {game.lower()} ":
            if 'insert' not in game.lower() and 'roleplaying' not in game.lower():
                game_was_found = 1
    return game_was_found


def setup_email(found_game_list, category):
    if len(found_game_list) <= 0:
        return
    
    else:
        if category == "zatu_outlet":
            category_type = "Zatu Outlet"
        elif category == "zatu_sale":
            category_type = "Zatu Sale"
        elif category == "chaos_damaged_items":
            category_type = "Chaos Cards Damaged Items"
        elif category == "chaos_clearance":
            category_type = "Chaos Cards Clearance"
        else:
            category_type = "Unknown"

        # content = content + ["\nCategory: {category_type}\nName: {name}\nPrice: {price}\nRRP: {rrp}\nSave: {save_price}\nLink: {link}\n\n".format(category_type = category_type, name = found_game[0], price = found_game[1], rrp = found_game[2], save_price = found_game[3], link = found_game[4]) for found_game in found_game_list]
        # content = "".join(content)

        global content

        if category == "zatu_outlet" or category == "zatu_sale":
            for found_game in found_game_list:
                content = content + f"\nCategory: {category_type}\nID: {found_game[0]}\nName: {found_game[1]}\nPrice: {found_game[2]}\nRRP: {found_game[3]}\nLink: {found_game[4]}\n\n"
        elif category == "chaos_damaged_items" or category == "chaos_clearance":
            for found_game in found_game_list:
                content = content + f"\nCategory: {category_type}\nName: {found_game[0]}\nPrice: {found_game[1]}\nOld price: {found_game[2]}\nRRP: {found_game[3]}\nSave: {found_game[4]}\nLink: {found_game[5]}\n\n"
        else:
            content = content + f"Error:No suitable category found, please contact admin"
        
        # print(content_header)
        # print(content)

    return content



def send_email(content):
    # if found_game == 1:
    if len(content) <= 0:
        print("No game is found")
        return
    
    email_sender = 'codeguysean@gmail.com'

    # Testing environment
    # email_password = os.getenv('python_gmail_password')

    # Live environment
    email_password = os.environ["GMAIL_PWD"]
    
    email_receiver = 'seanbeanli@gmail.com'
    smtp_server = 'smtp.gmail.com'
    port = 465

    # items = ["\nID: {id}\nName: {name}\nPrice: {price}\nRRP: {rrp}\nLink: {link}\n\n".format(id = found_list_game[0], name = found_list_game[1], price = found_list_game[2], rrp = found_list_game[3], link = found_list_game[4]) for found_list_game in found_list]
    # items = "".join(items)

    # if base_url == "https://www.board-game.co.uk/category/outlet-store/":
    #     subject = 'Wish list games found in Zatu Games Outlet'
    # elif base_url == "https://www.board-game.co.uk/buy/sale/":
    #     subject = 'Wish list games found in Zatu Games Sale'
    # else:
    #     subject = 'Wish List games found'

    subject = "Wish List Games Found"

    body = """
    Found games details:

    {0}

    """.format(content)

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()


    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, em.as_string())

    print("Games found, email has been sent")
    
    # else:
    #     return print("No game is found.")

setup_email(scrape_games("https://www.board-game.co.uk/category/outlet-store/", ""), "zatu_outlet")
setup_email(scrape_games("https://www.board-game.co.uk/buy/outlet-board-games/", "&oos=hide"), "zatu_outlet")
setup_email(scrape_games("https://www.board-game.co.uk/buy/sale/", "&category=board-games"), "zatu_sale")
setup_email(scrape_games_chaos("https://www.chaoscards.co.uk/shop/damaged-items"), "chaos_damaged_items")
setup_email(scrape_games_chaos("https://www.chaoscards.co.uk/shop/clearance/sort/newly-listed/sale-category/board-games"), "chaos_clearance")
send_email(content)