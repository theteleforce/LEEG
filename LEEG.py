from aiohttp.client_exceptions import ClientConnectionError
import asyncio
import constants as c
import json
from psutil import process_iter
import willump
from win32_nonsense import swap_monitors


# avert your eyes
globals()["in_game"] = False
DEBUG = False


import logging
if DEBUG:
    logging.basicConfig(format="[%(asctime)s] %(levelname)s | %(message)s", level=logging.WARNING)
else:
    logging.basicConfig(filename=c.LOG_FILE, format="[%(asctime)s] %(levelname)s | %(message)s", level=logging.ERROR)


async def nothing(data):
    pass


async def dump_request(data):
    print("\n\n Got new request:")
    print(json.dumps(data, indent=4, sort_keys=True))


async def game_state_handler(data):
    global in_game
    try:
        game_phase = data["data"]["phase"]
        logging.warning("got state request {}".format(game_phase))
        if game_phase == "GameStart" and not in_game or game_phase in c.END_GAME_STATES and in_game:
            in_game = not in_game
            # swap_monitors()
    except:
        pass


def in_leeg_game():
    for process in process_iter():
        if process.name() in ["League of Legends (TM) Client", "League of Legends.exe"]:
            logging.warning("found existing game {}".format(process.name))
            return True
    return False


async def main():
    global in_game
    if in_leeg_game():
        while True:
            await asyncio.sleep(c.POLL_FREQUENCY)
            if not in_leeg_game():
                swap_monitors()
                break

    while True:
        client = await willump.start()
        try:
            json_event_sub = await client.subscribe("OnJsonApiEvent", default_handler=nothing)
            json_event_sub.filter_endpoint(c.GAME_STATE_ENDPOINT, game_state_handler)

            watchdog_misses = 0
            while True:
                await asyncio.sleep(c.POLL_FREQUENCY)

                # watchdog process to restart willump when we close the client -- otherwise this would break when we close
                # and re-open the client
                try:
                    await client.request("get", c.WATCHDOG_ENDPOINT)
                    watchdog_misses = 0
                except ClientConnectionError:
                    watchdog_misses += 1
                    if watchdog_misses == c.WATCHDOG_RESTART_THRESHOLD:
                        logging.warning("Failed to connect to watchdog endpoint {} times; restarting LCU backend...".format(c.WATCHDOG_RESTART_THRESHOLD))
                        break
        finally:
            await client.close()


if __name__ == '__main__':
    asyncio.run(main())
