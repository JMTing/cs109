"""
Chris Satterthwaite
9/12/2013
Scrape function to find swimmers that yielded errors before.
"""

"""
Function declarations.
"""

def extractor(searchtab):
    """ Scrape SWIMS data from valid search results table. """
    global form, college_year, college
    # Get individual name and club team
    info_name = searchtab.find('span', attrs={'id' : 'ctl63_lblAthleteName'}).string
    info_club = searchtab.find('span', attrs={'id' : 'ctl63_lblAthleteClub'}).string
    name = info_name
    club = info_club[1:-1]
    
    # Extract pages, get one then iterate
    tablerows = searchtab.table.findAll('tr')
    more = searchtab.table.find('tr', attrs={'class' : 'GridPager'})
    morelinks = more.td.findAll('a')
    tablerows = tablerows[2:-1]
    # Add table values to aggregate string
    for row in tablerows:
        string = name + '\t' + club + '\t' + college_year + '\t' + college
        rowdata = row.contents[1:12]
        for col in rowdata:
            string = string + '\t' + col.string
        string = string + '\n'
        timeresults.write(string)
    # Iterate through multiple pages of times.
    for pagelink in morelinks:
        nextpage = pagelink['href'][25:-5]
        form['__EVENTTARGET'] = nextpage
        soup = submitform(form)
        results = soup.find('div', attrs={'id' : 'ctl63_pnlSearchResults'})
        tablerows = results.table.findAll('tr')
        tablerows = tablerows[2:-1]
        for row in tablerows:
            # Print string to file with tab seperators.
            string = name + '\t' + club + '\t' + college_year + '\t' + college
            rowdata = row.contents[1:12]
            for col in rowdata:
                string = string + '\t' + col.string
            string = string + '\n'
            timeresults.write(string)

def submitform(filledform):
    """ Submit form to USA Swimming and return the search results table. """
    global form
    # Submit form and extract search results.
    request = filledform.click()  # mechanize.Request object
    response =  br.open(request)
    soup = BeautifulSoup(response.read())
    form = list(br.forms())[0]
    form.set_all_readonly(False)
    return (soup)

def assignform(blankform):
    """ Take blank form and fill in static variables. """
    # Assign user inputted form values from file
    values = open('form_input.txt', 'r')
    for i in range(4):
        line = values.readline()
        items = line.split('=')
        blankform[items[0]] = items[2]
    for line in values:
        items = line.split('=')
        blankform[items[0]] = [items[2]]
    values.close()
    # Static variables
    blankform['RadScriptManager1_TSM'] = ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:c9cbdec3-c810-4e87-846c-fb25a7c08002:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.1.220.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:3e3b0da6-8c39-4d10-9111-25eaee1f7355:16e4e7cd:ed16cbdc:f7645509:24ee1bba:e330518b:2003d0b8:1e771326:c8618e41:a1a4383a:8674cba1:7c926187:b7778d6c:c08e9f8a:59462f1:a51ee93e'
    blankform['RadStyleSheetManager1_TSSM'] = ';Telerik.Web.UI, Version=2013.1.220.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:3e3b0da6-8c39-4d10-9111-25eaee1f7355:ed2942d4:580b2269:aac1aeb7:c73cf106:c86a4a06:4c651af2'
    blankform['ctl00_ctl63_dtEndDate_radTheDate_ClientState'] = '{"minDateStr":"1900-01-01-00-00-00","maxDateStr":"3013-11-11-00-00-00"}'
    blankform['ctl00_ctl63_dtEndDate_radTheDate_dateInput_ClientState'] = '{"enabled":true,"emptyMessage":"","validationText":"2013-08-31-00-00-00","valueAsString":"2013-08-31-00-00-00","minDateStr":"1900-01-01-00-00-00","maxDateStr":"3013-11-11-00-00-00"}'
    blankform['ctl00_ctl63_dtStartDate_radTheDate_ClientState'] = '{"minDateStr":"1900-01-01-00-00-00","maxDateStr":"3013-11-11-00-00-00"}'
    blankform['ctl00_ctl63_dtStartDate_radTheDate_dateInput_ClientState'] = '{"enabled":true,"emptyMessage":"","validationText":"1998-01-01-00-00-00","valueAsString":"1998-01-01-00-00-00","minDateStr":"1900-01-01-00-00-00","maxDateStr":"3013-11-11-00-00-00"}'
    return(blankform)

def checkvalid(html):
    """ Ensure pages returned by USA Swimming are valid. """
    # Extract table
    results = html.find('div', attrs={'id' : 'ctl63_pnlSearchResults'})
    # Checks for no results or multiple results
    error = html.find('div', attrs={'id' : 'ctl63_pnlPersonSearchResults'})
    if (results != None):
        string = "Found: " + names[0] + ', ' + names[1]
        status.write(string + '\n')
        print(string)
        extractor(results)
    elif (error != None):
        # Look for span error message to identify problem
        errormult = error.find('span', attrs={'id' : 'ctl63_lblPersonSearch'})
        if (errormult != None):
            string = "Multiple results found for: " + names[0] + ', ' + names[1]
            status.write(string + '\n')
            print(string)
            multiplefind(error)
        else:
            # Print error message if subselection returns an invalid range
            string = "No results found for: " + names[0] + ', ' + names[1]
            status.write(string + '\n')
            print(string)
    else:
        # Catch all error message
        status.write("Error not recognized. Inspect specific instance more carefully.\n")
        print("Error not recognized. Inspect specific instance more carefully.")
        exit()

