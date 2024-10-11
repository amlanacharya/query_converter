# Python Neo4j Knowledge Graph
Basic knowledge graph using Neo4j and LLM of choice

## Requirements
- Python 3.10+
- Neo4j 5.11+
- LLM of choice (OpenAI, Azure, Groq, Anthropic etc.) with API keys

## Usage
- Install dependencies `pip install -r requirements.txt`
- Run `faker_emp.py` to generate fake data
- Run `python emp_kg.py` to create the graph
- Optional step: `python kg_llm_st_v1.py` to check connection to Neo4j and LLM.
- Run `streamlit run streamlit_app.py` to use the Streamlit interface
- Visit https://queryconverter.streamlit.app to use the query converter
## Local usage
-Follow same steps as above till step 3
-Run `python kg_llm_st_v1.py` to check connection to Neo4j and LLM
-Run `streamlit run llm_neo4j_str.py` to use the Streamlit interface locally.



