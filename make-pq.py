import argparse
import mechanize
import http.cookiejar as cookielib
import fileinput
import getpass
from datetime import date
from bs4 import BeautifulSoup

######################################################################################################

def parse_arguments():
    parser = argparse.ArgumentParser(description='Add geocaching.com pocket queries by date range')
    
    parser.add_argument('-u', '--username', help='Your geocaching.com username', required=True)
    parser.add_argument('-p', '--prefix', help='A string to prefix each query name', default='pq-')
    parser.add_argument('-s', '--state', help='The geocaching.com state_id. Multiple state IDs may be separated by comma. See state_ids.txt for valid values.', required=True)
    parser.add_argument('-e', '--email', help='The email address to receive notifications. Omit to use default', default=None)
    parser.add_argument('-f', '--datafile', help='The file containing the date ranges. Default=standard input', default='-')
    parser.add_argument('-q', '--queue', help='Queue queries over subsequent days', action='store_true')
    parser.add_argument('-xf', '--exclude-found', help='Exclude found caches from query', action='store_true')
    parser.add_argument('-xo', '--exclude-owned', help='Exclude owned caches from query', action='store_true')

    return parser.parse_args()

######################################################################################################

def gc_session(username, password):
    """Create a browser instance and log on to geocaching.com"""
    # Create a browser
    br = mechanize.Browser()

    # Add a Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Set Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    # Set a User-Agent
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # Open the login page
    r = br.open('https://www.geocaching.com/login/default.aspx')
    if r.code != 200:
        raise ValueError("Unable to open login page")

    # Find the login form
    for f in br.forms():
        if 'action' in f.attrs and f.attrs['action'] == '/account/signin':
            br.form = f
            break
    if br.form == None:
        raise ValueError("Login form not found")

    br.form['UsernameOrEmail'] = username
    br.form['Password'] = password

    r = br.submit()
    if r.code != 200:
        raise ValueError("Failed to submit login details")

    return br

######################################################################################################

def split_digits(text):
  """
  Extracts number from a list of strings

  Args:
      text: The list of strings to process.

  Returns:
      A list of integers representing the extracted groups of digits.
  """
  number_list = []
  for item in text:
    number_list.append(int("".join(filter(str.isdigit,item.text))))
  return number_list

######################################################################################################


# def get_pq_summary(session):
#     """Get server's weekday and table of current PQs per day"""

#     r = session.open('https://www.geocaching.com/pocket/')
#     if r.code != 200:
#         raise ValueError("Unable to retrieve PQ summary page page")

#     soup = BeautifulSoup(session.response().read())

#     server_day_name=soup.find("div", id="ActivePQs").find("p").find("small").find("strong").next_sibling.strip().split(",")[0]
#     server_day = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'].index(server_day_name)

#     day_text = soup.find("tr", class_="TableFooter").find_all("td")[3:10]
#     day_counts = split_digits(day_text)

#     return server_day,day_counts

######################################################################################################

def get_next_free_day(session):
    """Get next weekeday with free PQ slot"""
    
    r = session.open('https://www.geocaching.com/pocket/')
    if r.code != 200:
        raise ValueError("Unable to retrieve PQ summary page page")
    
 ###soup = BeautifulSoup(session.response().read(), "lxml")
    soup = BeautifulSoup(session.response().read(), "html5lib")
    
    server_day_name=soup.find("div", id="ActivePQs").find("p").find("small").find("strong").next_sibling.strip().split(",")[0]
    server_day = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'].index(server_day_name)
    
    day_text = soup.find("tr", class_="TableFooter").find_all("td")[3:10]
    day_counts = split_digits(day_text)
    
#   Avoid adding queries for today (ie, will never have lowest count)
    day_counts[server_day] = 999

#   Distribute evenly over days: pick the day with the least existing queries
    return min(range(len(day_counts)), key=day_counts.__getitem__)
    

