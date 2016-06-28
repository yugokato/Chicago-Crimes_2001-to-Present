import os
import csv
import pymongo
from datetime import datetime


client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.chicago

DIR = os.getcwd()
FILENAME = 'Crimes_-_2001_to_present.csv'
FILEPATH = os.path.join(DIR, FILENAME)

days = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

def bulkInsert(docs):
    db.crimes.insert_many(docs, ordered=True)
    return

docs = []
print "%s: Started reading the csv file" % datetime.now()
with open(FILEPATH, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    # Skip the very first header line
    reader.next()
    i = 0
    for line in reader:
        doc = {}
        doc['ID'] = int(line[0].strip())
        doc['Case Number'] = line[1].strip()
        doc['Year'] = int(line[17].strip())
        doc['Date'] = datetime.strptime(line[2].strip(), "%m/%d/%Y %I:%M:%S %p")
        doc['DayOfWeek'] = days[doc['Date'].weekday()]
        doc['Block'] = line[3].strip()
        if line[5].strip() == "NON - CRIMINAL":
            line[5] = "NON-CRIMINAL"
        doc['Category'] = {
                'IUCR': line[4].strip(),
                'Primary Type': line[5].strip(),
                'Description': line[6].strip(),
                'FBI Code': line[14].strip()
                }
        doc['Arrest'] = line[8].strip()
        doc['Domestic'] = line[9].strip()
        doc['Beat'] = int(line[10].strip())
        doc['Distinct'] = line[11].strip()
        if line[12].strip():
            doc['Ward'] = int(line[12].strip())
        else:
            doc['Ward'] = "N.A"
        if line[13].strip():
            doc['Community Area'] = int(line[13].strip())
        else:
            doc['Community Area'] = "N.A"
        if line[19].strip() and line[20].strip():
            doc['Location'] = {
                    'type': 'Point',
                    'coordinates': [float(line[20].strip()), float(line[19].strip())]
                    }
        else:
            doc['Location'] = {
                    'type': 'Point',
                    'coordinates': [-1, -1]
                    }
        doc['Location Description'] = line[7].strip()
        doc['Updated On'] = datetime.strptime(line[18].strip(), "%m/%d/%Y %I:%M:%S %p")
        
        docs.append(doc)
        i += 1
        # Bulk insert every 3000 records
        if i % 3000 == 0:
            db.crimes.insert_many(docs, ordered=True)
            docs = []
    # Bulk insert the rest to DB        
    db.crimes.insert_many(docs, ordered=True)
    print "%s: Ended reading the csv file (Total %s records)" % (datetime.now(), i)



'''
Before (csv)

{
 0    "ID": 2593265,
 1    "Case Number": "HJ188978",
 2    "Date": "02/17/2003 05:16:57 PM",
 3    "Block": "030XX N ROCKWELL ST",
 4    "IUCR": 0610,
 5    "Primary Type": "BURGLARY",
 6    "Description": "FORCIBLE ENTRY",
 7    "Location Description": "COMMERCIAL / BUSINESS OFFICE",
 8    "Arrest": "false",
 9    "Domestic": "false",
10    "Beat": 1411,
11    "Distinct": 014,
12    "Ward": 1,
13    "Community Area": 21,
14    "FBI Code": 05,
15    "X Coordinate": 1158504,
16    "Y Coordinate": 1920378,
17    "Year": 2003,
18    "Updated On": "04/15/2016 08:55:02 AM",
19    "Latitude": 41.937259186,
20    "Longtitude": -87.692882474,
21    "Location": "(41.937259186, -87.692882474)"
}


After(document)
{
    "_id" : ObjectId("576e2a9fb2393b426d9e99c5"),
    "DayOfWeek" : "Monday",
    "Category" : {
        "FBI Code" : "05",
        "Primary Type" : "BURGLARY",
        "IUCR" : "0610",
        "Description" : "FORCIBLE ENTRY"
    },
    "Updated On" : ISODate("2016-04-15T08:55:02Z"),
    "Location Description" : "COMMERCIAL / BUSINESS OFFICE",
    "Beat" : 1411,
    "Domestic" : "false",
    "Arrest" : "false",
    "Distinct" : "014",
    "Location" : {
        "type" : "Point",
        "coordinates" : [
            -87.692882474,
            41.937259186
        ]
    },
    "Community Area" : 21,
    "Year" : 2003,
    "Date" : ISODate("2003-02-17T17:16:57Z"),
    "Ward" : 1,
    "Case Number" : "HJ188978",
    "ID" : 2593265,
    "Block" : "030XX N ROCKWELL ST"
}
'''




