## Description
`lab-vpn.py` helps to automate the openvpn connection for the InfoSec labs (i.e. PWK / CTP / WAPTx / AWAE).

### Usage
```
usage: lab_vpn.py [-h] -p  -c  -e  -t  [-d]

automate the openvpn lab connection

optional arguments:
  -h, --help            show this help message and exit
  -p , --vpn_credential 
                        provide vpn credential in a json file
  -c , --config         provide a ovpn file for the lab
  -e , --email_credential 
                        provide gmail credential in a json file
  -t , --email_to       provide a email to send the notification


sample:
python lab_vpn.py -p waptx_creds.json -c XSS_11_challenging_labs_320.ovpn -e asinha_emailFrom_creds.json -t your_email@gmail.com

```


 


