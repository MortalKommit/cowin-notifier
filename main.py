from plyer import notification
import fetcher
import configparser

config = configparser.ConfigParser(allow_no_value=True)


def read_config():
    """ Reads from config.ini and determines search parameters

    Returns:
        AppFetcher instance: object that has request parameters initialized
    """
    config.read("config.ini")
    search_term = None
    if config["SEARCH TERM"].get("pin codes"):
        search_term = config["SEARCH TERM"]["pin codes"].split(",")
    elif config["SEARCH TERM"].get("district"):
        search_term = config["SEARCH TERM"]["district"]

    if config["SEARCH TERM"].get("age range filter"):
        age_group = config["SEARCH TERM"].get("age range filter")
    else:
        age_group = None
    return fetcher.AppFetcher(pin_or_district=search_term,
                              age_filter=age_group)


def fetch_sessions(wait=30):
    sessions = app.get_sessions()

    if sessions is not None:
        msg = ""
        for session in sessions[0:3]:
            msg += " ".join((session["center_name"],
                            f" capacity: {session['available_capacity']}",
                             f"age: {session['age_range']}+")) + '\n'

        notification.notify(
            title="Vaccine Appointment Available",
            message=f"{msg}",
            timeout=15
        )


app = read_config()
fetch_sessions()
