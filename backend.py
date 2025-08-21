import psycopg2

class DatabaseManager:
    def __init__(self, dbname, user, password, host="localhost"):
        # Updated connection details
        self.conn = psycopg2.connect(dbname="xime", user="postgres", password="123456", host=host)
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id VARCHAR(255) PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                department VARCHAR(50),
                hire_date DATE,
                salary DECIMAL(10, 2)
            );
        """)
        self.conn.commit()

    def add_employee(self, employee_id, first_name, last_name, department, hire_date, salary):
        self.cur.execute("""
            INSERT INTO employees (employee_id, first_name, last_name, department, hire_date, salary)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (employee_id, first_name, last_name, department, hire_date, salary))
        self.conn.commit()

    def get_employees(self, department_filter=None, sort_by=None, order="DESC"):
        query = "SELECT * FROM employees"
        params = []
        if department_filter:
            query += " WHERE department = %s"
            params.append(department_filter)
        
        if sort_by in ["salary", "hire_date"]:
            query += f" ORDER BY {sort_by} {order}"
        
        self.cur.execute(query, tuple(params))
        return self.cur.fetchall()

    def get_departments(self):
        self.cur.execute("SELECT DISTINCT department FROM employees")
        return [row[0] for row in self.cur.fetchall()]

    def update_employee(self, employee_id, first_name, last_name, department, hire_date, salary):
        self.cur.execute("""
            UPDATE employees
            SET first_name = %s, last_name = %s, department = %s, hire_date = %s, salary = %s
            WHERE employee_id = %s;
        """, (first_name, last_name, department, hire_date, salary, employee_id))
        self.conn.commit()

    def delete_employee(self, employee_id):
        self.cur.execute("DELETE FROM employees WHERE employee_id = %s;", (employee_id,))
        self.conn.commit()

    def get_business_insights(self):
        self.cur.execute("SELECT COUNT(*), SUM(salary), AVG(salary), MIN(salary), MAX(salary) FROM employees;")
        count, total_sum, avg, min_sal, max_sal = self.cur.fetchone()
        
        self.cur.execute("SELECT first_name, last_name, salary FROM employees WHERE salary = %s", (min_sal,))
        min_employee = self.cur.fetchone()

        self.cur.execute("SELECT first_name, last_name, salary FROM employees WHERE salary = %s", (max_sal,))
        max_employee = self.cur.fetchone()
        
        return {
            "total_employees": count,
            "total_salary_expense": total_sum,
            "average_salary": avg,
            "lowest_paid_employee": min_employee,
            "highest_paid_employee": max_employee
        }
        
    def __del__(self):
        self.cur.close()
        self.conn.close()