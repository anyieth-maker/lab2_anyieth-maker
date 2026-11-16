# Lab 2: ALU Transcript Generator

A Python application that reads a student's course grades from `grades.csv`, validates them, and prints a transcript with the GPA, the final status (PASSED / FAILED), and the assignment(s) eligible for resubmission. A Bash script, `organizer.sh`, archives the grades file and logs each run.

Only the Python standard library is used. There are no external dependencies.

## Repository contents

| File | Purpose |
|------|---------|
| `grade-evaluator.py` | Validates grades and weights, calculates the GPA, pass/fail status and resubmission |
| `grades.csv` | Course grades data |
| `organizer.sh` | Archives `grades.csv` with a timestamp and logs the action |
| `Readme.md` | This file |

## CSV format

```
assignment,group,score,weight
Quiz,Formative,85,20
Midterm Project - Simple Calculator,Summative,70,20
```

- `group` must be `Formative` or `Summative`
- `score` is a number from 0 to 100 (e.g. `75` or `82.5`)
- `weight` is a number greater than 0 (e.g. `20`)

## How to run the Python app

```bash
python3 grade-evaluator.py
```

Enter the file name when asked, e.g. `grades.csv`. Pressing Enter with no name uses `grades.csv`.

## What the program checks and calculates

1. **Grade validation:** every score must be between 0 and 100.
2. **Weight validation:** all weights must add up to exactly 100, with Formative = 60 and Summative = 40.
3. **GPA:** each assignment contributes `score × weight / 100` points. The points are added up to give the Total Grade, and `GPA = (Total Grade / 100) × 5.0`.
4. **Pass/Fail:** the student passes only if they reach at least 50% in **both** categories (Formative points / 60 and Summative points / 40). The output is `PASSED` or `FAILED`.
5. **Resubmission:** the failed formative assignment (score below 50) with the highest weight is eligible. If several are tied for the highest weight, all of them are listed.

### Example output (provided `grades.csv`)

```
Formative: 34.00 / 60  (56.67%)
Summative: 26.00 / 40  (65.00%)
Total Grade: 60.00 / 100
GPA: 3.0000 / 5.0
Status: PASSED

Eligible for resubmission (failed formative with the highest weight):
  - Group Exercise (score 40, weight 20)
  - Functions and Debugging Lab (score 45, weight 20)
```

## Error handling

The program prints a clear message and stops, instead of crashing, when:

- the file does not exist, or is empty
- the header is missing or a required column is absent
- a row has an empty field, or an invalid group
- a score or weight is not a number
- a score is outside 0–100
- the weights do not total 100, or the Formative/Summative split is not 60/40

Completely blank rows are skipped.

## How to run the organizer

```bash
bash organizer.sh
```

On each run, the script:

1. Creates an `archive/` directory if it does not exist.
2. Moves `grades.csv` to `archive/grades_YYYYMMDD-HHMMSS.csv`.
3. Creates a new, empty `grades.csv`.
4. Appends a line to `organizer.log` with the timestamp, the original filename and the archived filename. The log keeps entries from every run.

Example log entry:

```
[20251105-170000] Original: grades.csv | Archived as: archive/grades_20251105-170000.csv
```

If `grades.csv` is missing, the script prints an error and exits with code 1.

> **Note:** running `organizer.sh` empties `grades.csv`. To run the Python app again afterwards, copy the archived file back or add new grades.
