import requests
from bs4 import BeautifulSoup
from time import sleep
import os

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

def scrape_games(base_url):
    page = 1
    # last_page = 0
    stop = 0
    game_was_found = 0
    # counter = 0
    found_game_list = []
    # while int(page) > int(last_page):
    while stop != 1:
        url = "?page="
        response = requests.get(f"{base_url}{url}{page}")
        print(f"Now scraping {base_url}{url}{page}...")
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

    # print(found_list)
    # print(all_games)
    # send_email(game_was_found, found_game_list, base_url)
    
    return found_game_list

def get_product_id(game):
    return int(game["data-product-id"])

def get_title(game):
    return game.find("h2").find("a")["title"]

def get_price(game):
    return float(game.find("div", class_="zg-price-box-now")["data-now"])

def get_rrp_price(game):
    if game.find("del", class_="zg-price-box-was"):
        rrp_price = float(game.find("del", class_="zg-price-box-was")["data-was"])
        return rrp_price
    else:
        return 0

def get_link(game):
    return game.find("a", class_="zg-product-image")["href"]

def find_wish_game(wish_list, game):
    game_was_found = 0
    for wish_list_game in wish_list:
        ## The first part is to check if the wish game name is in the retail game name on word basis
        ## The second part is in case the retail game name is with a colon
        if f" {wish_list_game.lower()} " in f" {game.lower()} " or f" {wish_list_game.lower()}:" in f" {game.lower()} ":
            if 'insert' not in game.lower():
                game_was_found = 1
    return game_was_found


def setup_email(found_game_list, category):
    if len(found_game_list) <= 0:
        return
    
    else:
        if category == "outlet":
            category_type = "Zatu Outlet"
        elif category == "sale":
            category_type = "Zatu Sale"
        else:
            category_type = "Zatu"

        # content = content + ["\nCategory: {category_type}\nName: {name}\nPrice: {price}\nRRP: {rrp}\nSave: {save_price}\nLink: {link}\n\n".format(category_type = category_type, name = found_game[0], price = found_game[1], rrp = found_game[2], save_price = found_game[3], link = found_game[4]) for found_game in found_game_list]
        # content = "".join(content)

        global content

        for found_game in found_game_list:
            content = content + f"\nCategory: {category_type}\nID: {found_game[0]}\nName: {found_game[1]}\nPrice: {found_game[2]}\nRRP: {found_game[3]}\nLink: {found_game[4]}\n\n"

        # print(content_header)
        # print(content)

    return content



def send_email(content):
    # if found_game == 1:
    if len(content) <= 0:
        print("No game is found")
        return
    
    email_sender = 'codeguysean@gmail.com'
    # email_password = os.getenv('python_gmail_password')
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

    subject = "Wish List games found in Zatu"

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

setup_email(scrape_games("https://www.board-game.co.uk/category/outlet-store/"), "outlet")
setup_email(scrape_games("https://www.board-game.co.uk/buy/sale/"), "sale")
send_email(content)