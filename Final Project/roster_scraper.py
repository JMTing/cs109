##########################################
# Scrapes schools' roster information
#
# Travis Downs
# CS 109 Final Project
# Fall, 2013
##########################################

# Import libraries
import csv
import datetime
from pattern.web import URL, DOM, plaintext, strip_between
from pattern.web import NODE, TEXT, COMMENT, ELEMENT, DOCUMENT
import itertools

# array to hold all of swimmers
swimmers = []

# gets the current year and month and adjust for url formats and updates in July
year = datetime.date.today().year
month = datetime.date.today().month
if month < 7:
	year -= 1

# define total number of years back to scrape
YEARS_TO_SCRAPE = 4

# Define vars to generate URLs for Presto Sports based sites
presto_years = []
for i in range(YEARS_TO_SCRAPE):
	presto_years.append(str(year-i) + '-' + str(year % 100 + 1 - i))
presto_urls = ["http://gocrimson.com/sports/mswimdive/", "http://www.yalebulldogs.com/sports/m-swim/", "http://www.brownbears.com/sports/m-swim/"]
presto_schools = ["Harvard", "Yale", "Brown"]

# download presto sports data
# for each school
for school in range(0,3):
    # for each year
    for presto_year in presto_years:
        print presto_schools[school] + " " + presto_year
        # generate url string, download dom
        base_url = presto_urls[school]
        url_string = base_url + presto_year + "/roster"
        url = URL(url_string)
        dom = DOM(url.download(cached=True))
        print "Downloaded."
        print "-----------------------"
        rows = (dom.by_class("roster-row0") + dom.by_class("roster-row1"))
        # go through rows of swimmers
        for row in rows:
            # adjustment for Brown 2011-12 (has an extra column), 
            # and for Brown and Harvard in general because year columns are in different place
            adj = 0
            if school == 2 and presto_year == "2011-12":
                adj = 1
            elif school == 0 or school == 2:
                adj = -1
            cells = row.by_tag("td")
            # skip divers
            if cells[1 - adj].content.strip() == "Diving":
                continue
            year_name = cells[2 + adj].content.strip()
            grad_year = 0
            # figure out graduating year
            if year_name[0:2] == "Se" or year_name[0:2] == "Sr":
                grad_year = int(presto_year[0:4]) + 1
            elif year_name[0:2] == "Ju" or year_name[0:2] == "Jr":
                grad_year = int(presto_year[0:4]) + 2
            elif year_name[0:2] == "So":
                grad_year = int(presto_year[0:4]) + 3
            elif year_name[0:2] == "Fr":
                grad_year = int(presto_year[0:4]) + 4
            # split name into first and last
            if adj == -1:
                adj = 0
            name = cells[0 + adj].by_tag("a")[0].content.split(" ", 1)
            # add swimmer (last name, first name, graduating year, school) to array
            swimmers.append([name[1].encode('ascii', 'ignore'), name[0].encode('ascii', 'ignore'), grad_year, presto_schools[school]])


# Define vars to generate URLs for Neu Lions based sites
neu_years = []
for i in range(YEARS_TO_SCRAPE):
	neu_years.append(str(year-i))
neu_urls = ["http://www.pennathletics.com/SportSelect.dbml?&DB_OEM_ID=1700&SPID=611&SPSID=10698", "http://dartmouthsports.com/SportSelect.dbml?SPID=4714&SPSID=48849",
    "http://www.gocolumbialions.com/SportSelect.dbml?&DB_OEM_ID=9600&SPID=4054&SPSID=45300", "http://www.goprincetontigers.com/SportSelect.dbml?SPSID=46494&SPID=4221&DB_OEM_ID=10600"]
neu_schools = ["Penn", "Dartmouth", "Columbia", "Princeton"]

