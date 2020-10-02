# https://github.com/WazeHell/acunetix-python

import json

import requests

requests.packages.urllib3.disable_warnings()

API_BASE = "/api/v1/"
API_SCAN = API_BASE + "scans"
API_TARGET = API_BASE + "targets"

target_criticality_list = {
    "critical": "10",
    "high": "20",
    "normal": "10",
    "low": "0",
}

target_criticality_allowed = list(target_criticality_list.keys())

scan_profiles_list = {
    "full_scan": "11111111-1111-1111-1111-111111111111",
    "high_risk_vuln": "11111111-1111-1111-1111-111111111112",
    "xss_vuln": "11111111-1111-1111-1111-111111111116",
    "sql_injection_vuln": "11111111-1111-1111-1111-111111111113",
    "weak_passwords": "11111111-1111-1111-1111-111111111115",
    "crawl_only": "11111111-1111-1111-1111-111111111117",
}

scan_profiles_allowed = list(scan_profiles_list.keys())


class AXException(Exception):
    HTTP_ERROR = "httpError"
    AUTH_ERROR = "authError"
    SERVER_RESOURCE = "serverResource"
    NOT_ALLOWED_CRITICYLITY_PROFILE = "Criticallity not found"
    NOT_ALLOWED_SCAN_PROFILE = "Scan Profile not found"
    JSON_PARSING_ERROR = "Decoding JSON has failed"

    def __init__(self, key, message):
        Exception.__init__(self, message)
        self.key = key


class Acunetix(object):
    def __init__(self, host=None, api=None, timeout=20):
        self.apikey = api
        self.host = str(
            "{}{}".format("https://" if "https://" not in host else "", host)
        )
        self.timeout = timeout
        self.headers = {
            "X-Auth": self.apikey,
            "content-type": "application/json",
            "User-Agent": "Acunetix",
        }
        self.authenticated = self.__is_connected()
        if not self.authenticated:
            raise AXException("AUTH_ERROR", "Wrong API Key !")

    def __json_return(self, data):
        try:
            return json.loads(data)
        except Exception as e:
            raise AXException("JSON_PARSING_ERROR", f"Json Parsing has occured: {e}")

    def __send_request(self, method="get", endpoint="", data=None):
        request_call = getattr(requests, method)
        url = str("{}{}".format(self.host, endpoint if endpoint else "/"))
        try:
            request = request_call(
                url,
                headers=self.headers,
                timeout=self.timeout,
                data=json.dumps(data),
                verify=False,
            )
            if request.status_code == 403:
                raise AXException("HTTP_ERROR", f"HTTP ERROR OCCURED: {request.text}")
            return self.__json_return(request.text)
        except Exception as e:
            raise AXException("HTTP_ERROR", f"HTTP ERROR OCCURED: {e}")

    def __is_connected(self):
        return False if 'Unauthorized' in str(self.info()) else True

    def info(self):
        return self.__send_request(method="get", endpoint="/api/v1/info")

    def targets(self):
        return self.__send_request(
            method="get", endpoint=f"{API_TARGET}?pagination=50"
        )

    def add_target(self, target="", criticality="normal"):
        if criticality not in target_criticality_allowed:
            raise AXException("NOT_ALLOWED_CRITICYLITY_PROFILE",
                              "Criticallity not found allowed values {}".format(str(list(target_criticality_allowed))))
        target_address = (
            target if "http://" in target or "https://" in target else "http://{}".format(target)
        )
        data = {
            "address": str(target_address),
            "description": "Sent from Acunetix-Python",
            "criticality": target_criticality_list[criticality],
        }
        # print(f"adding target {target_address} ")
        return self.__send_request(method="post", endpoint=API_TARGET, data=data)

    def delete_target(self, target_id):
        # print(f"deleting {target_id}")
        try:
            return self.__send_request(
                method="delete", endpoint=f"{API_TARGET}/{target_id}"
            )
        except:
            pass

    def delete_all_targets(self):
        while True:
            targets = self.targets()
            if len(targets["targets"]):
                for target in targets["targets"]:
                    self.delete_target(target["target_id"])
            else:
                break

    def scans(self):
        return self.__send_request(method="get", endpoint=API_SCAN)

    def start_scan(self, address=None, target_id=None, scan_profile="full_scan"):
        if scan_profile not in scan_profiles_allowed:
            raise AXException("NOT_ALLOWED_SCAN_PROFILE",
                              "Scan Profile not found allowed values {}".format(str(list(scan_profiles_allowed))))
        if address and not target_id:
            target_id = self.add_target(target=address)["target_id"]
        scan_payload = {
            "target_id": str(target_id),
            "profile_id": scan_profiles_list[scan_profile],
            "schedule": {"disable": False, "start_date": None, "time_sensitive": False},
        }
        # print(f"Scanning {target_id} , {scan_profile}")
        return self.__send_request(method="post", endpoint=API_SCAN, data=scan_payload)


class AcunetixReport():
    def acunetix(self, target):
        if not self.acunetix_host or not self.acunetix_token:
            msg = "disabled acunetix integration due to missing configurations"
            self.log(msg)
            self.local(msg)
            return

        try:
            acunetix = Acunetix(host="%s:%i" % (self.acunetix_host, self.acunetix_port), api=self.acunetix_token)
            acunetix.start_scan(target.strip())
            self.log("created new acunetix's scan target=" + target)
        except Exception as e:
            self.slack("acunetix integration had an error: " + str(e))