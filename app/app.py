import streamlit as st
import pandas as pd
import altair as alt
import os


file_dict = {}


@st.cache
def get_data():
    load_files('./data')
    forward_fill()
    melt()
    return merge()


def load_files(path):
    for file in os.listdir(path):
        df = pd.read_csv(path + '/' + file, index_col='country')
        key = file.split('.')[0]
        file_dict[key] = df


def forward_fill():
    for key, df in file_dict.items():
        filled_df = df.ffill(axis=1)
        file_dict[key] = filled_df


def melt():
    for key, df in file_dict.items():
        melted_df = pd.melt(df.reset_index(), id_vars='country', value_vars=df.columns,
                            var_name='year', value_name=key)
        melted_df['year'] = melted_df['year'].astype(int)
        file_dict[key] = melted_df


def merge():
    merged_df = None
    for key, df in file_dict.items():
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, 'inner', ['country', 'year'])
    return merged_df


st.title('Gapminder Data')
st.write('Looking at Population, Life Expectancy and GNI per Capita')

data = get_data()
unique_countries = data['country'].unique()

st.sidebar.markdown('## Controls')
st.sidebar.markdown('You can change the following values to adjust the chart.')

countries = st.sidebar.multiselect(
    "Choose from the following countries: ", list(sorted(unique_countries)), ["Germany"]
)

year = st.sidebar.slider(
    'Select a year: ', int(data['year'].min()), int(data['year'].max()), 2005, step=1
)

if not countries:
    st.error("Please select at least one country.")
else:
    filtered_by_year = data[data['year'] == year]
    filtered_by_country = filtered_by_year[filtered_by_year['country'].isin(countries)]

    chart = (
        alt.Chart(filtered_by_country).mark_circle().encode(
            alt.X('gni_per_capita:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title='GNI per Capita')),
            alt.Y('life_expectancy:Q', scale=alt.Scale(zero=False), axis=alt.Axis(title='Life Expectancy')),
            size='population:Q', color='country:N'
        )
    )
    st.altair_chart(chart, use_container_width=True)

