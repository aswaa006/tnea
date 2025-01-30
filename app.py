from flask import Flask, render_template, request, send_file
import csv
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def process_csv(input_file, column_names):
    output_file = "processed.csv"
    
    with open(input_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    for column_name in column_names:
        try:
            values = [float(row[column_name]) for row in data]
            adjusted_values = round_to_sum(values)

            for i, row in enumerate(data):
                row[f"Rounded_{column_name}"] = adjusted_values[i]
        except ValueError:
            print(f"Skipping column {column_name} due to non-numeric data.")

    fieldnames = reader.fieldnames + [f"Rounded_{col}" for col in column_names]
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return output_file, data, fieldnames

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Process CSV with selected columns
        columns_to_process = ["OC", "BC", "BCM", "MBC", "SC", "SCA", "ST"]  # Change as needed
        output_file, processed_data, fieldnames = process_csv(filepath, columns_to_process)

        return render_template("index.html", data=processed_data, columns=fieldnames, file_ready=True)

    return render_template("index.html", data=None, file_ready=False)

@app.route("/download")
def download():
    return send_file("processed.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
