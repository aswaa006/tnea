from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import csv
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def round_to_sum(values):
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum

    remainders = sorted(enumerate(values), key=lambda x: x[1] - floored_values[x[0]], reverse=True)

    for i in range(difference):
        floored_values[remainders[i][0]] += 1

    return floored_values

def process_csv(input_file, column_names):
    output_file = os.path.join(UPLOAD_FOLDER, "processed.csv")

    with open(input_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    if not data:
        flash("Uploaded CSV is empty!", "danger")
        return None, None, None

    fieldnames = list(reader.fieldnames)
    
    for column_name in column_names:
        try:
            values = [float(row[column_name]) if row[column_name] else 0 for row in data]
            adjusted_values = round_to_sum(values)

            for i, row in enumerate(data):
                rounded_col_name = f"Rounded_{column_name}"
                diff_col_name = f"Difference_{column_name}"
                row[rounded_col_name] = adjusted_values[i]
                row[diff_col_name] = round(adjusted_values[i] - values[i], 2)

            insert_index = fieldnames.index(column_name) + 1
            fieldnames = fieldnames[:insert_index] + [rounded_col_name, diff_col_name] + fieldnames[insert_index:]

        except ValueError:
            flash(f"Skipping column {column_name} due to non-numeric data.", "warning")

    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return output_file, data, fieldnames

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded.", "danger")
            return redirect(url_for("index"))

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file.", "warning")
            return redirect(url_for("index"))

        filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        columns_to_process = ["OC", "BC", "BCM", "MBC", "SC", "SCA", "ST"]
        output_file, processed_data, fieldnames = process_csv(filepath, columns_to_process)

        if not processed_data:
            return redirect(url_for("index"))

        return render_template("index.html", data=processed_data, columns=fieldnames, file_ready=True)

    return render_template("index.html", data=None, file_ready=False)

@app.route("/download")
def download():
    processed_file = os.path.join(UPLOAD_FOLDER, "processed.csv")
    if not os.path.exists(processed_file):
        flash("No processed file available for download.", "warning")
        return redirect(url_for("index"))

    return send_file(processed_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