def multiplefind(errorhtml):
    """ Function to search and identify desired swimmer when multiple results are returned. """
    global form
    # Re sort as desired.
    sort1 = form['ctl00$ctl63$ddlSortBy1']
    sort2 = form['ctl00$ctl63$ddlSortBy2']
    sort3 = form['ctl00$ctl63$ddlSortBy3']
    agestart = form['ctl00$ctl63$ddAgeStart']
    ageend = form['ctl00$ctl63$ddAgeEnd']
    form['ctl00$ctl63$ddlSortBy1'] = ['hytek_power_points desc']
    form['ctl00$ctl63$ddlSortBy2'] = ['']
    form['ctl00$ctl63$ddlSortBy3'] = ['']
    form['ctl00$ctl63$ddAgeStart'] = ['16']
    form['ctl00$ctl63$ddAgeEnd'] = ['24']
    form['__EVENTTARGET'] = 'ctl00$ctl63$btnSearch'
    soup = submitform(form)
    error = soup.find('div', attrs={'id' : 'ctl63_pnlPersonSearchResults'}) 
    # Find highest power point score.
    tablerows = error.table.findAll('tr')
    nextpages = tablerows[-1].findAll('a')
    # Set local values to keep
    maxp = 0
    maxpage = ''
    maxlink = ''
    # Create an array of pages to iterate over
    for num in range(len(nextpages)):
        nextpages[num] = nextpages[num]['href'][25:-5]
    nextpages.insert(0, 'ctl00$ctl63$btnSearch')
    # Iterate over all pages
    for page in nextpages:
        string = "Looking for: " + names[0] + ", " + names[1]
        print(string)
        status.write(string + '\n')
        # Iterate over multiple pages.
        form['__EVENTTARGET'] = page
        soup = submitform(form)
        results = soup.find('div', attrs={'id' : 'ctl63_pnlPersonSearchResults'})
        tablerows = results.table.findAll('tr')
        tablerows = tablerows[1:-1]
        # Iterate over names in page, save
        for name in tablerows:
            link = name.a['href'][25:-5]
            form['__EVENTTARGET'] = link
            request = form.click()
            html = br.open(request).read()
            soup = BeautifulSoup(html)
            results = soup.find('div', attrs={'id' : 'ctl63_pnlSearchResults'})
            if (results == None):
                continue
            text = results.text
            event = results.find('tr', attrs={'class' : 'DataGridItemStyle'})
            if (event == None):
                continue
            # Reject female swimmers
            if (re.search("women|girl", text, re.I)):
                continue
            pp = event.findAll('td')[5].string
            if (pp > maxp):
                toprace = event
                maxp = pp
                maxpage = page
                maxlink = link
            time.sleep(1)
    if (maxp == 0):
        status.write("No results found for: " + names[0] + ', ' + names[1] + '\n')
        print("No results found for: " + names[0] + ', ' + names[1])
    else:
        # Resort form to original settings
        form['__EVENTTARGET'] = 'ctl00$ctl63$btnSearch'
        submitform(form)
        form['__EVENTTARGET'] = maxpage
        submitform(form)
        form['__EVENTTARGET'] = maxlink
        form['ctl00$ctl63$ddlSortBy1'] = sort1
        form['ctl00$ctl63$ddlSortBy2'] = sort2
        form['ctl00$ctl63$ddlSortBy3'] = sort3
        form['ctl00$ctl63$ddAgeStart'] = agestart
        form['ctl00$ctl63$ddAgeEnd'] = ageend
        soup = submitform(form)
        # Report name and club team found here.
        # Fastest time, age, meet etc.
        results = soup.find('div', attrs={'id' : 'ctl63_pnlSearchResults'})
        info_name = results.find('span', attrs={'id' : 'ctl63_lblAthleteName'}).string
        info_club = results.find('span', attrs={'id' : 'ctl63_lblAthleteClub'}).string
        name = info_name
        club = info_club[1:-1]
        string2 = "Found: " + name + " from " + club
        raceinfo = toprace.findAll('td')
        racestring = ''
        # Write to file
        for i in range(11):
            racestring = racestring + raceinfo[i].string + ' - '
        status.write(string2+'\n')
        status.write(racestring+'\n')
        print(string2)
        print(racestring)
        extractor(results)

"""
Main function  begins here.
"""

# Import required modules and functions
import mechanize
import string
import cookielib
import re
import time
from BeautifulSoup import BeautifulSoup

# Open name input file and output files.
namefile = open('fix_input.csv', 'r')
status = open('fix_status.log', 'w')
timeresults = open('fix_results.txt', 'w')
# Establish mechanize browser
uri = "http://www.usaswimming.org/DesktopDefault.aspx?TabId=1470&Alias=Rainbow&Lang=en-US"
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.open(uri)

# Retrieve form data
form = list(br.forms())[0]
form.set_all_readonly(False)

# Assign static (and some dynamic) variables within form
form = assignform(form)
college_year = ""
college = ""

status.write("Beginning scrape ...\n")
# Create instance of form so I can use it in other functions
for aline in namefile:
    names = aline.split(',')
    form['ctl00$ctl63$txtSearchFirstName'] = names[1]
    form['ctl00$ctl63$txtSearchLastName'] = names[0]
    college_year = names[2]
    college = names[3]
    form['__EVENTTARGET'] = 'ctl00$ctl63$btnSearch'
    if (len(names) == 6):
        submitform(form)
        form['__EVENTTARGET'] = names[4].strip()
        submitform(form)
        form['__EVENTTARGET'] = names[5].strip()
        soup = submitform(form)
        result = checkvalid(soup)
        continue
    soup = submitform(form)
    results = checkvalid(soup)
    # Introduce sleep function to avoid scraping detection
    time.sleep(3)
string = "\nScrape completed\n"
print(string)
status.write(string)
namefile.close()
status.close()
timeresults.close()
exit()