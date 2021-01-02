import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px


def main():

# Set configs
    st.set_page_config(
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="expanded",  # Can be "auto", "expanded", "collapsed"
	page_title='SCPI',  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
    )
    

# Load Data
    info, prix, distri = scrap(275)
    prix = clean_prix(prix)
    distri = clean_distri(distri)
    #df = pd.merge(prix,distri,  how='inner', on = ['SCPI', 'Année'])
    info = clean_info(info)

# Set Sidebar
    st.sidebar.title('Navigation onglet')
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Ranking", "General"])

# Page 1
    if page == "Homepage":

        # Set Sidebar
        st.sidebar.title('Generals filters')
        sel_capital = st.sidebar.multiselect('Select Capital', sorted(info['Capital'].unique()))
        slider_distri = st.sidebar.slider('Taux de distribution', float(info['Tx distrib'].min()), float(info['Tx distrib'].max()), (float(info['Tx distrib'].min()), float(info['Tx distrib'].max())))
        slider_occup = st.sidebar.slider("Taux d'occupation", float(info['Tx occup'].min()), float(info['Tx occup'].max()), (float(info['Tx occup'].min()), float(info['Tx occup'].max())))
        slider_crea = st.sidebar.slider('Année de Création', int(info['Date de création'].min()), int(info['Date de création'].max()), (int(info['Date de création'].min()), int(info['Date de création'].max())))
        # Configure generals filters
        df_capital = multi_filter(info, sel_capital, 'Capital')
        df_distri = info[info['Tx distrib'].between(slider_distri[0],slider_distri[1])]
        df_occup = info[info['Tx occup'].between(slider_occup[0],slider_occup[1])]
        df_crea = info[info['Date de création'].between(slider_crea[0],slider_crea[1])]

        info_select = info[info.isin(df_capital) & info.isin(df_distri) & info.isin(df_occup) & info.isin(df_crea)].dropna()

        st.dataframe(info_select, width=2024, height=768)
        #st.dataframe(prix)
        #st.dataframe(distri)
        #st.dataframe(data)
	
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
    info = {'SCPI': [],'Capital': [], 'Date de création': [], 'Tx distrib': [], 'Prix souscri': [], 'Nb Associés': [], 'Nb Parts': [], 'Tx occup': [], 'Frais Souscription': []}
    lis_prix = []
    lis_distri = []

    for i in range(nb_sites):
        url = 'https://www.primaliance.com/scpi-de-rendement/' + str(i) +'-scpi-immorente'
        html = requests.get(url).content

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').string

        if title != '404 Page Not Found' and title[:4] != 'OPCI':
            
            year = all_element('span','bl left clear ml1 txtgrey txt11 txtitalic', url)[0][-5:-1]
            if '/' not in year:
                if int(year)>2019:

                    # Info
                    chiffre = all_element('span','bl left clear txtgrey txt36 txtlight', url)
                    info['Tx distrib'].append(chiffre[0][1:-1])
                    info['Prix souscri'].append(chiffre[1][1:-1])

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

    info = pd.DataFrame(info).dropna()
    prix = pd.concat(lis_prix)[['Année', 'Prix acquéreur *', 'Dividende par part', 'Résultat Courant','RAN / part', 'SCPI']].dropna()
    distri = pd.concat(lis_distri)[['Année', 'Taux de distribution**', 'Variation du prix ***', 'SCPI']].dropna()
    return info, prix, distri

def clean_info(info):
    clean_info = info.copy()
    clean_info = clean_info[clean_info['Tx distrib'] != 'NC'].reset_index().drop('index', axis = 1)
    for i in ['Tx distrib', 'Prix souscri','Nb Associés', 'Nb Parts', 'Tx occup', 'Frais Souscription']:
        clean_info[i] = clean_info[i].str.replace(r'-', '0')
        clean_info[i] = clean_info[i].str.replace(r'%', '0')
        clean_info[i] = clean_info[i].str.replace(' ', '')
        clean_info[i] = clean_info[i].str.replace(',', '.').astype(float).round(2)
    clean_info['Date de création'] = clean_info['Date de création'].str.replace(r'-', '0')
    clean_info['Date de création'] = clean_info['Date de création'].str[-4:].astype(int)
    
    return clean_info

def clean_prix(prix):
    clean_prix = prix[['SCPI','Année','Prix acquéreur *','Dividende par part','Résultat Courant','RAN / part']]
    clean_prix = clean_prix.reset_index().drop('index', axis = 1)

    for i in ['Prix acquéreur *', 'Dividende par part', 'Résultat Courant', 'RAN / part']:
        clean_prix[i] = clean_prix[i].str.replace(r'€', '')
        clean_prix[i] = clean_prix[i].str.replace(' ', '')
        clean_prix[i] = clean_prix[i].str.replace(',', '.').astype(float)
    return clean_prix

def clean_distri(distri):
    clean_distri = distri[['SCPI','Année','Taux de distribution**','Variation du prix ***']]
    clean_distri = clean_distri.reset_index().drop('index', axis = 1)
    for i in ['Taux de distribution**', 'Variation du prix ***']:
        clean_distri[i] = clean_distri[i].str.replace(r'%', '')
        clean_distri[i] = clean_distri[i].str.replace(' ', '')
        clean_distri[i] = clean_distri[i].str.replace(',', '.').astype(float)
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
