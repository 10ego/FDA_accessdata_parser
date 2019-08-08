from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

class accessdata_parser():
	def __init__(self, search_term):
		self.search_term = search_term
		querypage = "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=BasicSearch.process"
		headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type':'application/x-www-form-urlencoded'} 
		payload = "searchterm={}".format(search_term.replace(' ','+'))
		print('payload:', payload)
		r = requests.post(querypage, headers = headers, data = payload)
		self.fda_queried_data = r.content.decode("utf-8")
		print("Raw HTML from FDA ready (data size:{})".format(len(self.fda_queried_data)))

	def build_soup(self):
		raw_soup = BeautifulSoup(self.fda_queried_data, 'html.parser')
		print("raw soup size:", len(raw_soup))
		drug_hits = raw_soup.find_all("a", title="Click to expand drug name")
		drug_hits_links = raw_soup.find_all("ul", class_="collapse")
		print("Found hit size: ",len(drug_hits), len(drug_hits_links))
		all_li = [x for x in raw_soup.find_all('li')]
		hits=[]
		link_hits=[]
		for drug in drug_hits:
			drug_data = BeautifulSoup(str(drug), 'html.parser')
			for string in drug_data.stripped_strings:
				hits.append(string)
		for li in all_li:
			li_data = BeautifulSoup(str(li), 'html.parser')
			for href in li_data.find_all('a', href=True):
				link_hits.append(href['href'])
		try:
			p = hits.index(self.search_term.upper())
			print("Found term at", p)
			start_link = drug_hits_links[p].find_all('a', href=True)[0]['href']
			
			link_range_start = link_hits.index(start_link)
			if len(drug_hits_links)>1:
				end_link = drug_hits_links[p+1].find_all('a', href=True)[0]['href']
				link_range_end = link_hits.index(end_link)
				return link_hits[link_range_start:link_range_end]
			else:
				return [link_hits[link_range_start]]
			
		except Exception as e:
			print("Did not find term")
			print(e.args)
			return []

	def parse_datatable(self, datatable):
		joup = BeautifulSoup(str(datatable),'html.parser')
		d = {}
		for tr in joup.find_all('tr'):
			data = BeautifulSoup(str(tr), 'html.parser')
			if data.find_all('th'):
				tmp = []
				for th in data.find_all('th'):
					if not th.string in d:
						tmp.append(th.string)
						d[th.string] = []
			if data.find_all('td'):
				c = 0
				for td in data.find_all('td'):
					s = [string for string in td.stripped_strings]
					if not s:
						s.append("None")
					for x in s:
						d[tmp[c]].append(x)
					c+=1
		return d

	async def fetch(self, session, url):
		async with session.get(url) as resp:
			if resp.status != 200:
				resp.raise_for_status()
			return await resp.text()

	async def async_request(self, session, urls):
		loop = asyncio.get_event_loop()
		results = await asyncio.gather(*[loop.create_task(self.fetch(session, url)) for url in urls])
		return results
	
	async def async_process(self, urls):
		async with aiohttp.ClientSession() as session:
			htmls = await self.async_request(session, urls)
			return htmls

	def build_productlist(self):
		productlist = {}
		counter = 0
		pot = self.build_soup()
		if pot:
			urls = ["https://www.accessdata.fda.gov"+url for url in pot]
			parser_loop = asyncio.new_event_loop()
			asyncio.set_event_loop(parser_loop)
			print("Parser loop initialized", parser_loop)
			parsed_htmls = parser_loop.run_until_complete(self.async_process(urls))
			parser_loop.close()
			print("Parsed {} htmls".format(len(parsed_htmls)))
			for link in parsed_htmls:
				soup2 = BeautifulSoup(link, 'html.parser')
				app_id = [string for string in soup2.find_all('span', class_='appl-details-top')[0].stripped_strings][0]
				company_name = [string for string in soup2.find_all('span', class_='appl-details-top')[1].stripped_strings][0]
				data_tables = soup2.find_all('table')
				productlist[urls[counter][-6:]] = [{"company_name":company_name, "appID": app_id}]
				for table in data_tables:
					productlist[urls[counter][-6:]].append(self.parse_datatable(table))
				counter+=1
		return productlist
