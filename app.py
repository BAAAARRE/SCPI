import streamlit as st
import requests
import pandas as pd
import json
from BeautifulSoup4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px


def main():

# Set configs
    st.set_page_config(
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
	page_title='SCPI',  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
    )
    

# Load Data
    info, prix, distri = scrap(275)
    prix = clean_prix(prix)
    distri = clean_distri(distri)

# Set Sidebar
    st.sidebar.title('Navigation onglet')
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Ranking", "General"])

# Configure generals filters

    
# Page 1
    if page == "Homepage":
        st.dataframe(info)
        st.dataframe(prix)
        st.dataframe(distri)
	
# Bottom page
    st.write("\n") 
    st.write("\n")
    st.info("""By : Ligue des Datas [Instagram](https://www.instagram.com/ligueddatas/) / [Twitter](https://twitter.com/ligueddatas) | Data source : [Sport Reference Data](https://www.sports-reference.com/)""")


# Functions

def all_element(typ, detail, uri):
    html = requests.get(uri).content
    soup = BeautifulSoup(html, 'html.parser')
    all_ele = []
    for i in soup.find_all(typ, {'class' : detail}):
        all_ele.append(i.string)
    return all_ele

@st.cache
def scrap(nb_sites):
    info = {'SCPI': [],'Capital': [], 'Date de création': [], 'Nb Associés': [], 'Nb Parts': [], 'Tx occup': [], 'Frais Souscription': []}
    lis_prix = []
    lis_distri = []

    for i in range(nb_sites):
        url = 'https://www.primaliance.com/scpi-de-rendement/' + str(i) +'-scpi-immorente'
        html = requests.get(url).content

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').string

        if title != '404 Page Not Found' and title[:4] != 'OPCI':

            # Info
            scpi = title[5:]
            info['SCPI'].append(scpi)
            info_gen = all_element('span','w40 txtlight txtleft', url)
            info['Capital'].append(info_gen[2])
            info['Date de création'].append(info_gen[3])
            info['Nb Associés'].append(info_gen[6])
            info['Nb Parts'].append(info_gen[7])

            info_det = all_element('span','w30 txtlight txtright', url)
            info['Tx occup'].append(info_det[4])

            info_frais = all_element('span','w40 txtlight txtright', url)
            info['Frais Souscription'].append(info_frais[0])

            # Tables
            df_list = pd.read_html(html)

            # Prix
            df_prix = df_list[1]
            df_prix['SCPI'] = scpi
            lis_prix.append(df_prix)

            # Distribution
            df_distri = df_list[3]
            df_distri['SCPI'] = scpi
            lis_distri.append(df_distri)   

    info = pd.DataFrame(info)
    prix = pd.concat(lis_prix)
    distri = pd.concat(lis_distri)
    return info, prix, distri

def clean_prix(prix):
    clean_prix = prix[['SCPI','Année','Prix acquéreur *','Dividende par part','Résultat Courant','RAN / part']]
    clean_prix = clean_prix.reset_index().drop('index', axis = 1)

    for i in ['Prix acquéreur *', 'Dividende par part', 'Résultat Courant', 'RAN / part']:
        clean_prix[i] = clean_prix[i].str.replace(r'€', '')
        clean_prix[i] = clean_prix[i].str.replace(' ', '')
        clean_prix[i] = clean_prix[i].str.replace(',', '.').astype(float)
    clean_prix = clean_prix.fillna(0)
    return clean_prix

def clean_distri(distri):
    clean_distri = distri[['SCPI','Année','Taux de distribution**','Variation du prix ***']]
    clean_distri = clean_distri.reset_index().drop('index', axis = 1)
    for i in ['Taux de distribution**', 'Variation du prix ***']:
        clean_distri[i] = clean_distri[i].str.replace(r'%', '')
        clean_distri[i] = clean_distri[i].str.replace(' ', '')
        clean_distri[i] = clean_distri[i].str.replace(',', '.').astype(float)
    clean_distri = clean_distri.fillna(0)
    return clean_distri

def multi_filter(df, sel, var):
    if len(sel) == 0:
        df_sel = df
    elif len(sel) != 0:
        df_sel = df[df[var].isin(sel)]
    return df_sel


    st.write(fig)


if __name__ == "__main__":
    main()
