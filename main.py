from win10toast_click import ToastNotifier
import fetcher
import configparser
import webbrowser
import asyncio


config = configparser.ConfigParser(allow_no_value=True)


def read_config():
    """
    Reads from config.ini and determines search parameters

    Returns:
        AppFetcher instance: object that has request parameters initialized
    """
    config.read("config.ini")
    search_term = None
    if config["SEARCH TERM"].get("pin codes"):
        search_term = [pin.strip() for pin in
                       config["SEARCH TERM"]["pin codes"].split(",")]
    elif config["SEARCH TERM"].get("district"):
        search_term = config["SEARCH TERM"]["district"]

    if config["SEARCH TERM"].get("age range filter"):
        age_group = config["SEARCH TERM"].get("age range filter")
    else:
        age_group = None
    return fetcher.AppFetcher(pin_or_district=search_term,
                              age_filter=age_group)


def open_url(page_url="https://selfregistration.cowin.gov.in/"):
    try:
        webbrowser.open_new(page_url)
        print("Opening URL...")
    except webbrowser.Error:
        print('Failed to open URL. Unsupported variable type.')


async def fetch_sessions(app, wait):
    """
    Fetches appointment sessions,  if available every <wait> seconds

    Args:
        wait (int): Wait period between session fetch, in seconds.

    Returns:
        msg str: Notification message, top 3 sessions by available capacity
    """

    msg = ""
    sessions = app.get_sessions()

    if sessions is not None:
        for session in sessions[0:3]:
            msg += " ".join((session["center_name"],
                            f"{session['pincode']}",
                             f" no.s: {session['available_capacity']}",
                             f"age: {session['age_range']}+",
                             f"{session['vaccine']}",
                             f"{session['price']}")) + "\n"
    await asyncio.sleep(wait)

    return msg


async def notify(msg):
    """
    Creates a short-lived desktop notification

    Args:
        msg (str): Message string
    """

    toaster = ToastNotifier()
    toaster.show_toast(
        "Appointment available!",  # title
        f"{msg} >>",  # message
        icon_path=None,
        duration=8,  # None = leave notification in Notification Center
        threaded=True,  # True = run other code in parallel
        callback_on_click=open_url
    )

    while toaster.notification_active():
        await asyncio.sleep(0.1)


async def periodic_fetch(wait=15):
    """
    Runs notifier and session fetcher, asynchronously

    Args:

        wait (int, optional): Wait period between requests, in seconds.
                              Defaults to 15.
    """

    # Read config from config.ini
    app = read_config()
    while True:
        msg = await fetch_sessions(app, wait)
        if msg:
            await notify(msg)


asyncio.run(periodic_fetch(wait=10))
