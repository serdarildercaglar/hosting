import streamlit as st
from neo4j import GraphDatabase
import pandas as pd 
import numpy as np 
from PIL import Image

## Creating a Connection Class
class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        
        self.__url = url
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        
        try:
            self.__driver = GraphDatabase.driver(self.__url, auth=(self.__user, self.__pwd))
            
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response

url = 'bolt://3.238.153.201:7687'
pwd = "octobers-cures-drains"
user= 'neo4j'

conn = Neo4jConnection(uri=url, user=user , pwd=pwd)

# sidebar logo
logo = Image.open("/home/ubuntu/sparknlp_neo4j/nioyatech.jpg")
st.sidebar.image(logo)

# instant queries:
load_csv = """
              load csv with headers from 'https://raw.githubusercontent.com/serdarildercaglar/export_source/main/genia_2011_rel_result.csv' as row
              with row 
              where row is not null
              merge (n1:Ner {name: row.chunk1}) on create set n1.type = row.entity1
              merge (n2:Ner {name: row.chunk2}) on create set n2.type = row.entity2
              merge (n1)-[r:LINKS {relation: row.relation}]->(n2)
        """

delete_db = "Match (p) DETACH delete p"

# Database Operation
st.sidebar.title('Database Operation')
st.sidebar.write('Please select the operation you want to do from the menu')
options = ['Load data to Neo4j Database', 'Delete every things from database']
operation = st.sidebar.radio("Operations:", options, index=0)
result = st.sidebar.button("OK!")

if operation == options[0] and result:
    conn.query(load_csv)
    st.sidebar.write("Data Loaded!")
elif operation == options[1] and result:
    conn.query(delete_db)
    st.sidebar.write('All Node Deleted')

#sidebar 
st.sidebar.title("Explanation")
st.sidebar.write("""
In this study, we extracted protein and non-protein components
from a text document with biomedical content using NLP techniques.
Later, we extracted the relationships between the components with
the help of an artificial intelligence we developed.We converted
the results we obtained into an infographic to make the relationships 
between protein and other components more understandable.
Note: We only added the entities that are related to each other to the graph. 
""")

url = "https://github.com/serdarildercaglar/export_source/blob/main/genia-2011.txt"
st.sidebar.title("A part of text Used for Demo")
st.sidebar.write("""Lipopolysaccharide induction of tissue factor gene expression
in monocytic cells is mediated by binding of c-Rel/p65 heterodimers to a kappa
B-like site. Exposure of monocytic cells to bacterial lipopolysaccharide (LPS)
activates the NF-kappa B/Rel family of proteins and leads to the rapid
induction of inflammatory gene products, including tissue factor (TF).[click](%s)"""% url )
#st.write("Download whole text for read [link](%s)" % url)
#st.markdown("check out this [link](%s)" % url)

st.title("Relation Extraction  and Knowledge Graph ")
st.markdown("""
Queries are queried the neo4j sandbox. 
Results are displayed in tabular form as Streamlit does not support Knowledge Graph outputs. 
We have added neo4j outputs as images below the queries. 
You can also find the cypher query syntax in the results. 
""")



# read csv
df = pd.read_csv('https://raw.githubusercontent.com/serdarildercaglar/export_source/main/genia_2011_rel_result.csv')
entity1 = list(df.entity1.unique())
entity2 = list(df.entity2.unique())
all_entities = set(entity1+entity2)
relation = list(df.relation.unique())
relation.insert(0,'All Relationships')
type = list(df.entity1.unique())

