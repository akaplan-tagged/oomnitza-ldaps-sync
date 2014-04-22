import binascii
import ConfigParser
import json
import os
import sys
import requests


class OomnitzaConnection:

    # connection settings
    oomnitza_session = None
    oomnitza_access_token = None
    oomnitza_username = None
    oomnitza_password = None
    oomnitza_system_url = None
    oomnitza_default_role = None
    oomnitza_default_position = None

    def __init__(self, config_file):
        """
        Initializes Oomnitza server communication wrapper with provided config file.
        Performs authorization with server to retrieve API access token as well.
        """
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        try:
            self.oomnitza_username = config.get('oomnitza', 'username')
            self.oomnitza_password = config.get('oomnitza', 'password')
            self.oomnitza_system_url = config.get('oomnitza', 'system_url')
            self.oomnitza_default_role = config.get('oomnitza', 'default_role')
            self.oomnitza_default_position = config.get('oomnitza', 'default_position')
        except ConfigParser.NoOptionError as e:
            print "[x] Error: Config file is not complete! Section '%s' must contain option '%s'. " \
                  "Check config examples at https://github.com/Oomnitza.\nExiting." % (e.section, e.option)
            sys.exit(2)
        self.oomnitza_session = requests.Session()
        self.oomnitza_access_token = self.perform_authorization()

    def perform_authorization(self):
        """
        Performs authorization with Oomnitza and returns API access token

        Reference: https://wiki.oomnitza.com/wiki/REST_API#Logging_In
        """
        headers = {'contentType': 'application/json'}
        auth_url = self.oomnitza_system_url + "/api/request_token?login=%s&password=%s" \
                                              % (self.oomnitza_username, self.oomnitza_password)
        response = self.oomnitza_session.get(auth_url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print "[x] Error: Error occurred during Oomnitza authorization: '%s'. Check the 'username', " \
                  "'password' and 'system_url' options in the config file in the '[oomnitza]' section.\nExiting. " \
                  % e.message
            sys.exit(2)
        return response.json()["token"]

    def upload_users(self, ldap_users):
        """
        Uploads retrieved users from Active Directory
        """
        _users = []
        headers = {'content-type': 'application/json'}
        create_url = self.oomnitza_system_url + "/api/people/individuals/add_multiple?access_token=%s" \
                                                % self.oomnitza_access_token
        for user in ldap_users:
            try:
                _users.append({
                    "USER": user[1]['uid'][0],
                    "PASSWORD": binascii.b2a_hex(os.urandom(15)),
                    "FIRST_NAME": user[1]['givenName'][0],
                    "LAST_NAME": user[1]['sn'][0],
                    "EMAIL": user[1]['mail'][0],
                    "PERMISSIONS_ID": self.oomnitza_default_role,
                    "POSITION": self.oomnitza_default_position,
                    "PHONE": "",
                    "ADDRESS": ""
                })
            except KeyError:
                print "[x] Error - User Missing Key: " + json.dumps(user[1])
                continue

        # perform upload
        print "[x] Uploading %s users to Oomnitza..." % _users.__len__()
        response = self.oomnitza_session.post(create_url, data=json.dumps(_users), headers=headers)
        print "[x] " + response.text
        return