"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from models.ldap_connection import LDAPConnection
from models.oomnitza_connection import OomnitzaConnection


# initialize service wrappers
ldap = LDAPConnection("config.ini")
oomnitza = OomnitzaConnection("config.ini")


def main():
    """
    Main entry point for Oomnitza & Active Directory synchronization
    """
    print "Oomnitza LDAPS User Synchronization\n[x] Sync has started..."

    # perform synchronization
    _ldap_users = ldap.fetch_all_users()
    oomnitza.upload_users(_ldap_users)

    print "[x] Sync has completed. Bye!"
    return True


if __name__ == '__main__':
    main()