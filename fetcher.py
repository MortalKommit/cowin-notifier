import cloudscraper
import requests
import requests.exceptions
from datetime import datetime
from pprint import pprint
from jsonpath_ng.ext import parse
import logging
import os


class AppFetcher:

    def __init__(self,
                 pin_or_district=[400614, 400706, 400703],
                 calendar_fragment=True,
                 age_filter=None,
                 date=datetime.now().date().strftime("%d-%m-%Y")):
        """
        Fetches available appointments if they match a specified criteria.

        Args:
            pin_or_disrtict: Either a list of pin codes or a single
                             number district
            calendar_fragment (boolean, optional): fragment for 7-day date.
                Defaults to True.
            date (string, optional): date to search for.
                Defaults to current date.
        """

        self.search_term = pin_or_district
        self.date = date

        # main server address + url of the main app
        server_address, app_url = ("https://cdn-api.co-vin.in/api/v2",
                                   "appointment/sessions/public")

        pin_fragment, district_fragment = "findByPin",  "findByDistrict"

        # url endpoints change if using calendar view
        if calendar_fragment is True:
            pin_fragment, district_fragment = ("calendarByPin",
                                               "calendarByDistrict")

        if isinstance(pin_or_district, list):
            self.url = "/".join((server_address, app_url,
                                 pin_fragment))
        else:
            self.url = "/".join((server_address, app_url,
                                 district_fragment))

        self.age_filter = age_filter

        self._set_loggers()

        # For bypassing cloudflare anti-bot protection
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "firefox",
                     "platform": "windows"})

    def _parse_sessions(self, resp, jsonpath_expr):
        sessions = []

        # 1 center -> n sessions (2 level context)

        for match in jsonpath_expr.find(resp):

            sessions.append({"center_name": match.context.context.value[
                            "name"], "available_capacity": match.value[
                                "available_capacity"],
                "age_range": match.value["min_age_limit"],
                "price": match.context.context.value["fee_type"],
                "vaccine": match.value["vaccine"]})

        return sessions

    def _set_loggers(self):
        """ Configures logging for object

        Returns:
            None
        """
        date_format = datetime.now().strftime("%Y-%m-%d")
        self.log_filename = f"logs/infolog_{date_format}.log"
        os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
        # Root logger config
        logging.basicConfig(filename=self.log_filename, level=logging.INFO,
                            filemode='a')

        # define an error Handler which writes error messages to error log file
        error_file = logging.FileHandler(f"logs/errorlog_{date_format}.log",
                                         encoding="utf-8", mode='a')
        error_file.setLevel(logging.ERROR)

        # add error Handler to root logger
        logging.getLogger("").addHandler(error_file)

        self.info_logger = logging.getLogger('info_log')

    def get_sessions(self):
        """ Gets a list of appointments available and returns them by
            center

        Returns:
            list: list of appointments, filtered and sorted by capacity
            None: if none are available
        """
        sessions = []
        if isinstance(self.search_term, list):
            for pin in self.search_term:
                params = {"pincode": pin, "date": self.date}
        else:
            params = [{"district_id": self.search_term, "date": self.date}]

        for param in params:
            r = self.scraper.get(self.url, params=param)

            # 200 OK or other
            try:
                if not r.raise_for_status():
                    resp = r.json()
                    if self.age_filter is not None:

                        """
                        Previous schema
                        jsonpath_expr = parse(f"$.sessions \
                            [?(@.min_age_limit=={self.age_filter} \
                             & @.available_capacity > 0)]")
                        """

                        jsonpath_expr = parse(f"$.centers[*].sessions \
                        [?(@.min_age_limit == '{self.age_filter}' \
                         & @.available_capacity > 0)]")

                    else:
                        """
                        Previous schema
                        jsonpath_expr = parse("$.sessions \
                            [?(@.available_capacity > 0)]")

                        """

                        jsonpath_expr = parse("$.centers[*].sessions \
                        [?(@.available_capacity > 0)]")

                    sessions.extend(self._parse_sessions(resp, jsonpath_expr))

            except requests.HTTPError:
                logging.error(" ".join(
                    (f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :",
                     f"{r.request.url}",
                     f"[{r.status_code}]",
                     f"{r.text}")))

            except requests.exceptions.ConnectionError as e:
                logging.error(" ".join(
                    (f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :",
                     f"{e}")))

        if len(sessions) > 0:
            session_list = sorted(sessions, key=lambda k:
                                  k["available_capacity"],
                                  reverse=True)

            self.info_logger.info(" ".join(
                (f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :",
                 f"{r.request.url}",
                 "Appointments available! ",
                 f"[{r.status_code}]")))

            return session_list
        return


def setup_loggers():
    today = datetime.now().strftime("%Y-%m-%d")
    logging.basicConfig(filename=f"logs/infolog_{today}.log", encoding="utf-8",
                        level=logging.INFO, filemode='a')


if __name__ == "__main__":
    app = AppFetcher()
    pprint(app.get_sessions())
