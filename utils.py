import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

def setState(key, value):
    st.session_state[key] = value  

@st.cache_data
def _color_red_or_green(val, set_point):
    color = 'red' if val > set_point else 'green'
    return f'background-color: {color}'

def normalizeDataframe(dataFrame):
    dfCopy = dataFrame.copy()
    dfCopy['Tanggal'] = dfCopy['Tanggal'].dt.date
    return dfCopy

def generateColumn(dataFrame):
    dataframe = dataFrame.copy()
    #Kolom solar (kWh)
    dataframe['Solar (kWh)']  = dataframe['Solar (L)'].apply(lambda x: x * 10.1)
    #Kolom CNG (KWH)
    dataframe['CNG (KWH)']    = dataframe['CNG (MMBTU)'].apply(lambda x: x * 293.1)
    #Kolom Total Energy
    dataframe['Total Energy'] = dataframe['Listrik (KWH)']  + dataframe['Solar (kWh)'] + dataframe['Tasma (KWH)'] + dataframe['CNG (KWH)'] 
    #Kolom ratio Energy (KWH/TON)
    dataframe['Energy (KWH/TON)'] = dataframe['Total Energy'] / (dataframe['FO'] + dataframe['Finish Goods'])
    #Kolom ratio Water (M3/TON)
    dataframe['Water (M3/TON)'] = dataframe['Water (M3)'] / (dataframe['FO'] + dataframe['Finish Goods'])

    return dataframe

def getColumnName(dataframe, first=None):
    column = dataframe.columns.to_list()
    if (first != None):
        result = [first]
    else:
        result = []
    for i in range(1,len(column)):
        result.append(column[i])
    return result

def getYear(dataframe):
    df = dataframe.copy()
    df = df.set_index('Tanggal')
    df['tahun'] = df.index.year

    listTahun = df['tahun'].unique()

    return listTahun

def convertMonth(n):
    n = int(n)
    if (n==1):
        return "Jan."
    elif (n==2):
        return "Feb."
    elif (n==3):
        return "Mar."
    elif (n==4):
        return "Apr."
    elif (n==5):
        return "May"
    elif (n==6):
        return "Jun."
    elif (n==7):
        return "Jul"
    elif (n==8):
        return "Aug."
    elif (n==9):
        return "Sept."
    elif (n==10):
        return "Oct."
    elif (n==11):
        return "Nov."
    elif (n==12):
        return "Dec."
    return "Invalid"

def decodeMonth(month):
    if (month=="Jan."):
        return 1
    elif (month=="Feb."):
        return 2
    elif (month=="Mar."):
        return 3
    elif (month=="Apr."):
        return 4
    elif (month=="May"):
        return 5
    elif (month=="Jun."):
        return 6
    elif (month=="Jul."):
        return 7
    elif (month=="Aug."):
        return 8
    elif (month=="Sept."):
        return 9
    elif (month=="Oct."):
        return 10
    elif (month=="Nov."):
        return 11
    elif (month=="Dec."):
        return 12
    return "Invalid"

@st.cache_data
def getMonthFromYear(dataframe, year):
    df = dataframe.copy()
    df = df.set_index('Tanggal')
    monthByYear = df.loc[f'{year}']
    monthByYear['month'] = monthByYear.index.month
    listMonth = monthByYear['month'].unique()

    display = []
    for item in listMonth:
        display.append(convertMonth(item))

    return display

@st.cache_data
def getDayFromMonth(dataframe, year, month):
    df = dataframe.copy()
    df = df.set_index('Tanggal')
    monthByYear = df.loc[f'{year}-{month}']
    return monthByYear.index.day

@st.cache_data
def filteredData(dataframe, year, month):
    df = dataframe.copy()
    df = df.set_index('Tanggal')
    df.index = np.array(pd.to_datetime(df.index))
    filteredDataframe = df.loc[f'{year}-{month}']

    return filteredDataframe    

@st.cache_data
def barChart(dataframe, y):
    df = dataframe.copy()
    # df = df.set_index('Tanggal')
    fig = px.bar(df, x=df.index, y=y, color_discrete_sequence=px.colors.qualitative.Pastel, barmode='group', text_auto=".h")
    fig.update_layout(
        xaxis_title='Date', 
        yaxis_title='Value',
        )
    fig.update_xaxes(
        dtick="86400000"
    )
    fig.update_traces(textfont_size=14, textposition='outside', hovertemplate="value=%{y}")
    
    return fig

@st.cache_data
def lineChart(dataframe, y):
    df = dataframe.copy()
    fig = px.line(df, x=df.index, y=y, color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
    fig.update_layout(
        xaxis_title='Date', 
        yaxis_title='Value')
    fig.update_xaxes(
        dtick="86400000"
    )
    fig.update_traces(textfont_size=14, textposition='top center')

    return fig

@st.cache_data
def sumByMonth(df: pd.DataFrame, year):
    df = df.copy()
    df = df.set_index('Tanggal')
    key = df.columns.to_list()
    data = df[key].resample("M").sum()

    data = data.loc[f'{year}']
    return data

@st.cache_data
def barChartMonthlyData(df: pd.DataFrame, y):
    df = df.copy()
    df = df.reset_index()
    df.columns.values[0] = "Tanggal"
    df['Tanggal'] = df['Tanggal'].apply(lambda x: x.strftime('%Y-%m'))
    df = df.set_index('Tanggal')

    fig = px.bar(df, x=df.index, y=y, color_discrete_sequence=px.colors.qualitative.Pastel, barmode='group', text_auto=True)
    fig.update_layout(
            xaxis_title="Month", 
            yaxis_title='Value')
    fig.update_xaxes(
        dtick="M1"
    )
    fig.update_traces(textfont_size=14)
    return fig
@st.cache_data
def lineChartMonthlyData(df: pd.DataFrame, y):
    df = df.copy()
    df = df.reset_index()
    df.columns.values[0] = "Tanggal"
    df['Tanggal'] = df['Tanggal'].apply(lambda x: x.strftime('%Y-%m'))
    df = df.set_index('Tanggal')

    fig = px.line(df, x=df.index, y=y, color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
    fig.update_layout(
        xaxis_title="Month", 
        yaxis_title='Value')
    fig.update_xaxes(
        dtick="M1"
    )
    fig.update_traces(textfont_size=14)
    return fig
def twoDigitDecimal(data):
    return np.ceil(data*100)/100
def multiple100(data):
    return data * 100
@st.cache_data
def percentageMonthly(dataframe: pd.DataFrame):
    df = dataframe.copy()
    monthPercentage = df.pct_change()
    monthPercentage = monthPercentage.apply(multiple100)
    monthPercentage = monthPercentage.reset_index()
    monthPercentage.columns.values[0] = "Tanggal"
    monthPercentage['Tanggal'] = monthPercentage['Tanggal'].apply(lambda x: x.strftime('%Y-%m'))
    monthPercentage = monthPercentage.set_index('Tanggal')
    monthPercentage = monthPercentage.apply(twoDigitDecimal)
    monthPercentage = monthPercentage.fillna(0)

    return monthPercentage
@st.cache_data
def sumOfYear(df: pd.DataFrame, y):
    df = df.copy()
    key = df.columns.tolist()
    df = df.set_index('Tanggal')
    df.index = np.array(pd.to_datetime(df.index))
    data = df[y].resample("Y").sum()
    yearData = data
    yearData = yearData.reset_index()
    yearData.columns.values[0] = "tanggal"
    yearData['tanggal'] = yearData['tanggal'].apply(lambda x: x.strftime('%Y'))
    yearData = yearData.set_index('tanggal')

    return yearData