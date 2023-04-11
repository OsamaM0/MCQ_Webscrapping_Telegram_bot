from bs4 import BeautifulSoup
import requests
import random
import time


class Scrapper:

  # Define the URL and headers to use for the request
  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
  }

  # Define a list of user agent strings to use for the request
  user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
  ]

  # Define List Of all Send URL
  url_list = {}

  # # Get list of proxies to use for the request
  # def get_free_proxies():
  #     url = "https://free-proxy-list.net/"
  #     # request and grab content
  #     soup = BeautifulSoup(requests.get(url).content, 'html.parser')
  #     # to store proxies
  #     proxies = []
  #     for row in soup.find("table", attrs={"class": "table-striped"}).find_all("tr")[1:]:
  #         tds = row.find_all("td")
  #         try:
  #             ip = tds[0].text.strip()
  #             port = tds[1].text.strip()
  #             proxies.append(str(ip) + ":" + str(port))
  #         except IndexError:
  #             continue
  #     return proxies

  # Send a request with a random proxy and user agent
  def send_request(self, url, proxyes: list = None):
    # Pick Random Proxy & User_agent
    #proxy = random.choice(proxyes)
    headers = {'User-Agent': random.choice(self.user_agents)}

    # Get HTML of Desierd Url
    try:
      if proxyes is None:
        response = requests.get(url, headers=headers)
      else:
        response = requests.get(url, headers=headers, proxies=proxyes)
      if response.status_code == 200:
        print(response)
        return response

    except requests.exceptions.RequestException as e:
      print("Exception in requist  ", e)
    except:
      return None

  def get_responce(self, url):

    print("==================================")
    print("Quizz Scrapping Start")
    content = None
    url.strip()
    try:
      content = self.url_list[url]
      print("Old Link")
    except:
      while not content:
        res = self.send_request(url)
        if not res:
          # Wait for a random amount of time before trying again
          time.sleep(random.uniform(1, 3))
        else:
          content = res.text
        print("Try")

      print("New Link")
      self.url_list[url] = content

    soup = BeautifulSoup(content, 'html.parser')
    return soup
