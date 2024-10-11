import streamlit as st
from kg_llm_st_v1 import natural_language_query_2_cypher, execute_cypher, test_neo4j_connection
import pandas as pd
import json

# Streamlit UI
st.title("Query Converter")
st.write("Enter an organisational query:")
query = st.text_input("Enter your natural language query:")

#session
if 'cypher_query' not in st.session_state:
    st.session_state.cypher_query = None
if 'result' not in st.session_state:
    st.session_state.result = None
def handle_query():
    if query:
        #connection check
        if not test_neo4j_connection():
            st.error("Unable to connect to Neo4j database. Please check your connection details and try again.")
            return

        #cypher query
        st.session_state.cypher_query = natural_language_query_2_cypher(query)
        st.write("Backend Cypher Query: ")
        st.code(st.session_state.cypher_query, language="cypher")
        
        if st.session_state.cypher_query:
            st.write("Executing cypher query...")
            st.session_state.result = execute_cypher(st.session_state.cypher_query)
            
            if st.session_state.result is not None:
                st.write("Query Results (JSON):")
                st.session_state.result
            else:
                st.write("No records found. Please contact your administrator")
        else:
            st.error("An error occurred while executing the query. Please check the logs for more information.")
    else:
        st.write("Invalid input")

st.warning("Please enter a query before clicking the button")
#get data
if st.button("Get Data"):
    handle_query()

#download
if st.session_state.cypher_query and st.session_state.result is not None:
    csv_output_file = "report.csv"
    df = pd.DataFrame(st.session_state.result)
    df.to_csv(csv_output_file, index=False)

    with open(csv_output_file, "rb") as file:
        st.download_button(
            label="Export to CSV",
            data=file,
            file_name=csv_output_file,
            mime="text/csv"
        )

