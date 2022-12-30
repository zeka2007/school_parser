import requests
from bs4 import BeautifulSoup
import bot_sql

sql = bot_sql.MySQL()

class Parser():
	def __init__(self):
		self.agent = 'Mozilla/5.0 (X11; Linux i686; rv:80.0) Gecko/20100101 Firefox/80.0'
		self.URL = 'https://schools.by/login'
	
	def login(self, user_id: int, login: str, password: str):
		URL = 'https://schools.by/login'
		headers = {
			'user-agent': self.agent,
			'Referer': URL
		}

		client = requests.session()

		#Retrieve the CSRF token first
		req = client.get('https://schools.by/login')
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

	def is_login(self, user_id):
		data = sql.get_login_data(user_id)
		if data is None:
			return False
		if data['csrf_token'] is None or data['session_id'] is None:
			return False
		cookies = {
			'csrftoken': data['csrf_token'],
			'sessionid': data['session_id'],
			'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
			}
		get = requests.get(self.URL, 
				headers={'user-agent': self.agent},
				cookies=cookies)
		if get.url == self.URL:
			return False
		return True

	def get_name(self, user_id):
		if not self.is_login(user_id):
			return False

		data = sql.get_login_data(user_id)
		cookies = {
				'csrftoken': data['csrf_token'],
				'sessionid': data['session_id'],
				'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
				}

		req = requests.get(self.URL,
				headers={'user-agent': self.agent},
				cookies=cookies).content
		soup = BeautifulSoup(req, features="html.parser")
		name = soup.find('div', {'class': 'title_box'})
		name = name.find('h1').text
		return name
