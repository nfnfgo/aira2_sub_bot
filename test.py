import asyncio
import json

from services import aria


async def main():
    info = await aria.tell_stopped(keys=['gid'])
    text = json.dumps(info)
    with open('return_text.json', 'w') as f:
        f.write(text)


if __name__ == '__main__':
    asyncio.run(main())
