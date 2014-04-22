import ConfigParser
import ldap
import ldapurl
import sys


class LDAPConnection:

    # connection settings
    ldap_connection = None
    ldap_provider_url = None
    ldap_dn = None
    ldap_protocol_version = None
    ldap_username = None
    ldap_password = None
    ldap_enable_tls = None
    ldap_filter = None
    ldap_user_name = None
    ldap_user_surname = None
    ldap_user_email = None
    ldap_user_uid = None

    def __init__(self, config_file):
        """
        Initializes LDAP server communication wrapper with provided config file
        """
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        try:
            self.ldap_username = config.get('active_directory', 'username')
            self.ldap_password = config.get('active_directory', 'password')
            self.ldap_provider_url = config.get('active_directory', 'provider_url')
            self.ldap_dn = config.get('active_directory', 'dn')
            self.ldap_protocol_version = config.get('active_directory', 'protocol_version')
            self.ldap_enable_tls = config.get('active_directory', 'tls_enabled')
            self.ldap_filter = config.get('active_directory', 'ldap_filter')
            self.ldap_user_name = config.get('active_directory', 'ldap_user_name')
            self.ldap_user_surname = config.get('active_directory', 'ldap_user_surname')
            self.ldap_user_email = config.get('active_directory', 'ldap_user_email')
            self.ldap_user_uid = config.get('active_directory', 'ldap_user_uid')
        except ConfigParser.NoOptionError as e:
            print "[x] Error: Config file is not complete! Section '%s' must contain option '%s'. " \
                  "Check config examples at https://github.com/Oomnitza.\nExiting." % (e.section, e.option)
            sys.exit(2)
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 30)

        # the default LDAP protocol version - if not recognized - is v3
        if self.ldap_protocol_version == '2':
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION2)
        else:
            self.ldap_protocol_version = '3'
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
        try:
            parsed_url = ldapurl.LDAPUrl(self.ldap_provider_url)
        except ValueError:
            print "[x] Error: Invalid url to LDAP service. Check config examples at https://github.com/Oomnitza." \
                  "\nExiting"
            sys.exit(2)
        self.ldap_connection = ldap.initialize(parsed_url.unparse())
        if self.ldap_enable_tls in ['True', 'true', '1'] and self.ldap_protocol_version == '3':
            try:
                self.ldap_connection.start_tls_s()
            except ldap.PROTOCOL_ERROR:
                print "[x] Error: LDAP server do not support TLS connection. Change the 'tls_enabled' to 'False' if " \
                      "you allow insecure data transfer.\nExiting"
                sys.exit(2)

    def fetch_all_users(self):
        """
        Connects to LDAP server using configuration and attempts to query
        and return all users.
        """
        # connect to server
        try:
            self.ldap_connection.simple_bind_s(self.compute_dn_with_cn(), self.ldap_password)
        except ldap.INVALID_CREDENTIALS:
            print "[x] Error: Cannot connect to the LDAP server with given credentials. Check the 'username', " \
                  "'password' and 'dn' options in the config file in the '[active_directory]' section.\nExiting."
            sys.exit(2)

        # search the server for users
        ldap_users = self.ldap_connection.search_s(self.ldap_dn, ldap.SCOPE_SUBTREE, self.ldap_filter, [
            self.ldap_user_surname,
            self.ldap_user_name,
            self.ldap_user_email,
            self.ldap_user_uid
        ])

        # disconnect and return results
        self.ldap_connection.unbind_s()
        return ldap_users

    def compute_dn_with_cn(self):
        """
        Returns the command name and distinguished name
        """
        return "cn=" + self.ldap_username + "," + self.ldap_dn
