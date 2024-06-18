# pq-by-date
## Create pocket queries for nominated date ranges

Go to http://project-gc.com/Tools/PQSplit and select the location you want the queries for. You
can also add a filter to exclude your found or owned caches from the list, make sure you set the
corresponding flags in the command line (-xf and -xo).

Copy all rows from the "Splitted on 1000" table except the heading row

Paste them into a file, eg pq.dat. Make sure each field remains TAB delimited.

Run the script

WARNING: There isn't very much input validation

```
usage: make-pq.py [-h] -u USERNAME [-p PREFIX] -s STATE [-e EMAIL]
                  [-f DATAFILE] [-xf] [-xo] [-q]

Add geocaching.com pocket queries by date range

arguments:
  -h, --help            show this help message and exit
  -u, --username USERNAME
                        Your geocaching.com username. This is required. Enclose in quotes if it has spaces.
                        You will be prompted for your password
  -p, --prefix PREFIX
                        A string to prefix each query name
  -s, --state STATE
                        The geocaching.com state_id. Multiple state IDs may be
                        separated by comma. See state_ids.txt for valid
                        values.
  -e, --email EMAIL
                        The email address to receive notifications. Omit to
                        use the default configured in your geocaching.com profile
  -f, --datafile DATAFILE
                        The file containing the date ranges. Default=standard
                        input
  -xf, --exclude-found
                        Set the flag in each pocket query to exclude caches found
                        by USERNAME. Set this if you added the corresponding filter
                        in Project-GC.
  -xf, --exclude-owned
                        Set the flag in each pocket query to exclude caches owned
                        by USERNAME. Set this if you added the corresponding filter
                        in Project-GC.
  -q, --queue
                        Queue the queries to run on the next available days
                        Does not queue for current day
                        Uses current queue by day
```


There is no checking that the pocket queries already exist. Be careful with this, as duplicate names
will be created.

Without the -queue option, the pocket queries will not be queued to run. When the -queue option is selected,
the queries will be distributed among across days, filling days with the least queued queries first. No query is 
queued on the current day, to prevent queries running before you are ready.

The first column of the data file is used as a suffix to the query name.

## Examples

python make-pq.py -u "polar bear" -p "victoria-" -s 53 -f pq.dat --queue

tail -2l pq.dat | python make-pq.py -u grizzlybear -p vic- -s 53 -e grizzly@bearcave.com -xf -xo

## Prerequisites

Ensure you have the bs4 and mechanize packages. If you don't have them you can get them (on Ubuntu) by entering

sudo apt install python-bs4
sudo apt install python-mechanize
