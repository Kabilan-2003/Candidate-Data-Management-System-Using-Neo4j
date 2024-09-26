from django.shortcuts import render
import pandas as pd
from neo4j import GraphDatabase


def get_data(request):
    if request.method=="POST":
        name = request.POST.get('name')
        college = request.POST.get('college')
        yop = request.POST.get('yop')
        skills = request.POST.get('skills')
        email = request.POST.get('email')
        degree = request.POST.get('degree')

        data={"Name":name,"Email":email,"College":college,"Year of Passout":yop,"Skills":skills,"Degree":degree}
        save_neo(data)
    return render(request,"home.html")

def save_neo(data):
    graphDB_Driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Kabilan2003"))
    with graphDB_Driver.session() as session:
        session.run("""
        MERGE (p:Candidate {email: $email})
        ON CREATE SET p.name = $name, p.college = $college, p.year_of_passout = $yop, p.degree = $degree, p.skills = $skills
        
        MERGE (c:College {name: $college_name})
        MERGE (p)-[:STUDIED_AT]->(c)
        
        MERGE (d:Degree {name: $degree_name})
        MERGE (p)-[:HAS_DEGREE]->(d)
        
        MERGE (y:Year {name: $yop})
        MERGE (p)-[:PASSED_OUT]->(y)
        
        FOREACH (skill IN $skills |
            MERGE (s:Skill {name: skill})
            MERGE (p)-[:HAS_SKILL]->(s)
        )
        """,
        name=data['Name'],
        email=data['Email'],
        college=data['College'],
        yop=int(data['Year of Passout']),
        degree=data['Degree'],
        college_name=data['College'],
        degree_name=data['Degree'],
        skills=data['Skills'].split(',')
        )

def show_db(request):
    graphDB_Driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Kabilan2003"))
    with graphDB_Driver.session() as session:
        result = session.run("MATCH (p:Candidate) RETURN p.name AS Name, p.email AS Email, p.college AS College, p.year_of_passout AS Year_of_Passout, p.degree AS Degree")
        df = pd.DataFrame([record.values() for record in result], columns=result.keys())
        df.dropna(inplace=True)
        df['Year_of_Passout'] = df['Year_of_Passout'].astype(int)
    return render(request, "show_data.html", {"df": df.to_html()})
