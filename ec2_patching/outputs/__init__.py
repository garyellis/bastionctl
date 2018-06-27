import csv

def to_csv(content, filename, append=False, keys=[]):
    """
    """
    if not keys:
        keys = sorted(content[0].keys())

    with open(filename, 'w') as stream:
        csv_writer = csv.DictWriter(stream, keys)
        csv_writer.writeheader()
        csv_writer.writerows(content)
