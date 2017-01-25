# -*- coding: utf-8 -*-

import os
import sys


import sqlite3
import os.path
import json
import urlparse
import keyring
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

reload(sys)
sys.setdefaultencoding('utf-8')

""" 本程序将chrome下cookies解密成字典形式，以提供给requests使用
"""

def decrypt():
    url = 'http://www.zhihu.com'
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

    def chrome_decrypt(encrypted_value, key=None):
        # Encrypted cookies should be prefixed with 'v10' according to the
        # Chromium code. Strip it off.
        encrypted_value = encrypted_value[3:]

        # Strip padding by taking off number indicated by padding
        # eg if last is '\x0e' then ord('\x0e') == 14, so take off 14.
        # You'll need to change this function to use ord() for python2.
        def clean(x):
            #return x[:-x[-1]].decode('utf8')
            return x[:-ord(x[-1])]

        cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        decrypted = cipher.decrypt(encrypted_value)
        return clean(decrypted)

    if sys.platform == 'darwin':
        my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
        my_pass = my_pass.encode('utf8')
        iterations = 1003
        cookie_file = os.path.expanduser(
            '~/Library/Application Support/Google/Chrome/Default/Cookies'
        )

    # Generate key from values above
    key = PBKDF2(my_pass, salt, length, iterations)

    # Part of the domain name that will help the sqlite3 query pick it from the Chrome cookies
    #domain = urllib.parse.urlparse(url).netloc
    domain = urlparse.urlparse(url).netloc
    domain_no_sub = '.'.join(domain.split('.')[-2:])

    conn = sqlite3.connect(cookie_file)
    sql = 'select name, value, encrypted_value from cookies ' \
          'where host_key like "%{}%"'.format(domain_no_sub)

    cookies = {}
    cookies_list = []
    with conn:
        for k, v, ev in conn.execute(sql):
            # if there is a not encrypted value or if the encrypted value
            # doesn't start with the 'v10' prefix, return v
            if v or (ev[:3] != b'v10'):
                cookies_list.append((k, v))
            else:
                decrypted_tuple = (k, chrome_decrypt(ev, key=key))
                cookies_list.append(decrypted_tuple)
        cookies.update(cookies_list)
    with open('zhihu_cookies', 'wb') as w_file:
        w_file.write(json.dumps(cookies))
    return cookies


if __name__ == '__main__':
    decrypt()


