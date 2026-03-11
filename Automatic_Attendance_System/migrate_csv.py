import csv
import os
import codecs

filename = 'Attendance.csv'
if os.path.exists(filename):
    with codecs.open(filename, 'r', 'utf-8-sig') as f:
        reader = csv.reader(f)
        lines = list(reader)
        
    if lines and 'Time' in lines[0]:
        new_lines = []
        for i, row in enumerate(lines):
            if not row or not any(row): continue # skip empty lines
            if i == 0:
                header = row[:4] + ['In Time', 'Out Time'] + row[5:]
                new_lines.append(header)
            else:
                new_row = row[:4] + [row[4], 'N/A'] + row[5:]
                new_lines.append(new_row)
                
        with codecs.open(filename, 'w', 'utf-8-sig') as f:
            for row in new_lines:
                f.write(','.join(row) + '\n')
        print("Migrated successfully")
    else:
        print("Already migrated or empty")
else:
    print("File not found")
