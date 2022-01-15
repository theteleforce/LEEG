# LEEG.py
LOG_FILE = "log.txt"
POLL_FREQUENCY = 0.5
GAME_STATE_ENDPOINT = "/lol-gameflow/v1/session"
END_GAME_STATES = ["EndOfGame", "TerminatedInError", "PreEndOfGame", "WaitingForStats"]
WATCHDOG_ENDPOINT = "/riotclient/ux-state"
WATCHDOG_RESTART_THRESHOLD = 5

# win32_nonsense.py
PRIMARY_MONITOR_I_THINK = 0x1
