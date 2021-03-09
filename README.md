# Overview
Collection of scripts to periodically:
* query coinmarketcap historical api;
* store results into sqlite;
* update excel with new data;

# Demo
## query_and_store
![screen1](screen1.png)
## update_excel
![screen2](screen2.png)

# Usage
Uses anacron to run scripts at times defined in setup.yml

To run manually:
* `python3 main.py query_and_store` - query cmc api and store data into sqlite. Runs at 08:00 by default.
* `python3 main.py update_excel` - query sqlite and update excel. Runs at 08:30 by default.


# Centos8 installation
* copy dir to /opt/cmc or change setup.yml parameters;
* provide relevant credentials in setup.yml;
* `dnf install ansible python38`;
* `ansible-playbook setup.yml`;