#   Alternative: fill each day's queries first
#
#   for i in range(6):                 # only 6 days. Never queue for today Alternative: fill each day's queries first
#       day_index = (server_day+i+1) % 7    Alternative: fill each day's queries first
#       if day_counts[day_index] < 10:  Alternative: fill each day's queries first
#          return day_index Alternative: fill each day's queries first


######################################################################################################    

def add_pq(session,
           name,
           state_id,
           start_day, start_month, start_year,
           end_day,end_month,end_year,
           queue,
           email=None,
           exclude_found=False,
           exclude_owned=False):

    if queue == True:
        next_free_day = get_next_free_day(session)
      
    r = session.open('https://www.geocaching.com/pocket/gcquery.aspx')

    for f in session.forms():
        if f.attrs.get('id') == 'aspnetForm':
            session.form = f
            break
    if session.form == None:
        raise ValueError("Pocket query form not found")

    session.form['ctl00$ContentBody$rbRunOption']         = ['2']     # 1 = run and deselect, 2 = run weekly, 3 = run once and delete
    session.form['ctl00$ContentBody$tbName']              = name

    session.form['ctl00$ContentBody$tbResults']           = '1000'
    session.form['ctl00$ContentBody$CountryState']        = ['rbStates']
    session.form['ctl00$ContentBody$lbStates']            = state_id.split(",")
    session.form['ctl00$ContentBody$Placed']              = ['rbPlacedBetween']

    session.form['ctl00$ContentBody$DateTimeBegin$Day']   = [start_day]
    session.form['ctl00$ContentBody$DateTimeBegin$Month'] = [start_month]
    session.form['ctl00$ContentBody$DateTimeBegin$Year']  = [start_year]

    session.form['ctl00$ContentBody$DateTimeEnd$Day']     = [end_day]
    session.form['ctl00$ContentBody$DateTimeEnd$Month']   = [end_month]
    session.form['ctl00$ContentBody$DateTimeEnd$Year']    = [end_year]

    if exclude_found:
        session.form['ctl00$ContentBody$cbOptions$0']     = ['2']

    if exclude_owned:
        session.form['ctl00$ContentBody$cbOptions$2']     = ['6']

    if email != None:
        session.form['ctl00$ContentBody$ddlAltEmails']        = [email]
    session.form['ctl00$ContentBody$cbIncludePQNameInFileName'] = ['on']

    if (queue == True) and (next_free_day != None):
            session.form['ctl00$ContentBody$cbDays$'+str(next_free_day)] = [str(next_free_day)]

    session.set_all_readonly(False)
    session.form['__EVENTTARGET'] = "ctl00$ContentBody$btnSubmit"

    r = session.submit()
    if r.code != 200:
        raise ValueError("Failed to submit pocket query details")


######################################################################################################

# Lookup month name
def month_num(month_name):
    return ['January','February','March','April','May','June','July','August','September','October','November','December'].index(month_name)+1

######################################################################################################

# Convert project-gc date to pq form date
def pgcdate_split(pgcdate):
    (m,d,y) = pgcdate.rstrip().split("/")
    mm = str(month_num(m))
    dd = str(d).lstrip("0")              # Can't have leading zero in pq form
    return (dd,mm,y)

######################################################################################################

args = parse_arguments()
    
s = gc_session(args.username, getpass.getpass('Password: '))

for line in fileinput.input([args.datafile]):
   (row,start_date,end_date,num_days,num_caches) = line.rstrip().split("\t")
   print("Adding row "+row)
   (start_day, start_month, start_year) = pgcdate_split(start_date)
   if end_date == "":                    # The last entry has no end date. Use end of next year
       end_day = '31'
       end_month = '12'
       end_year = str(date.today().year + 1)
   else:
      (end_day, end_month, end_year) = pgcdate_split(end_date)

   add_pq(s,
          args.prefix+row.zfill(2),
          args.state,
          start_day,start_month,start_year,
          end_day,end_month,end_year,
          args.queue,
          args.email,
          args.exclude_found,
          args.exclude_owned)

fileinput.close()
