import datetime
import webbrowser

import requests

from deezer_api.deezer_objects import DeezerUrl, DeezerError, DeezerErrorMessage


class DeezerBasicAuth:

    def __init__(self, expired):
        self.expired = datetime.datetime.now() + datetime.timedelta(seconds=expired)

    def is_token_expired(self):
        now = datetime.datetime.now()
        if now > self.expired:
            return True


class DeezerTokenAuth(DeezerBasicAuth):

    def __init__(self, token=None, access=None, expired=3600):
        if token is None:
            raise DeezerError(DeezerErrorMessage.WrongTokenAuthParameters.format(token, access))

        super().__init__(expired)
        self.token = token

    def get_access_token(self):
        if self.token and not self.is_token_expired():
            return self.token
        raise DeezerError(DeezerErrorMessage.TokenExpired)


class DeezerTokenAppAuth(DeezerBasicAuth):

    def __init__(self, app_id=None, secret=None, code=None, access=None, expired=3600):
        if app_id is None or secret is None or code is None:
            raise DeezerError(DeezerErrorMessage.WrongTokenAppAuthParameters.format(app_id, secret, code, access))

        super().__init__(expired)
        self.app_id = app_id
        self.secret = secret
        self.code = code
        self.token = None

    def get_access_token(self):
        if self.token is None:
            self.token = self.generate_auth_token()
        if self.token and not self.is_token_expired():
            return self.token
        raise DeezerError(DeezerErrorMessage.TokenExpired)

    def generate_auth_token(self):
        try:
            response = requests.get(DeezerUrl.TokenUrl.format(self.app_id, self.secret, self.code)).text
            if response == 'wrong code':
                raise DeezerError(DeezerErrorMessage.Unauthorized)
            self.token = response.split("access_token=")[1].split("&expires=")[0]
            seconds = int(response.split("access_token=")[1].split("&expires=")[1])
            self.expired = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            return self.token
        except Exception as e:
            print("Error with authentication due to: {}".format(e))
            raise DeezerError(DeezerErrorMessage.Unauthorized)


class DeezerOAuth(DeezerTokenAppAuth):

    def __init__(self, app_id, secret, access, redirect_url):
        if app_id is None or secret is None or redirect_url is None:
            raise DeezerError(DeezerErrorMessage.WrongAuthParameters.format(app_id, secret, redirect_url, access))

        super().__init__(app_id, secret, '')

        self.code = access
        self.redirect_url = redirect_url
        self.token = None
        self.token_expires = None

    def get_access_token(self):
        if self.token and not self.is_token_expired():
            return self.token

        self.code = self.__get_auth_code()
        return self.generate_auth_token()

    def __get_auth_code(self):
        auth = DeezerUrl.CodeGenerationUrl.format(self.app_id, self.redirect_url, self.code)
        webbrowser.open(auth)
        response = input("Enter the URL you were redirected to: ")
        return self._parse_response_code(response)

    @staticmethod
    def _parse_response_code(response):
        try:
            return response.split("?code=")[1].replace(' ', '')
        except IndexError:
            return None
