import json
import csv

# Opening JSON file and loading the data
# into the variable data
with open('full_output.json') as json_file:
    data = json.load(json_file)

# now we will open a file for writing
data_file = open('results.csv', 'w')

# create the csv writer object
csv_writer = csv.writer(data_file)

# Counter variable used for writing
# headers to the CSV file
count = 0

for res in data:
    if count == 0:
        # Writing headers of CSV file
        header = res.keys()
        csv_writer.writerow(header)
        count += 1

    # Writing data of CSV file
    csv_writer.writerow(res.values())

data_file.close()