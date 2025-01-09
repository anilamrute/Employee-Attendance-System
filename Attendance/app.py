from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Excel files
EMPLOYEE_FILE = 'employees.xlsx'
ATTENDANCE_FILE = 'attendance.xlsx'
HOLIDAY_FILE = 'holidays.xlsx'

# Load employees from Excel
def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        return pd.read_excel(EMPLOYEE_FILE).to_dict('records')
    return []

# Save employees to Excel
def save_employees(employees):
    df = pd.DataFrame(employees)
    df.to_excel(EMPLOYEE_FILE, index=False)

# Load attendance from Excel
def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        return pd.read_excel(ATTENDANCE_FILE).to_dict('records')
    return []

# Save attendance to Excel
def save_attendance(attendance):
    df = pd.DataFrame(attendance)
    df.to_excel(ATTENDANCE_FILE, index=False)

# Load holidays from Excel
def load_holidays():
    if os.path.exists(HOLIDAY_FILE):
        return pd.read_excel(HOLIDAY_FILE).to_dict('records')
    return []

# Save holidays to Excel
def save_holidays(holidays):
    df = pd.DataFrame(holidays)
    df.to_excel(HOLIDAY_FILE, index=False)

# Default Page (Mark Attendance)
@app.route('/', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        # Process attendance form data
        employees = load_employees()
        attendance_records = load_attendance()
        holidays = load_holidays()
        
        # Get selected date
        selected_date = request.form['date']
        
        for emp in employees:
            emp_id = str(emp['ID'])
            
            # Check if the selected date is a holiday for this employee
            is_holiday = any(holiday['Employee ID'] == emp['ID'] and holiday['Date'] == selected_date for holiday in holidays)
            
            status = 'Holiday' if is_holiday else ('Present' if emp_id in request.form else 'Absent')
            
            # Check if attendance for this employee on this date already exists
            existing_record = next((record for record in attendance_records if record['Employee ID'] == emp['ID'] and record['Date'] == selected_date), None)
            
            if existing_record:
                # Update existing record
                existing_record['Status'] = status
            else:
                # Add new attendance record
                attendance_records.append({
                    'Employee ID': emp['ID'],
                    'Name': emp['Name'],
                    'Date': selected_date,
                    'Status': status
                })
        
        # Save attendance to Excel
        save_attendance(attendance_records)
        flash('Attendance submitted successfully')
        return redirect(url_for('mark_attendance'))
    
    # Display the attendance form with today's date as default
    employees = load_employees()
    attendance_records = load_attendance()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Filter attendance records for today
    today_attendance = [record for record in attendance_records if record['Date'] == today]
    
    return render_template('mark_attendance.html', employees=employees, attendance=today_attendance, today=today)

# Add Employee Page
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Add employee to the Excel file
        name = request.form['name']
        role = request.form['role']
        employees = load_employees()
        employees.append({'ID': len(employees) + 1, 'Name': name, 'Role': role})
        save_employees(employees)
        flash('Employee added successfully')
        return redirect(url_for('add_employee'))
    
    # Display the form to add employees
    return render_template('add_employee.html')

# Add Holiday for Specific Employee
@app.route('/add_holiday', methods=['GET', 'POST'])
def add_holiday():
    employees = load_employees()
    
    if request.method == 'POST':
        # Add holiday to the Excel file
        employee_id = int(request.form['employee_id'])
        date = request.form['date']
        description = request.form['description']
        
        holidays = load_holidays()
        holidays.append({
            'Employee ID': employee_id,
            'Date': date,
            'Description': description
        })
        save_holidays(holidays)
        flash('Holiday added successfully')
        return redirect(url_for('add_holiday'))
    
    # Display the form to add holidays
    return render_template('add_holiday.html', employees=employees)

# Reports Page
@app.route('/reports')
def reports():
    attendance_records = load_attendance()
    return render_template('reports.html', attendance=attendance_records)

# Export Attendance Data
@app.route('/export_attendance')
def export_attendance():
    attendance_records = load_attendance()
    df = pd.DataFrame(attendance_records)
    
    # Save to Excel
    export_file = 'attendance_export.xlsx'
    df.to_excel(export_file, index=False)
    
    # Send the file to the user
    return send_file(export_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)