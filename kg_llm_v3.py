import anthropic
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
import pandas as pd
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

schema = """{
  "nodes": [
    { "label": "EmpID" },
    { "label": "EmpName" },
    { "label": "SupervisorStatus" },
    { "label": "DepartmentID" }
  ],
  "relationships": [
    { "type": "HAS_NAME" },
    { "type": "HAS_SUPERVISOR_STATUS" },
    { "type": "BELONGS_TO" },
    { "type": "REPORTS_TO" },
    { "type": "SUPERVISES" }
  ],
  "properties": [
    "emp_id", "emp_name", "is_supervisor", "dept_id", "id", "name",
    "data", "nodes", "relationships", "style", "visualisation"
  ],
  "constraints": ["is_supervisor property must be either 'Yes' or 'No'"]
}
"""

def natural_language_query_2_cypher(query):
    predefined_prompt = f"""You are an expert in Neo4j Cypher queries. Based on the following schema, generate a Cypher query to meet the user's requirements.

    Schema:
    {schema}

    User Request: {{query}}

    Cypher Query:

    You must only use the specified nodes and relationships given in the schema.

Guidelines:
- Output only a valid Cypher query using the above nodes and relationships.
- Do not introduce new nodes or relationships.
- No introductions or explanations.
- Use appropriate Cypher clauses and functions.
- Ensure the query captures the intent of the question.

Steps:
1. Identify main entities and relationships based on the provided structure.
2. Use only the specified Cypher clauses (MATCH, WHERE, RETURN, etc.).
3. Translate filtering conditions strictly using the defined nodes and relationships.
4. Ensure query correctness.

Output the Cypher query within <cypher_query> tags."""

    formatted_query = f"Convert to Cypher: {query}"

    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        system=predefined_prompt,
        messages=[
            {"role": "user", "content": formatted_query}
        ],
        max_tokens=500
    )
    
    content = response.content[0].text if response.content else ""
    tag_b = "<cypher_query>"
    tag_e = "</cypher_query>"
    start_index = content.find(tag_b)
    end_index = content.find(tag_e)

    if start_index != -1 and end_index != -1:
        cypher_query = content[start_index + len(tag_b):end_index].strip()
        return cypher_query
    else:
        return "Error: No content in response"

def execute_cypher(cypher_query):
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run(cypher_query)
                return list(result)
    except Exception as e:
        logging.error(f"Error executing Cypher query: {str(e)}")
        return None

def test_neo4j_connection():
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run("RETURN 1 AS test")
                return list(result)[0]["test"] == 1
    except Exception as e:
        logging.error(f"Neo4j connection test failed: {str(e)}")
        return False
def json_csv(json_data,output_file="report.csv"):
    try:
        df=pd.DataFrame(json_data)
        df.to_csv(output_file,index=False)
        logging.info(f"CSV file '{output_file}' has been created successfully.")
    except Exception as e:
        logging.error(f"Error creating CSV file: {str(e)}")

if __name__ == "__main__":
    if test_neo4j_connection():
        print("Neo4j connection successful!")
    else:
        print("Neo4j connection failed. Please check your credentials and connection details.")

