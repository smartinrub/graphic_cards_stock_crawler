# graphic_cards_stock_crawler

## Running locally

Set environment variable `TELEGRAM_TOKEN`

### PyCharm

Create a run configuration that points to: `graphic_cards_stock_crawler/main.py`

### CLI

Run:

```
scrapy crawl graphic_cards_stock`
```

## Raspberry Setup

1. Install and configure MariaDB:

Install:

```
sudo apt update
sudo apt upgrade
sudo apt install mariadb-server
```

Configure:

```
sudo mysql_secure_installation
```

Create user:

```
sudo mysql -uroot -p
CREATE USER 'pi'@'%' IDENTIFIED BY '<PASSWORD>';
GRANT ALL PRIVILEGES ON *.* TO 'pi'@'%';
FLUSH PRIVILEGES;
exit;
```

Configure remote access:

```
nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

```
bind-address            = 0.0.0.0
```

From your local machine:

```
mysql -upi -p -h <RASPBERYPI_IP>
```

2. Copy files to server:

```
scp -r PythonProjects/graphic_cards_stock_crawler <user>@<ip>:/home/<user>/scrapy-projects
```

Set env variables (this is only for running manually, the cron job requires to set the env variables globally):

```
nano ~/.bashrc
```

and add:

```
export TELEGRAM_TOKEN=<TOKEN>
export MARIADB_USER=pi
export MARIADB_PASSWORD=<PASSWORD>
export MARIADB_HOST=localhost
export MARIADB_PORT=3306
export MARIADB_SCHEMA=graphic_cards_stock_crawler
```

3. Install dependencies:

```
cd ~/scrapy-projects/graphic_cards_stock_crawler
pip3 install -r requirements.txt
```

4. Create script (`~/crawl.sh`):

```sh
#!/bin/sh
# go to the spider directory
cd /home/<user>/scrapy-projects/graphic_cards_stock_crawler
# run the spider
/usr/local/bin/scrapy crawl graphic_cards_stock
```

5. Make the script executable:

```
chmod +x ~/crawl.sh
```

6. Create cron job:

```
crontab -e
```

```
*/2 * * * * MARIADB_USER=pi MARIADB_PASSWORD=<PASSWORD> MARIADB_HOST=localhost MARIADB_PORT=3306 MARIADB_SCHEMA=graphic_cards_stock_crawler TELEGRAM_TOKEN=<TOKEN> /home/pi/crawl.sh
```

It will run every 2 minutes.

7. Check cron jobs:

```
crontab -l
```

8. Check logs:

```
grep CRON /var/log/syslog
```

## TODO

* Crawler for LCLC
* Add exclusions
* Create CI/CD GitHub action
