# coolmod_crawler

## Running locally

Set environment variable `TELEGRAM_TOKEN`

### PyCharm

Create a run configuration that points to: `coolmod_crawler/main.py`

### CLI

Run:

```
scrapy crawl graphic_cards
```

## Raspberry Setup

1. Copy files to server:

```
scp -r PythonProjects/coolmod_crawler <user>@<ip>:/home/<user>/scrapy-projects
```

2. Install dependencies:

```
Cd ~/scrapy-projects/coolmod_crawler
pip3 install -r requirements.txt
```

3. Create script (`~/crawl.sh`):

```sh
#!/bin/sh
# go to the spider directory
cd /home/<user>/scrapy-projects/coolmod_crawler
# run the spider
/usr/local/bin/scrapy crawl graphic_cards
```

4. Make the script executable:

```
chmod +x ~/crawl.sh
```

5. Create cron job:

```
crontab -e
```

```
*/2 * * * * /home/pi/crawl.sh
```

It will run every 2 minutes.

6. Check cron jobs:

```
crontab -l
```

7. Check logs:

```
grep CRON /var/log/syslog
```
