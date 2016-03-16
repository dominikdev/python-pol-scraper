from HTMLParser import HTMLParser
import urllib2
import tempfile
from pymongo import MongoClient

client = MongoClient()
db = client.test
pol = db.polit

allData = dict()
tf = tempfile.TemporaryFile()
canidates = [
    {"first_name": "Donald", "last_name": "Trump", "party": "Republican"},
    {"first_name": "Bernie", "last_name": "Sanders", "party": "Democrat"},
    {"first_name": "Hillary", "last_name": "Clinton", "party": "Democrat"},
    {"first_name": "Ted", "last_name": "Cruz", "party": "Republican"},
    {"first_name": "Marco", "last_name": "Rubio", "party": "Republican"},
    {"first_name": "John", "last_name": "Kasich", "party": "Republican"}
]


class MyHTMLParser(HTMLParser):
    """This class divides the html by tag."""

    def handle_starttag(self, tag, attrs):
        """Handle Starting Tag."""
        tf.write('tag:' + str(tag))

    def handle_data(self, data):
        """Handle Data in tag."""
        tf.write('|data: ' + str(data.replace("/\n/\r\t+/g", " ")) + "\n")

parser = MyHTMLParser()


def gethtml(url):
    """Read HTML from url."""
    response = urllib2.urlopen(url)
    r = response.read()
    return r


def geturl(can):
    """Create url from candidate name."""
    url = "http://www.ontheissues.org/" + can['first_name']
    url = url + "_" + can['last_name'] + ".htm"
    return url


def handlerawdata(data, can):
    """Handle parsed html data."""
    isu = False
    curkey = ""
    poldata = dict()
    srch = can['first_name'] + " " + can['last_name'] + " on"
    for a in data:
        if srch in a and "on the Issues" not in a:
            isu = True
            curkey = unicode(a.replace(srch, '').strip())
            poldata[curkey] = []
        if isu is True:
            if "tag:li" in a:
                q = a.replace('tag:li|data: ', '').replace('\r', '')
                poldata[curkey].append(unicode(q, 'utf8', 'replace'))
    return poldata


def struturedatatodb(data, can):
    """Combine candidate info and quotes then insert into mongodb."""
    s = {"candidate": can, "stance": data}
    pol.insert_one(s)


def getcanidatequotes():
    """Run through each canidate."""
    for a in canidates:
        url = geturl(a)
        parser.feed(gethtml(url))
        tf.seek(0)
        file = tf.read()
        f = file.split('\n')
        rd = handlerawdata(f, a)
        struturedatatodb(rd, a)

getcanidatequotes()
