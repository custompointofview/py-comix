# py-comix

Python crawler that downloads images & creates comic book reader compatible files (.cbz)

## Standard execution

```shell script
# standard execution
python3 main.py -j /path/to/default.json

# help for command
usage: main.py [-h] [-u url] [-j json] [-c] [-p] [-d] [-v]

Creates a comic reader compatible file from a given URL

optional arguments:
  -h, --help            show this help message and exit
  -u url, --url url     URL to scrape chapters from
  -j json, --json json  Path config json
  -c, --clean           keep only .cbz files
  -p, --parallel        parallel execution
  -d, --dry-run         only print what you will do
  -v, --verbose         verbose execution
  -x, --no-proxies      disable proxies
  -r, --reverse         reverse chapter execution
```

## Default configuration

```json
{
  "to": {
    "urls": [],
    "rss": "",
    "watch": [],
    "filter": ["Issue"]
  },
  "manga": {
    "urls": [],
    "rss": "",
    "watch": [],
    "filter": ["Chapter"]
  },
  "referer": ""
}
```
