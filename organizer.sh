#!/bin/bash
# organizer.sh - archives grades.csv with a timestamp, resets the workspace,
# and logs every run to organizer.log.

SOURCE_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# 1. Create the archive directory if it does not exist.
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir "$ARCHIVE_DIR" || { echo "Error: could not create '$ARCHIVE_DIR' directory."; exit 1; }
    echo "Created directory: $ARCHIVE_DIR"
fi

# Stop if there is nothing to archive.
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: '$SOURCE_FILE' was not found in $(pwd). Nothing to archive."
    exit 1
fi

# 2. Archive grades.csv with a timestamp, e.g. grades_20251105-170000.csv
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

mv "$SOURCE_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME" || { echo "Error: could not move '$SOURCE_FILE'."; exit 1; }
echo "Archived: $SOURCE_FILE -> $ARCHIVE_DIR/$ARCHIVED_NAME"

# 3. Reset the workspace with a new, empty grades.csv.
touch "$SOURCE_FILE"
echo "Created new empty $SOURCE_FILE"

# 4. Append the details to organizer.log (never overwritten).
echo "[$TIMESTAMP] Original: $SOURCE_FILE | Archived as: $ARCHIVE_DIR/$ARCHIVED_NAME" >> "$LOG_FILE"
echo "Logged to $LOG_FILE"
