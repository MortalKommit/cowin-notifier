# Cowin Notifier
A simple python script that fetches available sessions through CoWin Public APIs

## Getting started
1. Install required packages with pip install -r requirements.txt
2. Configure required pin code or district lookups, and age ranges in config.ini
3. Run the program : python main.py

## Additional Notes
1. Logs are logged in logs/, with infolog containing successful requests that do have appointments  available ,which you may have missed and errorlog containing errors.  
2. You can only search by a list of pincode or a single district. WIP: search for multiple districts
and pincodes
