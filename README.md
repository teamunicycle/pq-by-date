# pq-by-date
## Create pocket queries for nominated date ranges

Go to http://project-gc.com/Tools/PQSplit and select the location you want the queries for.

Copy all rows from the Splitted on 1000 table except the heading row

Paste them into a file, eg pq.dat. Make sure each field remains TAB delimited.

Run the scipt

WARNING: There isn't very much input validation

---

usage: make-pq.py [-h] -u USERNAME [-p PREFIX] -s STATE [-e EMAIL]
                  [-f DATAFILE]

Add geocaching.com pocket queries by date range

optional arguments:
  -h, --help            show this help message and exit
  -u, --username USERNAME
                        Your geocaching.com username
  -p, --prefix PREFIX
                        A string to prefix each query name
  -s, --state STATE
                        The geocaching.com state_id. NSW=52, VIC=53, QLD=54,
                        SA=55, WA=56, TAS=57, NT=58, ACT=59
  -e, --email EMAIL
                        The email address to receive notifications. Omit to
                        use default
  -f, --datafile DATAFILE
                        The file containing the date ranges. Default=standard
                        input
  -q, --queue           Queue the queries to run on the next available days
                        Does not queue for current day
                        Uses current queue by day
---


There is no checking that the pocket queries already exist.
You will need to set the days to run the queries manually once these have been added.
The first column of the data file is used as a suffix to the query name.

## Examples

make-pq.py -u "polar bear" -p "victoria-" -s 53 -f pq.dat

tail -2l pq.dat | make-pq.py -u grizzlybear -p vic- -s 53 -e grizzly@bearcave.com

## Prerequisites

Ensure you have the bs4 and mechanize packages. If you don't have them you can get them by entering

sudo apt install python-bs4
sudo apt install python-mechanize

