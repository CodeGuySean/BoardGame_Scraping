import requests
from bs4 import BeautifulSoup
from time import sleep
import os

from email.message import EmailMessage
import ssl
import smtplib

all_games = []
found_list = []
my_file = open("wish_list.txt", "r")
my_file_data = my_file.read()
wish_list = my_file_data.split("\n")
my_file.close()
found_game = 0
# print(wish_list)

def scrape_games(base_url):
    page = 1
    last_page = 0
    # counter = 0
    while int(page) > int(last_page):
        url = "?page="
        response = requests.get(f"{base_url}{url}{page}")
        print(f"Now scraping {base_url}{url}{page}...")
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("li", class_="zg-product")
        
        for game in games:
            # title = game.find("h2").find("a")["title"]
            # price = float(game.find("div", class_="zg-price-box-now")["data-now"])

            found_list_temp = find_wish_game(wish_list, get_title(game))
            for found_list_temp_item in found_list_temp:
                found_game_data = get_product_id(game), get_title(game), get_price(game), get_rrp_price(game), get_link(game)
                found_list.append(found_game_data)
                found_game = 1


            game_data = (get_product_id(game), get_title(game), get_price(game), get_rrp_price(game))
            all_games.append(game_data)


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
        last_page += 1
        next_btn = soup.find_all(lambda tag: tag.name == 'li' and tag.get('class') == ['auto'])
        page = next_btn[-1].find("a")["data-page"] if next_btn else None
        # print(page)
        sleep(5)
        # counter += 1
        # if counter == 3:
        # 	break

    # print(found_list)
    # print(all_games)
    send_email(found_game, found_list)


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
    found_list = []
    for wish_list_game in wish_list:
        if wish_list_game in game:
            found_list.append(wish_list_game)
    return found_list

def send_email(found_game, found_list):
    if found_game == 1:
        email_sender = 'seanbeanli@gmail.com'
        # email_password = os.getenv('python_gmail_password')
        email_password = os.environ["GMAIL_PWD"]
        print(email_password)
        email_receiver = 'seanbeanli@gmail.com'
        smtp_server = 'smtp.gmail.com'
        port = 465

        items = ["\nID: {id}\nName: {name}\nPrice: {price}\nRRP: {rrp}\nLink: {link}\n\n".format(id = found_list_game[0], name = found_list_game[1], price = found_list_game[2], rrp = found_list_game[3], link = found_list_game[4]) for found_list_game in found_list]
        items = "".join(items)

        subject = 'Wish list games found in Zatu Games Outlet'
        body = """
        Found games details:

        {0}

        """.format(items)

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()


        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, em.as_string())
    else:
        return print("No game is found.")

# scrape_games("https://www.board-game.co.uk/board-game-top-20-chart/")
# scrape_games("https://www.board-game.co.uk/category/board-games/?popular=best-sellers")
scrape_games("https://www.board-game.co.uk/category/outlet-store/")