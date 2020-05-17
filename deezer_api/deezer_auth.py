import datetime
import webbrowser

import requests

from deezer_api.deezer_objects import DeezerAuthorizationError, DeezerUrl


class DeezerOAuth:

    def __init__(self, app_id, secret, scope, redirect_url):
        self.client_id = app_id
        self.client_secret = secret
        self.token = None
        self.scope = scope
        self.redirect_url = redirect_url
        self.token_expires = None

    def get_access_token(self):
        if self.token and not self.is_token_expired():
            return self.token

        code = self.__get_auth_code()
        return self.__generate_auth_token(code)

    def __get_auth_code(self):
        auth = DeezerUrl.CodeGenerationUrl.format(self.client_id, self.redirect_url, self.scope)
        try:
            webbrowser.open(auth)
        except Exception:
            print(f"Please navigate here {auth}")
        response = input("Enter the URL you were redirected to: ")
        return self._parse_response_code(response)

    def is_token_expired(self):
        now = datetime.datetime.now()
        if now > self.token_expires:
            return True

    @staticmethod
    def _parse_response_code(response):
        try:
            return response.split("?code=")[1].replace(' ', '')
        except IndexError:
            return None

    def __generate_auth_token(self, code):
        try:
            response = requests.get(DeezerUrl.TokenUrl.format(self.client_id, self.client_secret, code)).text
            if response == 'wrong code':
                raise Exception(
                    "Unauthorized. Check authentication parameters and that access code was not used before")
            self.token = response.split("access_token=")[1].split("&expires=")[0]
            seconds = int(response.split("access_token=")[1].split("&expires=")[1])
            self.token_expires = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            return self.token
        except Exception as e:
            print("Error with authentication due to: {}".format(e))
            raise DeezerAuthorizationError(
                "Unauthorized. Check authentication parameters and that access code was not used before")
