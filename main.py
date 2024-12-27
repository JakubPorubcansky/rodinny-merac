import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
import streamlit as st

SOURCE_FILE = "rodinny_merac.csv"
FIRST_DATA_ROW_INDEX = 0
FIRST_DATA_COLUMN_INDEX = 5

class PersonDataRecord:
    def __init__(self, age, height):
        self.age = age
        self.height = height

class Person:
    def __init__(self, first_name, last_name, sex, birthday, predecessor):
        self.first_name = first_name
        self.last_name = last_name
        self.sex = sex
        self.birthday = datetime.strptime(birthday, "%d.%m.%Y")
        self.predecessor = predecessor
        self.data = []

class Figure:
    def __init__(self, title):
        self.title = title
        self.layout = go.Figure()
        self.layout.update_layout(
            title=self.title,
            xaxis_title="Vek",
            yaxis_title="Výška",
            legend_title="Meno",
            yaxis=dict(autorange=True),
            height=600,
            width=1000
        )

def load_data():
    return pd.read_csv(SOURCE_FILE, sep=",", header=0)

def process_data(df):
    people_data = []

    for i in range(FIRST_DATA_ROW_INDEX, len(df)):
        if df.iloc[i, :FIRST_DATA_COLUMN_INDEX].isnull().any():
            continue

        last_name = str(df.iloc[i, 0])
        first_name = str(df.iloc[i, 1])
        sex = str(df.iloc[i, 2])
        birthday = df.iloc[i, 3]
        predecessor = str(df.iloc[i, 4])
        person = Person(first_name, last_name, sex, birthday, predecessor)
        people_data.append(person)

        for j in range(FIRST_DATA_COLUMN_INDEX, len(df.columns)):
            if pd.isnull(df.iloc[i, j]):
                continue
            date_of_measurement = datetime.strptime(df.columns[j], "%d.%m.%Y")
            age_in_years = round((date_of_measurement - person.birthday).days / 365.25, 2)
            height = float(df.iloc[i, j])
            person.data.append(PersonDataRecord(age_in_years, height))
    
    return people_data

def prepare_figures_to_plot(people_data):
    figures = {
        "všetci": Figure("Všetci"),
        "žena": Figure("Ženy"),
        "muž": Figure("Muži"),
        "Elena": Figure("Potomkovia - Elena Vanochová"),
        "Štefan": Figure("Potomkovia - Štefan Porubčanský"),
        "Jozef": Figure("Potomkovia - Jozef Porubčanský"),
        "Miro": Figure("Potomkovia - Miro Porubčanský"),
        "Mariena": Figure("Potomkovia - Mariena Porubčanská"),
    }

    for person in people_data:
        person_data = [(record.age, record.height) for record in person.data]
        person_data.sort(key=lambda x: x[0])
        years = [x[0] for x in person_data]
        heights = [x[1] for x in person_data]
        name = f"{person.first_name} {person.last_name}"

        for key in ["všetci", person.sex, person.predecessor]:
            figures[key].layout.add_trace(
                go.Scatter(x=years, y=heights, mode="lines+markers",
                           name=name, line=dict(width=2), marker=dict(size=8))
            )

    return figures

def render(df, figures):
    st.set_page_config(layout="wide")
    st.title("Rodinný merač 🧍↕")
    for fig in figures.values():
        st.plotly_chart(fig.layout)

    df = df.fillna("")

    st.write("Dáta:")
    st.dataframe(df, hide_index=True, height=600)

def main():
    tabular_data = load_data()
    people_data = process_data(tabular_data)
    figures = prepare_figures_to_plot(people_data)
    render(tabular_data, figures)

if __name__ == "__main__":
    main()