container0 = st.container()
with container0:
    st.markdown(
			"<h1 style='font-size:300%;\
						font-family:;\
						text-align:center;\
						background-color:#4FE5FF;\
						color:;'>Instant Cypher Queries\
			</h1>", unsafe_allow_html=True
			)
    selection = ["All Nodes and Their Relations with eachother",
               "Relation from Protein to non Protein",
               "relation from non Protein to Protein",
               "Protein List",
               "non_Protein List"
                ]
    queries = [
                "MATCH (n:Protein)-[r:LINKS]-(m:non_Protein) RETURN n as Chunk1,r.relation as Relation ,m as Chunk2",
                "MATCH (n:Protein)-[r:LINKS]-(m:non_Protein) RETURN n.name as Protein,r.relation as Relation ,m.name as non_Protein",

                "match (n1:Protein)-[r:LINKS]->(n2:non_Protein) return n1 as Protein, r.relation as Relation, n2 as non_Protein",
                "match (n1:Protein)-[r:LINKS]->(n2:non_Protein) return n1.name as Protein, r.relation as Relation, n2.name as non_Protein",

                "match (n1:Protein)< -[r:LINKS]-(n2:non_Protein)return n2 as Non_Protein, r.relation, n1 as Protein",
                "match (n1:Protein)< -[r:LINKS]-(n2:non_Protein)return n2.name as Non_Protein, r.relation, n1.name as Protein",

                "match (pro:Protein) return pro as Proteins",
                "match (pro:Protein) return pro.name as Proteins",
                
                "match (pro:non_Protein) return pro as non_Proteins",
                "match (pro:non_Protein) return pro.name as non_Proteins"
            ]
    
    instant = st.selectbox(label = 'Select a query to run from list',options = selection)

    b = st.button(label = 'Run Selection')
    if b:

        if instant == selection[0]:
            st.markdown(f'<b style="color:blue">Cypher query:</b><br> <p style="background-color:#F0D8D3">**{queries[0]}**</p>',unsafe_allow_html=True)
            image = Image.open("/home/ubuntu/genia_2011/graph1.png")
            st.image(image)
            df = pd.DataFrame([dict(i) for i in conn.query(queries[1])])
            st.table(df)
            # image
            

        elif instant == selection[1]:
            st.markdown(f'<b style="color:blue">Cypher query:</b><br> <p style="background-color:#F0D8D3">**{queries[2]}**</p>',unsafe_allow_html=True)
            image = Image.open("/home/ubuntu/genia_2011/graph2.png")
            st.image(image)
            df = pd.DataFrame([dict(i) for i in conn.query(queries[3])])
            st.table(df)

        elif instant == selection[2]:
            st.markdown(f'<b style="color:blue">Cypher query:</b><br> <p style="background-color:#F0D8D3">**{queries[4]}**</p>',unsafe_allow_html=True)
            image = Image.open("/home/ubuntu/genia_2011/graph3.png")
            st.image(image)
            df = pd.DataFrame([dict(i) for i in conn.query(queries[5])])
            st.table(df)

        elif instant == selection[3]:
            st.markdown(f'<b style="color:blue">Cypher query:</b><br> <p style="background-color:#F0D8D3">**{queries[6]}**</p>',unsafe_allow_html=True)
            image = Image.open("/home/ubuntu/genia_2011/graph4.png")
            st.image(image)
            df = pd.DataFrame([dict(i) for i in conn.query(queries[7])])
            st.table(df)
        elif instant == selection[4]:
            st.markdown(f'<b style="color:blue">Cypher query:</b><br> <p style="background-color:#F0D8D3">**{queries[8]}**</p>',unsafe_allow_html=True)
            image = Image.open("/home/ubuntu/genia_2011/graph5.png")
            st.image(image)
            df = pd.DataFrame([dict(i) for i in conn.query(queries[9])])
            st.table(df)




container1 = st.container()
with container1:
    st.markdown(
			"<h1 style='font-size:300%;\
						font-family:;\
						text-align:center;\
						background-color:;\
						color:;'>Relationships by Entity Types\
			</h1>", unsafe_allow_html=True
			)

    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Entity 1\
			</h1>", unsafe_allow_html=True
			)
        s1 = st.selectbox(label = 'Please select entity 1',options = type)
    with col2:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Relation\
			</h1>", unsafe_allow_html=True
			)
        s2 = st.selectbox(label = 'Please Select Relationships',options = relation)
    with col3:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Entity 2\
			</h1>", unsafe_allow_html=True
			)
        s3 = st.selectbox(label = 'Please select entity 2',options = type)
    # query generation
    condition1 = s1
    if s2 == 'All Relationships':
        condition2 = f'r:LINKS'
    else:
        condition2 = 'r:LINKS{'+f"relation:'{s2}'"+'}'
    condition3 = s3
    container1_query = f"""
                            match (n1:{condition1} )-[{condition2}]->(n2:{condition3})
                            return n1.name, r.relation,n2.name
                        """
    st.markdown(f'<b style="color:blue">Your cypher query is generated below:</b><br> <p style="background-color:#F0D8D3">**{container1_query}**</p>',unsafe_allow_html=True)
    button = st.button(label = 'Run Query')
    if button:
        df = pd.DataFrame([dict(i) for i in conn.query(container1_query)])
        st.table(df)
###############################################################################################################################################################################
                                                #Aşağıdaki kısım test ediliyor
###############################################################################################################################################################################

container2 = st.container()
with container2:
    st.markdown(
			"<h1 style='font-size:300%;\
						font-family:;\
						text-align:center;\
						background-color:;\
						color:;'>Relationships by Entity Types\
			</h1>", unsafe_allow_html=True
			)

    st.markdown("")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Entity 1\
			</h1>", unsafe_allow_html=True
			)
        s1 = st.selectbox(label = 'Please select entity 1',options = type)
    with col2:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Relation\
			</h1>", unsafe_allow_html=True
			)
        s2 = st.selectbox(label = 'Please Select Relationships',options = relation)
    with col3:
        st.markdown(
			"<h1 style='font-size:200%;\
						font-family:;\
						text-align:center;\
						background-color:#867DFF;\
						color:;'>Entity 2\
			</h1>", unsafe_allow_html=True
			)
        s3 = st.selectbox(label = 'Please select entity 2',options = type)
    # query generation
    condition1 = s1
    if s2 == 'All Relationships':
        condition2 = f'r:LINKS'
    else:
        condition2 = 'r:LINKS{'+f"relation:'{s2}'"+'}'
    condition3 = s3
    container1_query = f"""
                            match (n1:{condition1} )-[{condition2}]->(n2:{condition3})
                            return n1.name, r.relation,n2.name
                        """
    st.markdown(f'<b style="color:blue">Your cypher query is generated below:</b><br> <p style="background-color:#F0D8D3">**{container1_query}**</p>',unsafe_allow_html=True)
    button = st.button(label = 'Run Query')
    if button:
        df = pd.DataFrame([dict(i) for i in conn.query(container1_query)])
        st.table(df)