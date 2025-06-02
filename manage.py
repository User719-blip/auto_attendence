import csv
import os
import sys
from datetime import datetime

# Define the path to the attendance CSV file
CSV_FILE = 'attendance.csv'

def initialize_csv():
    """
    Initializes the CSV file with headers if it doesn't exist.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Timestamp'])
        print(f"Created {CSV_FILE} with headers.")

def read_attendance():
    """
    Reads the attendance records from the CSV file.
    Returns:
        List of dictionaries containing attendance records.
    """
    records = []
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except FileNotFoundError:
        print(f"{CSV_FILE} not found. Initializing a new file.")
        initialize_csv()
    except Exception as e:
        print(f"Error reading {CSV_FILE}: {e}")
    return records

def write_attendance(records):
    """
    Writes the attendance records to the CSV file.
    Args:
        records: List of dictionaries containing attendance records.
    """
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['ID', 'Name', 'Timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)
    except Exception as e:
        print(f"Error writing to {CSV_FILE}: {e}")

def display_records(records):
    """
    Displays all attendance records in a tabular format.
    Args:
        records: List of dictionaries containing attendance records.
    """
    if not records:
        print("No attendance records found.")
        return
    
    print("\nAttendance Records:")
    print("{:<5} {:<25} {:<20}".format("ID", "Name", "Timestamp"))
    print("-" * 55)
    
    for record in records:
        # Validate that all required keys are present
        if all(key in record for key in ['ID', 'Name', 'Timestamp']):
            print("{:<5} {:<25} {:<20}".format(record['ID'], record['Name'], record['Timestamp']))
        else:
            print("Record is missing required fields:", record)
    
    print()

def add_record(records):
    """
    Adds a new attendance record.
    Args:
        records: List of dictionaries containing attendance records.
    """
    name = input("Enter Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    # Generate a new unique ID
    if records:
        try:
            new_id = max(int(record['ID']) for record in records) + 1
        except ValueError:
            print("Existing IDs are not numeric. Cannot generate a new ID.")
            return
    else:
        new_id = 1
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Append the new record
    records.append({'ID': str(new_id), 'Name': name, 'Timestamp': timestamp})
    write_attendance(records)
    print(f"Record added successfully with ID {new_id}.\n")

def edit_record(records):
    """
    Edits an existing attendance record.
    Args:
        records: List of dictionaries containing attendance records.
    """
    if not records:
        print("No records to edit.")
        return
    display_records(records)
    try:
        record_id = input("Enter the ID of the record you want to edit: ").strip()
        record = next((r for r in records if r['ID'] == record_id), None)
        if not record:
            print(f"No record found with ID {record_id}.\n")
            return
        print(f"Editing Record ID {record_id}:")
        new_name = input(f"Enter new name (leave blank to keep '{record.get('Name', '')}'): ").strip()
        new_timestamp = input(f"Enter new timestamp (leave blank to keep '{record.get('Timestamp', '')}'): ").strip()
        if new_name:
            record['Name'] = new_name
        if new_timestamp:
            # Validate timestamp format
            try:
                datetime.strptime(new_timestamp, "%Y-%m-%d %H:%M:%S")
                record['Timestamp'] = new_timestamp
            except ValueError:
                print("Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS. Changes to timestamp not saved.")
        write_attendance(records)
        print(f"Record ID {record_id} updated successfully.\n")
    except Exception as e:
        print(f"An error occurred: {e}\n")

def delete_record(records):
    """
    Deletes an attendance record.
    Args:
        records: List of dictionaries containing attendance records.
    """
    if not records:
        print("No records to delete.")
        return
    display_records(records)
    try:
        record_id = input("Enter the ID of the record you want to delete: ").strip()
        record = next((r for r in records if r['ID'] == record_id), None)
        if not record:
            print(f"No record found with ID {record_id}.\n")
            return
        confirm = input(f"Are you sure you want to delete record ID {record_id}? (y/n): ").strip().lower()
        if confirm == 'y':
            records.remove(record)
            write_attendance(records)
            print(f"Record ID {record_id} deleted successfully.\n")
        else:
            print("Deletion canceled.\n")
    except Exception as e:
        print(f"An error occurred: {e}\n")

def main_menu():
    """
    Displays the main menu and handles user input.
    """
    initialize_csv()
    records = read_attendance()
    
    while True:
        print("===== Attendance Management System =====")
        print("1. View Attendance Records")
        print("2. Add a New Record")
        print("3. Edit an Existing Record")
        print("4. Delete a Record")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()
        print()
        if choice == '1':
            records = read_attendance()
            display_records(records)
        elif choice == '2':
            records = read_attendance()
            add_record(records)
        elif choice == '3':
            records = read_attendance()
            edit_record(records)
        elif choice == '4':
            records = read_attendance()
            delete_record(records)
        elif choice == '5':
            print("Exiting Attendance Management System. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please enter a number between 1 and 5.\n")

if __name__ == "__main__":
    main_menu()
