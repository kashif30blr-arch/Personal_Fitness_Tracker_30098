import streamlit as st
import pandas as pd
from backend import DatabaseManager
from datetime import datetime

# Initialize database connection
db = DatabaseManager(dbname="xime", user="postgres", password="123456")
db.create_table()

st.set_page_config(page_title="Urban Asset Tracker", layout="wide")
st.title("🏙️ Urban Asset Tracker: Employee Directory & Analytics")

# --- CRUD Operations ---
st.header("Employee Management (CRUD)")

# Form for adding/updating employees
with st.expander("Add/Update Employee"):
    with st.form("employee_form", clear_on_submit=True):
        st.subheader("Employee Details")
        employee_id = st.text_input("Employee ID (Required for all operations)")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        department = st.text_input("Department")
        hire_date = st.date_input("Hire Date", datetime.now())
        salary = st.number_input("Salary", min_value=0.0, format="%.2f")
        col1, col2, col3 = st.columns(3)
        with col1:
            add_button = st.form_submit_button("Add Employee")
        with col2:
            update_button = st.form_submit_button("Update Employee")
        with col3:
            delete_button = st.form_submit_button("Delete Employee")

    if add_button:
        if employee_id and first_name and last_name and department and hire_date and salary:
            try:
                db.add_employee(employee_id, first_name, last_name, department, hire_date, salary)
                st.success(f"Employee {first_name} {last_name} added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error(f"Error: Employee with ID {employee_id} already exists.")
        else:
            st.warning("Please fill in all employee details.")

    if update_button:
        if employee_id:
            db.update_employee(employee_id, first_name, last_name, department, hire_date, salary)
            st.success(f"Employee {employee_id} updated successfully!")
        else:
            st.error("Please provide an Employee ID to update.")
    
    if delete_button:
        if employee_id:
            db.delete_employee(employee_id)
            st.success(f"Employee {employee_id} deleted successfully.")
        else:
            st.error("Please provide an Employee ID to delete.")

# --- Employee Directory & Filtering ---
st.header("Employee Directory")
col1, col2 = st.columns(2)

with col1:
    departments = ["All"] + db.get_departments()
    selected_department = st.selectbox("Filter by Department", departments)

with col2:
    sort_option = st.selectbox("Sort by", ["salary", "hire_date"], index=0)
    sort_order = st.radio("Order", ["DESC", "ASC"], index=0)

# Fetch data based on filters and sorting
if selected_department == "All":
    employee_data = db.get_employees(sort_by=sort_option, order=sort_order)
else:
    employee_data = db.get_employees(department_filter=selected_department, sort_by=sort_option, order=sort_order)

# Create a DataFrame for display
if employee_data:
    columns = ["Employee ID", "First Name", "Last Name", "Department", "Hire Date", "Salary"]
    df = pd.DataFrame(employee_data, columns=columns)
    st.dataframe(df)
else:
    st.info("No employees found.")

# --- Business Insights ---
st.header("Business Insights")
insights = db.get_business_insights()

if insights["total_employees"] > 0:
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Employees", insights["total_employees"])
    
    with col2:
        st.metric("Total Monthly Salary Expense", f"£{insights['total_salary_expense']:.2f}")
    
    with col3:
        st.metric("Average Salary", f"£{insights['average_salary']:.2f}")
        
    st.markdown("---")
    
    with col4:
        st.metric("Highest Paid Employee", f"£{insights['highest_paid_employee'][2]:.2f}")
        st.write(f"Name: {insights['highest_paid_employee'][0]} {insights['highest_paid_employee'][1]}")
    
    with col5:
        st.metric("Lowest Paid Employee", f"£{insights['lowest_paid_employee'][2]:.2f}")
        st.write(f"Name: {insights['lowest_paid_employee'][0]} {insights['lowest_paid_employee'][1]}")
else:
    st.info("No data available to generate business insights.")