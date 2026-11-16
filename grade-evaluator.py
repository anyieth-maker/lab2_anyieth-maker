#!/usr/bin/env python3
"""
ALU Transcript Generator (Lab 2)

Reads a CSV file of course grades, validates it, and prints:
  - the weighted total and the GPA  (GPA = Total / 100 * 5.0)
  - PASSED / FAILED (the student must reach 50% in BOTH Formative and Summative)
  - the failed formative assignment(s) eligible for resubmission

Expected CSV format (header row required):
    assignment,group,score,weight
    Quiz,Formative,85,20

Only the Python standard library is used.
"""

import csv
import os
import sys

REQUIRED_COLUMNS = ["assignment", "group", "score", "weight"]
VALID_GROUPS = ["Formative", "Summative"]
REQUIRED_WEIGHTS = {"Formative": 60, "Summative": 40}
PASS_MARK = 50


def load_csv_data():
    """Ask for a CSV file name, read it and return a list of clean rows."""
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()
    if filename == "":
        filename = "grades.csv"
        print("No file name given, using 'grades.csv'.")

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found. "
              "Check the spelling and that it is in this folder.")
        sys.exit(1)

    if os.path.getsize(filename) == 0:
        print(f"Error: The file '{filename}' is empty. "
              "Add a header row (assignment,group,score,weight) and at least one assignment.")
        sys.exit(1)

    assignments = []
    errors = []

    try:
        with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print(f"Error: '{filename}' has no header row.")
                sys.exit(1)

            # Accept headers in any letter case and with stray spaces.
            header_map = {name.strip().lower(): name for name in reader.fieldnames if name}
            missing = [col for col in REQUIRED_COLUMNS if col not in header_map]
            if missing:
                print(f"Error: '{filename}' is missing the column(s): {', '.join(missing)}.")
                print("Expected header: assignment,group,score,weight")
                sys.exit(1)

            for line_number, row in enumerate(reader, start=2):
                values = {col: (row.get(header_map[col]) or "").strip() for col in REQUIRED_COLUMNS}

                # Skip completely empty rows.
                if all(value == "" for value in values.values()):
                    continue

                empty = [col for col, value in values.items() if value == ""]
                if empty:
                    errors.append(f"Line {line_number}: missing value(s) for {', '.join(empty)}.")
                    continue

                group = values["group"].capitalize()
                if group not in VALID_GROUPS:
                    errors.append(f"Line {line_number}: group '{values['group']}' is not valid "
                                  "(use Formative or Summative).")
                    continue

                try:
                    score = float(values["score"])
                except ValueError:
                    errors.append(f"Line {line_number}: score '{values['score']}' is not a number "
                                  "(e.g., 75 or 82.5).")
                    continue

                try:
                    weight = float(values["weight"])
                except ValueError:
                    errors.append(f"Line {line_number}: weight '{values['weight']}' is not a number "
                                  "(e.g., 20).")
                    continue

                if weight <= 0:
                    errors.append(f"Line {line_number}: weight must be greater than 0, got {values['weight']}.")
                    continue

                assignments.append({
                    "line": line_number,
                    "assignment": values["assignment"],
                    "group": group,
                    "score": score,
                    "weight": weight,
                })
    except UnicodeDecodeError:
        print(f"Error: '{filename}' is not a readable text/CSV file.")
        sys.exit(1)
    except csv.Error as error:
        print(f"Error: '{filename}' is not a valid CSV file ({error}).")
        sys.exit(1)
    except OSError as error:
        print(f"Error: could not open '{filename}' ({error}).")
        sys.exit(1)

    if errors:
        print("\nThe CSV file contains invalid rows:")
        for message in errors:
            print(f"  - {message}")
        print("Fix these rows and run the program again.")
        sys.exit(1)

    if not assignments:
        print(f"Error: '{filename}' has a header but no assignments.")
        sys.exit(1)

    return assignments


