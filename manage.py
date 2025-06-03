import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar  # Requires installation: pip install tkcalendar

# Define the path to the attendance CSV file
CSV_FILE = 'attendance.csv'

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry("900x600")
        
        # Initialize CSV file if it doesn't exist
        self.initialize_csv()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Load initial data
        self.load_records()
        
    def initialize_csv(self):
        """Initializes the CSV file with headers if it doesn't exist."""
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Timestamp'])
    
    def create_widgets(self):
        """Create all the widgets for the application."""
        # Create paned window for resizable panels
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Treeview for records
        left_panel = ttk.Frame(paned_window, padding="5")
        paned_window.add(left_panel, weight=2)
        
        # Treeview with scrollbars
        self.tree_frame = ttk.Frame(left_panel)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=('ID', 'Name', 'Timestamp'), show='headings')
        
        # Define headings
        self.tree.heading('ID', text='ID', anchor=tk.W)
        self.tree.heading('Name', text='Name', anchor=tk.W)
        self.tree.heading('Timestamp', text='Timestamp', anchor=tk.W)
        
        # Define columns
        self.tree.column('ID', width=50, stretch=tk.NO)
        self.tree.column('Name', width=150)
        self.tree.column('Timestamp', width=200)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Right panel - Form for adding/editing records
        right_panel = ttk.Frame(paned_window, padding="5")
        paned_window.add(right_panel, weight=1)
        
        # Form frame
        form_frame = ttk.LabelFrame(right_panel, text="Record Details", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # ID field
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state='readonly')
        self.id_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        # Name field
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        # Timestamp field
        ttk.Label(form_frame, text="Timestamp:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.timestamp_var = tk.StringVar()
        self.timestamp_entry = ttk.Entry(form_frame, textvariable=self.timestamp_var)
        self.timestamp_entry.grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        # Calendar button for timestamp
        self.cal_button = ttk.Button(form_frame, text="Select Date/Time", command=self.show_calendar)
        self.cal_button.grid(row=3, column=1, sticky=tk.EW, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(right_panel, padding="5")
        button_frame.pack(fill=tk.X)
        
        # Action buttons
        self.add_button = ttk.Button(button_frame, text="Add New", command=self.add_record)
        self.add_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.update_button = ttk.Button(button_frame, text="Update", command=self.update_record, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_record, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(left_panel, padding="5")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_records)
        
        # Export/Import buttons
        export_import_frame = ttk.Frame(left_panel, padding="5")
        export_import_frame.pack(fill=tk.X)
        
        ttk.Button(export_import_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(export_import_frame, text="Import from CSV", command=self.import_csv).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    def load_records(self):
        """Load records from CSV file into the treeview."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Read records from CSV
        records = []
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", f"{CSV_FILE} not found. A new file will be created.")
            self.initialize_csv()
        except Exception as e:
            messagebox.showerror("Error", f"Error reading {CSV_FILE}: {e}")
            return
        
        # Add records to treeview
        for record in records:
            if all(key in record for key in ['ID', 'Name', 'Timestamp']):
                self.tree.insert('', tk.END, values=(record['ID'], record['Name'], record['Timestamp']))
    
    def on_tree_select(self, event):
        """Handle treeview selection event."""
        selected_item = self.tree.focus()
        if selected_item:
            item_data = self.tree.item(selected_item)
            self.id_var.set(item_data['values'][0])
            self.name_var.set(item_data['values'][1])
            self.timestamp_var.set(item_data['values'][2])
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
        else:
            self.clear_form()
    
    def clear_form(self):
        """Clear the form and reset buttons."""
        self.id_var.set('')
        self.name_var.set('')
        self.timestamp_var.set('')
        self.tree.selection_remove(self.tree.selection())
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
    
    def validate_form(self):
        """Validate form fields."""
        name = self.name_var.get().strip()
        timestamp = self.timestamp_var.get().strip()
        
        if not name:
            messagebox.showwarning("Validation Error", "Name cannot be empty.")
            return False
        
        if timestamp:
            try:
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showwarning("Validation Error", "Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS.")
                return False
        
        return True
    
    def add_record(self):
        """Add a new record."""
        if not self.validate_form():
            return
        
        name = self.name_var.get().strip()
        timestamp = self.timestamp_var.get().strip()
        
        # Generate new ID
        records = []
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
        except FileNotFoundError:
            pass
        
        if records:
            try:
                new_id = max(int(record['ID']) for record in records) + 1
            except ValueError:
                messagebox.showerror("Error", "Existing IDs are not numeric. Cannot generate a new ID.")
                return
        else:
            new_id = 1
        
        # Use current timestamp if not provided
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add new record
        try:
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['ID', 'Name', 'Timestamp'])
                if records:  # If file was empty except for headers
                    writer.writerow({'ID': str(new_id), 'Name': name, 'Timestamp': timestamp})
                else:
                    writer.writeheader()
                    writer.writerow({'ID': str(new_id), 'Name': name, 'Timestamp': timestamp})
            
            # Reload records and select the new one
            self.load_records()
            self.clear_form()
            messagebox.showinfo("Success", f"Record added successfully with ID {new_id}.")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding record: {e}")
    
    def update_record(self):
        """Update an existing record."""
        if not self.validate_form():
            return
        
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        
        # Get all records
        records = []
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading records: {e}")
            return
        
        # Find and update the record
        record_id = self.id_var.get()
        updated = False
        
        for record in records:
            if record['ID'] == record_id:
                record['Name'] = self.name_var.get().strip()
                timestamp = self.timestamp_var.get().strip()
                if timestamp:  # Only update timestamp if provided
                    record['Timestamp'] = timestamp
                updated = True
                break
        
        if not updated:
            messagebox.showwarning("Not Found", f"Record with ID {record_id} not found.")
            return
        
        # Write all records back to file
        try:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['ID', 'Name', 'Timestamp'])
                writer.writeheader()
                writer.writerows(records)
            
            # Reload records and keep selection
            self.load_records()
            # Find and select the updated record
            for child in self.tree.get_children():
                if self.tree.item(child)['values'][0] == record_id:
                    self.tree.selection_set(child)
                    self.tree.focus(child)
                    break
            messagebox.showinfo("Success", "Record updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating record: {e}")
    
    def delete_record(self):
        """Delete the selected record."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        
        record_id = self.id_var.get()
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete record ID {record_id}?")
        if not confirm:
            return
        
        # Get all records except the one to delete
        records = []
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = [record for record in reader if record['ID'] != record_id]
        except Exception as e:
            messagebox.showerror("Error", f"Error reading records: {e}")
            return
        
        # Write remaining records back to file
        try:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['ID', 'Name', 'Timestamp'])
                writer.writeheader()
                writer.writerows(records)
            
            # Reload records and clear form
            self.load_records()
            self.clear_form()
            messagebox.showinfo("Success", "Record deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting record: {e}")
    
    def search_records(self, event=None):
        """Search records based on the search term."""
        search_term = self.search_var.get().lower()
        
        # Show all records if search is empty
        if not search_term:
            for child in self.tree.get_children():
                self.tree.item(child, tags=())
                self.tree.detach(child)
                self.tree.reattach(child, '', 'end')
            return
        
        # Hide non-matching records
        for child in self.tree.get_children():
            values = [str(v).lower() for v in self.tree.item(child)['values']]
            if any(search_term in value for value in values):
                self.tree.item(child, tags=('match',))
                self.tree.detach(child)
                self.tree.reattach(child, '', 'end')
            else:
                self.tree.detach(child)
    
    def show_calendar(self):
        """Show a calendar dialog to select date and time."""
        def set_datetime():
            selected_date = cal.get_date()
            selected_time = f"{hour_var.get():02d}:{minute_var.get():02d}:{second_var.get():02d}"
            self.timestamp_var.set(f"{selected_date} {selected_time}")
            top.destroy()
        
        top = tk.Toplevel(self.root)
        top.title("Select Date and Time")
        
        # Calendar
        cal_frame = ttk.Frame(top, padding="10")
        cal_frame.pack(fill=tk.BOTH, expand=True)
        
        cal = Calendar(cal_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)
        
        # Time selection
        time_frame = ttk.Frame(top, padding="10")
        time_frame.pack(fill=tk.X)
        
        ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT)
        
        hour_var = tk.IntVar(value=datetime.now().hour)
        minute_var = tk.IntVar(value=datetime.now().minute)
        second_var = tk.IntVar(value=datetime.now().second)
        
        ttk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=second_var, width=3).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(top, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Set", command=set_datetime).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=top.destroy).pack(side=tk.RIGHT)
        
        # Center the window
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)
    
    def export_csv(self):
        """Export records to a CSV file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export to CSV"
        )
        
        if not file_path:
            return
        
        try:
            # Just copy the existing file to the new location
            import shutil
            shutil.copyfile(CSV_FILE, file_path)
            messagebox.showinfo("Success", f"Records exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting records: {e}")
    
    def import_csv(self):
        """Import records from a CSV file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Import from CSV"
        )
        
        if not file_path:
            return
        
        confirm = messagebox.askyesno(
            "Confirm Import",
            "This will replace all current records with the imported data. Continue?"
        )
        if not confirm:
            return
        
        try:
            # Read the import file to validate it
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
                
                # Check required fields
                if not all(field in records[0] for field in ['ID', 'Name', 'Timestamp']):
                    messagebox.showerror("Error", "Imported file must contain 'ID', 'Name', and 'Timestamp' columns.")
                    return
            
            # Copy the import file to our CSV file
            import shutil
            shutil.copyfile(file_path, CSV_FILE)
            
            # Reload records
            self.load_records()
            self.clear_form()
            messagebox.showinfo("Success", f"Records imported successfully from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error importing records: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
