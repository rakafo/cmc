# Overview
Collection of scripts to periodically:
* query coinmarketcap historical api;
* store results into sqlite;
* update excel with new data;

# Usage
By default runs collection at 08:00 (or when available daily).

By default updates excel at 8:30 (or when available daily).

# Centos8 installation
* copy scripts to /opt/cmc or change setup.yml parameters
* `dnf install ansible python38`
* `ansible-playbook main.yml`
