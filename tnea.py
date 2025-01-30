import csv

def round_to_sum(values):
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum

    remainders = [(i, v - floored_values[i]) for i, v in enumerate(values)]
    remainders.sort(key=lambda x: x[1], reverse=True)

    for i in range(difference):
        floored_values[remainders[i][0]] += 1

    return floored_values

def process_csv(input_file, output_file, column_names):
    with open(input_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    for column_name in column_names:
        values = [float(row[column_name]) for row in data]
        adjusted_values = round_to_sum(values)

        for i, row in enumerate(data):
            row[f"Rounded_{column_name}"] = adjusted_values[i]

    fieldnames = reader.fieldnames + [f"Rounded_{col}" for col in column_names]
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Example usage
input_csv = "og.csv"  
output_csv = "newog11.csv"  
columns_to_process = ["OC", "BC", "BCM","MBC","SC","SCA","ST"]  # Replace with the column names to process

process_csv(input_csv, output_csv, columns_to_process)
