import requests
from bs4 import BeautifulSoup
import bot_sql

sql = bot_sql.MySQL()

class Parser():
	def __init__(self):
		self.agent = 'Mozilla/5.0 (X11; Linux i686; rv:80.0) Gecko/20100101 Firefox/80.0'
	
	def login(self, user_id: int, login: str, password: str):
		URL = 'https://schools.by/login'
		headers = {
			'user-agent': self.agent,
			'Referer': URL
		}

		client = requests.session()

		#Retrieve the CSRF token first
		req = client.get('https://schools.by/login')
		print(req.content)
		soup = BeautifulSoup(req.content, features="html.parser")
		csrftoken = soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

		login_data = {
			'csrfmiddlewaretoken': csrftoken,
			'username': login,
			'password': password,
			'|123': '|123'
		}
		r = client.post(
			URL,
			data=login_data, 
			headers=headers, 
			allow_redirects=True,
			verify=False)
		if r.url == URL:
			return False

		for resp in r.history:

			sql.set_login_data(
				user_id,
				{
				'login': None,
				'password': None,
				'csrf_token': resp.cookies['csrftoken'],
				'session_id': resp.cookies['sessionid']
				}
				)
		return True
