#!/usr/bin/env python3

# author: greyshell
# description: use openvpn to access offensive security labs


import argparse
import base64
import json
import subprocess
import sys
import time

import pexpect
from colorama import Fore

# global constant variable
PROGRAM_LOGO = """
 _      ____  _____    __  _______  __  _ 
| |__  / () \ | () )   \ \/ /| ()_)|  \| |
|____|/__/\__\|_()_)    \__/ |_|   |_|\__|
"""


class UserInput:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                description="automate the openvpn lab connection")
        self.parser.add_argument("-p", "--vpn_credential", metavar="", help="provide vpn credential in a json file ",
                                 required=True)
        self.parser.add_argument("-c", "--config", metavar="", help="provide a ovpn file for the lab", required=True)
        self.parser.add_argument("-e", "--email_credential", metavar="", help="provide email credential in a json file",
                                 required=True)
        self.parser.add_argument("-t", "--email_to", metavar="", help="provide a email to send the notification",
                                 required=True)


class LoginVpn:
    def __init__(self):
        self._email_to = ""

        self._email_from = ""
        self._email_password = ""
        self._login_message = ""
        self._logout_message = ""

        self._vpn_user = ""
        self._vpn_password = ""
        self._dns = ""

        self._vpn_config = ""

        self._vpn_command = ""

    def get_parameters(self, vpn, config_file, email, email_to):
        """
        retrieve the value from the input
        :param vpn: dict
        :param config_file: string
        :param email: dict
        :param email_to: string
        :return: None
        """
        self._email_to = email_to
        self._email_from = email["email_from"]

        self._email_password = base64.b64decode(email["email_password"].encode()).decode()  # convert bytes to string
        self._login_message = email["login_message"]
        self._logout_message = email["logout_message"]

        self._vpn_user = vpn["vpn_user"]
        self._vpn_password = vpn["vpn_password"]
        self._dns = vpn["dns"]

        self._vpn_config = config_file

        self._vpn_command = "openvpn" + " " + self._vpn_config

    def lab_connection(self):
        """
        connect to the vpn
        :return: None
        """
        try:
            if self._dns:
                print(Fore.GREEN, f"[+] set the dns entry {self._dns} into /etc/resolve.conf")
                set_dns_command = "sed -i \'1s/^/nameserver " + self._dns + "\\n/\' /etc/resolv.conf"
                subprocess.check_output(set_dns_command, shell=True)

            print(Fore.GREEN, f"[+] sending email notification to {self._email_to}")
            send_email_command = "sendEmail -f " + self._email_from + " -t " + self._email_to + \
                                 " -u \'logged-In\' -o message-file=" + self._login_message + \
                                 " -s smtp.gmail.com:587 -o tls=yes -xu " + self._email_from + \
                                 " -xp " + self._email_password

            subprocess.check_output(send_email_command, shell=True)

            print(Fore.LIGHTBLUE_EX, f"[*] connected to the lab, press ctrl+c to disconnect from the lab")

            # connect to the lab
            i = pexpect.spawn(self._vpn_command)
            i.expect_exact("Enter")
            i.sendline(self._vpn_user)
            i.expect_exact("Password")
            i.sendline(self._vpn_password)

            # delay for 1 day
            time.sleep(3600 * 24)

        except KeyboardInterrupt:
            print(Fore.RED, f"[*] received ctrl+c, disconnecting from lab ")
            send_email_command = "sendEmail -f " + self._email_from + " -t " + self._email_to + \
                                 " -u \'logged-Out\' -o message-file=" + self._logout_message + \
                                 " -s smtp.gmail.com:587 -o tls=yes -xu " + self._email_from + \
                                 " -xp " + self._email_password
            subprocess.check_output(send_email_command, shell=True)
            print(Fore.GREEN, f"[*] sent email notification  ")

            if self._dns:
                print(Fore.GREEN, f"[+] unset the dns entry ")
                unset_dns_command = "sed -i '1d' /etc/resolv.conf"
                subprocess.check_output(unset_dns_command, shell=True)

        except Exception as e:
            print(Fore.MAGENTA, f"[x] error occurs while connecting vpn !")
            print(e)


if __name__ == "__main__":
    my_input = UserInput()
    args = my_input.parser.parse_args()

    if len(sys.argv) == 1:
        my_input.parser.print_help(sys.stderr)
        sys.exit(1)

    if args.vpn_credential and args.config and args.email_credential and args.email_to:
        with open(args.vpn_credential) as f:
            vpn_credential = json.load(f)
        with open(args.email_credential) as f:
            email_credential = json.load(f)

        # display program logo
        print(Fore.GREEN, f"{PROGRAM_LOGO}")

        conn = LoginVpn()
        conn.get_parameters(vpn_credential, args.config, email_credential, args.email_to)
        conn.lab_connection()

    else:
        my_input.parser.print_help(sys.stderr)