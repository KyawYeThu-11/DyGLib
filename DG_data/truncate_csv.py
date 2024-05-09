import csv
import argparse

def truncate_csv(read_file, write_file, n):
    # Read all rows from the CSV file
    with open(read_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    # Truncate the list to remove the last n rows
    truncated_data = data[:-n]

    # Write the truncated data back to the CSV file
    with open(write_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(truncated_data)



parser = argparse.ArgumentParser('Interface for preprocessing datasets')
parser.add_argument('--read', type=str)
parser.add_argument('--write', type=str)
parser.add_argument('--rows', type=int)

args = parser.parse_args()
read_file = args.read  # Replace with your CSV file path
write_file = args.write  # Replace with your CSV file path
rows = args.rows # rows to delete

truncate_csv(read_file, write_file, rows)