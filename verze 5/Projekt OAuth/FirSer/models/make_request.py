import aiohttp

async def get_request_with_params(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=data) as resp:
            return await resp.text()

async def get_request_with_headers(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=data) as resp:
            return await resp.json()	
                
async def get_request(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			return await resp.text()

async def post_request_with_files(url, data, ClientID, ClientSecret):
	async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(ClientID,ClientSecret)) as session:
		async with session.post(url, data=data) as resp:
			return await resp.json()