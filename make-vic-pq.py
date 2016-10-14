my_username = 'polar bear'
pq_prefix   = 'vic-'
pq_state_id = '53'
pq_data     = 'pq.dat'  # Save the date ranges from project-gc to this file

import mechanize
import cookielib
import fileinput
import getpass
from datetime import date

def gc_session(username, password):
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
        if f.attrs['id'] == 'aspnetForm':
            br.form = f
            break
    if br.form == None:
        raise ValueError("Login form not found")

    br.form['ctl00$ContentBody$tbUsername'] = username
    br.form['ctl00$ContentBody$tbPassword'] = password

    r = br.submit()
    if r.code != 200:
        raise ValueError("Failed to submit login details")

    return br


def add_pq(session,name,state_id,start_day,start_month,start_year,end_day,end_month,end_year,email=r'nowhere@teamunicycle.net'):
    r = session.open('https://www.geocaching.com/pocket/gcquery.aspx')

    for f in session.forms():
        if f.attrs.get('id') == 'aspnetForm':
            session.form = f
            break
    if session.form == None:
        raise ValueError("Pocket query form not found")


    session.form['ctl00$ContentBody$tbName']              = name

    session.form['ctl00$ContentBody$tbResults']           = '1000'
    session.form['ctl00$ContentBody$CountryState']        = ['rbStates']
    session.form['ctl00$ContentBody$lbStates']            = [state_id]
    session.form['ctl00$ContentBody$Placed']              = ['rbPlacedBetween']

    session.form['ctl00$ContentBody$DateTimeBegin$Day']   = [start_day]
    session.form['ctl00$ContentBody$DateTimeBegin$Month'] = [start_month]
    session.form['ctl00$ContentBody$DateTimeBegin$Year']  = [start_year]

    session.form['ctl00$ContentBody$DateTimeEnd$Day']     = [end_day]
    session.form['ctl00$ContentBody$DateTimeEnd$Month']   = [end_month]
    session.form['ctl00$ContentBody$DateTimeEnd$Year']    = [end_year]

    session.form['ctl00$ContentBody$ddlAltEmails']        = [email]
    session.form['ctl00$ContentBody$cbIncludePQNameInFileName'] = ['on']

    r = session.submit()
    if r.code != 200:
        raise ValueError("Failed to submit pocket query details")



# Lookup month name
def month_num(month_name):
    return ['January','February','March','April','May','June','July','August','September','October','November','December'].index(month_name)+1

# Convert project-gc date to pq form date
def pgcdate_split(pgcdate):
    (m,d,y) = pgcdate.rstrip().split("/")
    mm = str(month_num(m))
    dd = str(d).lstrip("0")              # Can't have leading zero in pq form
    return (dd,mm,y)

    
s = gc_session(my_username, getpass.getpass('Password: '))

for line in fileinput.input(['pq.dat']):
   (row,start_date,end_date,num_days,num_caches) = line.rstrip().split("\t")
   print "Adding row "+row
   (start_day, start_month, start_year) = pgcdate_split(start_date)
   if end_date == "":                    # The last entry has no end date. Use end of next year
       end_day = '31'
       end_month = '12'
       end_year = str(date.today().year + 1)
   else:
      (end_day,   end_month,   end_year)   = pgcdate_split(end_date)

   add_pq(s,pq_prefix+row.zfill(2),pq_state_id,start_day,start_month,start_year,end_day,end_month,end_year)

fileinput.close()