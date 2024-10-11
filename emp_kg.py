from neo4j import GraphDatabase
import csv
import os
from dotenv import load_dotenv
import logging
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s",filename="kg_log.txt",filemode="w")

logging.info("Start connection to Neo4j")
driver=GraphDatabase.driver(NEO4J_URI,auth=(NEO4J_USERNAME,NEO4J_PASSWORD))
logging.info("Connection to Neo4j Established")

def create_kg(tx,employee):
    emp_id,emp_name,supervisor_id,dept_id=employee

    logging.info(f"Creating node for emp_id:{emp_id}")
    tx.run("MERGE(emp_idNode:EmpID{emp_id:$emp_id_p})",emp_id_p=emp_id)#emp_id node
    logging.info(f"Node for emp_id:{emp_id} created successfully")

    logging.info(f"Creating node for emp_name:{emp_name}")
    tx.run("MERGE(emp_nameNode:EmpName{emp_name:$emp_name_p})",emp_name_p=emp_name)#emp_name node
    logging.info(f"Node for emp_name:{emp_name} created successfully")

    is_supervisor="Yes" if supervisor_id and supervisor_id!="None" else "No"
    logging.info(f"Creating SupervisorStatus node for emp_id:{emp_id},is_supervisor:{is_supervisor}")
    tx.run("MERGE (supervisor_StatusNode:SupervisorStatus{emp_id:$emp_id_p,is_supervisor:$is_supervisor_p})",
           emp_id_p=emp_id,is_supervisor_p=is_supervisor)#supervisor node
    logging.info(f"SupervisorStatus node for emp_id:{emp_id},is_supervisor:{is_supervisor} created succesfully")


    logging.info(f"Creating Dept Node for dept_id: {dept_id}")  
    tx.run("MERGE(dept_idNode:DepartmentID{dept_id:$dept_id_p})",dept_id_p=dept_id)
    logging.info(f"Node for dept_id:{dept_id} created succesfully")   

    #relationships
    logging.info(f"Creating HAS_NAME relationship for emp_id: {emp_id}")
    tx.run(
        "MERGE (emp_idNode:EmpID {emp_id: $emp_id_p})"
        "MERGE (emp_nameNode:EmpName {emp_name: $emp_name_p})"
        "MERGE (emp_idNode)-[:HAS_NAME]->(emp_nameNode)",  # Corrected emp_IdNode to emp_idNode
        emp_id_p=emp_id, emp_name_p=emp_name
    )
    logging.info(f"Created HAS_NAME relationship for emp_id: {emp_id}")

    logging.info(f"Creating HAS_SUPERVISOR_STATUS relationship for emp_id: {emp_id}")
    tx.run(
        "MERGE (emp_idNode:EmpID {emp_id: $emp_id_p})"
        "MERGE (supervisor_StatusNode:SupervisorStatus {emp_id: $emp_id_p, is_supervisor: $is_supervisor_p})"
        "MERGE (emp_idNode)-[:HAS_SUPERVISOR_STATUS]->(supervisor_StatusNode)",
        emp_id_p=emp_id, is_supervisor_p=is_supervisor
    )
    logging.info(f"Created HAS_SUPERVISOR_STATUS relationship for emp_id: {emp_id}")

    logging.info(f"Creating BELONGS_TO relationship for emp_id: {emp_id} and dept_id: {dept_id}")
    tx.run(
        "MERGE (emp_idNode:EmpID {emp_id: $emp_id_p})"
        "MERGE (dept_idNode:DepartmentID {dept_id: $dept_id_p})"
        "MERGE (emp_idNode)-[:BELONGS_TO]->(dept_idNode)",
        emp_id_p=emp_id, dept_id_p=dept_id
    )    
    logging.info(f"Created BELONGS_TO relationship for emp_id: {emp_id} and dept_id: {dept_id}")

    if supervisor_id and supervisor_id != 'None':
        logging.info(f"Creating REPORTS_TO relationship for emp_id: {emp_id} to supervisor_id: {supervisor_id}")
        tx.run(
            "MERGE (emp_idNode:EmpID {emp_id: $emp_id_p})"
            "MERGE (supervisorNode:EmpID {emp_id: $supervisor_id_p})"
            "MERGE (emp_idNode)-[:REPORTS_TO]->(supervisorNode)",
            emp_id_p=emp_id, supervisor_id_p=supervisor_id
        )
        logging.info(f"Created REPORTS_TO relationship for emp_id: {emp_id} to supervisor_id: {supervisor_id}")


        logging.info(f"Creating SUPERVISES relationship for supervisor_id: {supervisor_id} to emp_id: {emp_id}")
        tx.run(
            "MERGE (supervisorNode:EmpID {emp_id: $supervisor_id_p})"
            "MERGE (emp_idNode:EmpID {emp_id: $emp_id_p})"
            "MERGE (supervisorNode)-[:SUPERVISES]->(emp_idNode)",
            emp_id_p=emp_id, supervisor_id_p=supervisor_id
        )
def load_to_neo4j(file_path):
    logging.info(f"Loading data from {file_path}")
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        with driver.session() as session:
            for row in reader:
                logging.info(f"Processing row: {row}")
                session.execute_write(create_kg, row)  # Changed write_transaction to execute_write

if __name__ == "__main__":
    file_path = "employee_data.csv"
    load_to_neo4j(file_path)
    logging.info("Knowledge graph created successfully!")
    driver.close()
