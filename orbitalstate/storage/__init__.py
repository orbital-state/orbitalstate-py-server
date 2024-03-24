ALL_STATES : list = [
    "pending", # initial state
    "processing", # state when contract is being processed
    "ok", # state when contract is successfully processed
    "drifted", # state when contract is processed but has drifted
    "failed", # state when contract processing failed with error
    "terminating", # state when contract is being terminated
    "terminated", # final state
]


TRANSITING_STATES : dict = {
    # from -> to
    "pending": ["processing", "terminating"],
    "processing": ["ok", "failed"],
    "failed": ["pending", "terminating"],
    "ok": ["drifted", "terminating"],
    "drifted": ["pending", "terminating"],
    "terminating": ["terminated", "failed"],
    "terminated": [],  # no transitions from terminated state
}


ACCEPTED_STATES : dict = {
    # to <- from
    "pending": [],
    "processing": ["pending"],
    "failed": ["processing", "terminating"],
    "ok": ["processing"],
    "drifted": ["ok"],
    "terminating": ["processing", "failed", "ok", "drifted"],
    "terminated": ["terminating"]
}