# get neu lions data
# for each school
for school in range(0,4):
    # for each year
    for neu_year in neu_years:
        print neu_schools[school] + " " + neu_year
        # generate url string, download dom
        base_url = neu_urls[school]
        url_string = base_url + "&Q_SEASON=" + neu_year
        url = URL(url_string)
        dom = DOM(url.download(cached=True))
        print "Downloaded."
        print "-----------------------"
        rows = dom.by_class("sm")[-1].by_tag("table")[0].children[1::2]
        # go through rows of swimmers
        for row in rows:
            cells = row.by_tag("td")
            # skip divers
            if cells[1].content.strip() == "Diving":
                continue
            year_name = cells[3].content.strip() if school == 0 else cells[2].content.strip()
            grad_year = 0
            # figure out graduating year
            if year_name[0:2] == "Sr":
                grad_year = int(neu_year) + 1
            elif year_name[0:2] == "Jr":
                grad_year = int(neu_year) + 2
            elif year_name[0:2] == "So":
                grad_year = int(neu_year) + 3
            elif year_name[0:2] == "Fr":
                grad_year = int(neu_year) + 4
            # split name into first and last (adjusting for title rows)
            name = cells[0].by_tag("a")
            name = cells[0].content.split(" ", 1) if len(name) == 0 else cells[0].by_tag("a")[0].content.split(" ", 1)
            # reorder name if from Columbia or Princeton
            if school in (2,3):
                name.reverse()
            # add swimmer (last name, first name, graduating year, school) to array
            swimmers.append([name[1].encode('ascii', 'ignore').strip(",").strip(), name[0].encode('ascii', 'ignore').strip(), grad_year, neu_schools[school]])


# Get all Cornell Roster id numbers for the URLs
url = URL("http://www.cornellbigred.com/roster.aspx?roster=847")
dom = DOM(url.download(cached=True))
options = dom.by_id("ctl00_cplhMainContent_ddlPastRosters").by_tag("option")
base_url = "http://www.cornellbigred.com/roster.aspx?roster="
cornell_roster_ids = []
for option in options:
    cornell_roster_ids.append(str(option.attrs["value"]))

# define years array
cornell_years = []
for i in range(YEARS_TO_SCRAPE):
	cornell_years.append(str(year-i))

counter = 0 
for cornell_year in cornell_years:
    print counter
    print "Cornell" + " " + cornell_year
    url_string = base_url + cornell_roster_ids[counter]
    url = URL(url_string)
    dom = DOM(url.download(cached=True))
    print "Downloaded."
    print "-----------------------"
    table = dom.by_class("default_dgrd roster_dgrd")[0]
    rows = table.by_tag("tr")
    for row in rows:
        cells = row.by_tag("td")
        if len(cells) == 0:
            continue
        # skip divers
        if cells[1].content.strip() == "Dive":
            continue
        year_name = cells[2].content
        grad_year = 0
        # figure out graduating year
        if year_name[0:2] == "Sr":
            grad_year = int(cornell_year) + 1
        elif year_name[0:2] == "Jr":
            grad_year = int(cornell_year) + 2
        elif year_name[0:2] == "So":
            grad_year = int(cornell_year) + 3
        elif year_name[0:2] == "Fr":
            grad_year = int(cornell_year) + 4
        name = cells[0].by_tag("a")[0].content.split(" ", 1)
        swimmers.append([name[1].encode('ascii', 'ignore'), name[0].encode('ascii', 'ignore'), grad_year, "Cornell"])
    counter += 1



# remove duplicate swimmers and error roles
print ""
print "Number of swimmers: " + str(len(swimmers))
print "Removing duplicates..."
swimmers.sort()
swimmers = [x for x in swimmers if x[2] != 0]
swimmers = list(swimmers for swimmers,_ in itertools.groupby(swimmers))
print "Number of swimmers: " + str(len(swimmers))

# Creating the csv output file for writing into as well as defining the writer
output = open("swimmers.csv", "wb")
writer = csv.writer(output)

# add header row
print "Writing to file..."
writer.writerow(["Lastname", "Firstname", "GraduatingYear", "School"])

# write each swimmer to outputfile
for swimmer in swimmers:
    writer.writerow(swimmer)

# close output file
output.close()

print "Done!"