def validate_scores(data):
    """Return True if every score is between 0 and 100."""
    valid = True
    for item in data:
        if item["score"] < 0 or item["score"] > 100:
            print(f"Invalid score: '{item['assignment']}' (line {item['line']}) has "
                  f"{item['score']:g}. Scores must be between 0 and 100.")
            valid = False
    return valid


def validate_weights(data):
    """Return True if weights total 100, Formative = 60 and Summative = 40."""
    totals = {"Formative": 0.0, "Summative": 0.0}
    for item in data:
        totals[item["group"]] += item["weight"]
    overall = totals["Formative"] + totals["Summative"]

    valid = True
    if abs(overall - 100) > 1e-9:
        print(f"Invalid weights: all weights add up to {overall:g}, but they must add up to exactly 100.")
        valid = False
    for group, required in REQUIRED_WEIGHTS.items():
        if abs(totals[group] - required) > 1e-9:
            print(f"Invalid weights: {group} weights add up to {totals[group]:g}, "
                  f"but they must add up to exactly {required}.")
            valid = False
    return valid


def evaluate_grades(data):
    print("\n--- Processing Grades ---")

    scores_ok = validate_scores(data)
    weights_ok = validate_weights(data)
    if not (scores_ok and weights_ok):
        print("\nCannot calculate the transcript until the errors above are fixed.")
        sys.exit(1)
    print("All scores are between 0 and 100.")
    print("Weights are valid: Total = 100, Formative = 60, Summative = 40.")

    # Weighted points earned per category (e.g. 85% on a weight-20 task = 17 points).
    earned = {"Formative": 0.0, "Summative": 0.0}
    for item in data:
        earned[item["group"]] += item["score"] * item["weight"] / 100

    total_grade = earned["Formative"] + earned["Summative"]
    gpa = (total_grade / 100) * 5.0

    # Percentage achieved inside each category.
    formative_pct = earned["Formative"] / REQUIRED_WEIGHTS["Formative"] * 100
    summative_pct = earned["Summative"] / REQUIRED_WEIGHTS["Summative"] * 100
    passed = formative_pct >= PASS_MARK and summative_pct >= PASS_MARK

    # Resubmission: failed formatives with the highest weight (all ties included).
    failed_formatives = [item for item in data
                         if item["group"] == "Formative" and item["score"] < PASS_MARK]
    resubmit = []
    if failed_formatives:
        highest = failed_formatives[0]["weight"]
        for item in failed_formatives:
            if item["weight"] > highest:
                highest = item["weight"]
        resubmit = [item for item in failed_formatives if item["weight"] == highest]

    # ---- Transcript ----
    print("\n" + "=" * 60)
    print("TRANSCRIPT".center(60))
    print("=" * 60)
    print(f"{'Assignment':<36}{'Group':<11}{'Score':>6}{'Weight':>7}")
    print("-" * 60)
    for item in data:
        print(f"{item['assignment'][:35]:<36}{item['group']:<11}"
              f"{item['score']:>6g}{item['weight']:>7g}")
    print("-" * 60)
    print(f"Formative: {earned['Formative']:.2f} / 60  ({formative_pct:.2f}%)")
    print(f"Summative: {earned['Summative']:.2f} / 40  ({summative_pct:.2f}%)")
    print(f"Total Grade: {total_grade:.2f} / 100")
    print(f"GPA: {gpa:.4f} / 5.0")
    print(f"Status: {'PASSED' if passed else 'FAILED'}")
    if not passed:
        if formative_pct < PASS_MARK:
            print(f"  - Formative is below {PASS_MARK}%.")
        if summative_pct < PASS_MARK:
            print(f"  - Summative is below {PASS_MARK}%.")

    print("\nResubmission:")
    if resubmit:
        print("Eligible for resubmission (failed formative with the highest weight):")
        for item in resubmit:
            print(f"  - {item['assignment']} (score {item['score']:g}, weight {item['weight']:g})")
    else:
        print("  No failed formative assignments. Nothing to resubmit.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        course_data = load_csv_data()
        evaluate_grades(course_data)
    except KeyboardInterrupt:
        print("\nProgram cancelled by user.")
        sys.exit(1)
