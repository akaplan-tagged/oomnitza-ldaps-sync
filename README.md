Oomnitza - User Synchronization via LDAPS
===========================

Python package to synchronize users from Active Directory to Oomnitza via LDAPS.

Prerequisites
-------------
 * python-ldap ~> 2.4.15
 * requests ~> 2.3.0

Usage
-----
* Update `config.ini` with your LDAPS and Oomnitza settings. For Oomnitza credentials, we recommend creating an additional "user" for this task.
* Perform `./run.sh` or `python start.py`