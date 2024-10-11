from faker import Faker
import random
import csv

fake = Faker('en_IN')

def generate_employee_data(num_employees):
    employees = []
    dept_ids = [random.randint(100, 999) for _ in range(5)]  # Limiting to 5 departments

    for i in range(num_employees):
        emp_id = i + 1000
        emp_name = fake.name()
        supervisor_id = random.choice(range(1000, emp_id)) if i > 0 else None  # Supervisor from previous employees
        dept_id = random.choice(dept_ids)
        employees.append((emp_id, emp_name, supervisor_id, dept_id))

    return employees

def write_to_csv(employees, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["emp_id", "emp_name", "supervisor_id", "dept_id"])
        writer.writerows(employees)

if __name__ == "__main__":
    random.seed(42)  # Set seed for reproducibility
    num_employees = 1000
    employees = generate_employee_data(num_employees)
    write_to_csv(employees, "employee_data.csv")
    print(f"{num_employees} employee records have been written to employee_data.csv")
