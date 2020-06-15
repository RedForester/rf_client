import asyncio
import os

from rf_api_client import RfApiClient
from rf_client import Wrapper

client = Wrapper(RfApiClient(
    username=os.getenv('USERNAME'),
    password=os.getenv('PWD')
))


@client.session
async def task(session):
    m = await session.maps.load_map(os.getenv('MAP_ID'))
    print(m.users)


async def task_with():
    async with client as s:
        data = await s.maps.load_map(os.getenv('MAP_ID'))
        print(data.users)


loop = asyncio.get_event_loop()

loop.run_until_complete(task())
loop.run_until_complete(task_with())
loop.close()