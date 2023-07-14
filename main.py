# importing section
import streamlit  as st
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
from spare_parts import ratios,get_company_list,income_statement,balance_sheet
from recommend_stock import *
import plotly.graph_objects as go
import plotly.express as px


# setting the user interface
st.set_page_config(page_title="Stock Analysis",page_icon="📈",layout="wide")
# setting the color of the user interface

@st.cache_data
def load_data_1():
    df = pd.read_csv("tickertape.csv")
    return df

@st.cache_data
def load_data():
    df = pd.read_csv("selected_companies.csv")
    df['company'] = df['company'].str.lower()
    return df

with st.sidebar: #type: ignore
    #st.title("Bike Rental Prediction")
    button_1 = st.radio("options", ['Fundamental Analysis', "Stock Recommendation","Financials","Stock Recommendation intraday"])

    
if(button_1):
        
        if(button_1 == "Fundamental Analysis"):
            st.title("Fundamental Analysis")
            st.subheader("<--- More options[scroll the sidebar]")
            # providing search option
            st.subheader("Search for a stock")
            data = load_data()
            try:
                ticker_data = st.selectbox("Select a stock",data['company'])
                dataframe_generated = ratios(ticker_data)
                st.write(dataframe_generated)
                # visulization of the data
                st.subheader("Visualization of the data")
                ratio_selected = st.selectbox("Select a ratio",dataframe_generated.columns)
                st.line_chart(dataframe_generated[ratio_selected]) #type: ignore
                # multiple visulization
    

            except:
                pass

            # working with multiple vislization
            st.subheader("Multiple visulization")
            try:
                #dataframe_generated
                tickers = st.multiselect("Select the stocks",dataframe_generated.columns) #type:ignore
                if(len(tickers) > 0):
                    st.line_chart(dataframe_generated[tickers]) #type: ignore
            except:
                 pass
        

        

    
        elif(button_1 == "Stock Recommendation"):
            st.title("Stock Recommendation")
            # adding slider for selecting number of companies
            st.subheader("Select the number of companies")
            number_of_companies = st.slider("Number of companies",1,2012)
            button_1 = st.button("Run")
            # main function
            if(button_1):
                    get_company_list_1 = get_company_list()
                    #data_1 = [i[1] for i in get_company_list_1]
                    dict_1 = {}
                    for i in get_company_list_1[0:number_of_companies]:
                        try:
                            target = bollinger_band(i[1 ])
                            target.run_test()
                            dict_1[i[0]] = target.call
                        except:
                             pass
                    # creating a dataframe

                    df = pd.DataFrame(dict_1.items(),columns=['company','call'])
                    df = df[df['call'] != ""]
                    # creating a pie chart
                    st.subheader("final call")
                    st.write(df)
        elif(button_1 == "Stock Recommendation intraday"):

            st.title("Stock Recommendation")
            # adding slider for selecting number of companies
            st.subheader("Select the number of companies")
            number_of_companies = st.slider("Number of companies",1,2012)
            button_1 = st.button("Run")
            # main function
            if(button_1):
                 st.write("processing")
                 result = process_company_list(get_company_list(),number_of_companies)
                 
                 for i, j in zip(result[0], result[1]):
                      st.write(i)
                      print(j)
                      with st.expander("stock chart",False):
                        for k in j:
                            fig_close = go.Figure(data=go.Scatter(x=k.index, y=k['Close'], mode='lines'))
                            fig_close.update_layout(title="Close Data", xaxis_title="Date", yaxis_title="Close Value")
                            fig_macd = go.Figure()
                            fig_macd.add_trace(go.Scatter(x=k.index, y=k['macd'].tail(60), mode='lines', name='MACD',line=dict(color='red')))
                            fig_macd.add_trace(go.Scatter(x=k.index, y=k['macd_signal'].tail(60), mode='lines', name='MACD Signal',line=dict(color='yellow')))
                            fig_macd.update_layout(title="MACD Data", xaxis_title="Date", yaxis_title="MACD Value")

                            # alfa=======================
                            fig_r2 = go.Figure()
                            fig_r2.add_trace(go.Scatter(x=k.index, y=k['r2'].tail(60), mode='lines', name='r2_score',line=dict(color='red')))
                            fig_r2.update_layout(title="r2 data", xaxis_title="Date", yaxis_title="r2_data")

                            # seperation
                            col_1 , col_2 = st.columns(2)
                            st.plotly_chart(fig_close)

                            with col_1:
                                st.plotly_chart(fig_macd)
                            with col_2:

                                st.plotly_chart(fig_r2)

              

                 


        else:

            st.title("Financials")
            st.write("EPS and DPS in ₹. Other numbers except Payout Ratio in ₹ cr, Shares outstanding numbers in cr. Other numbers in ₹ cr")
            st.subheader("Income Statement")
            data_1 = load_data_1()
            select_stock = st.selectbox("Select a stock",data_1['companies_list'])
            if(len(select_stock) > 0): #type: ignore
                try:

                    dataframe_1 = income_statement(select_stock)
                    
                    dataframe_1 = dataframe_1.T
                    st.subheader("Income Statement")
                    st.write(dataframe_1.T)
                    print("processing balance sheet")
                    dataframe_2 = balance_sheet(select_stock)
                    dataframe_2.replace("—", None, inplace=True)
                    dataframe_2 = dataframe_2.T
                    st.subheader("Balance Sheet")
                    st.write(dataframe_2.T)
                    # visulization of the data
                    st.subheader("Visulization")
                    button_2 = st.selectbox("Select a financial statements",["","Income Statement","Balance Sheet"])
                    if(button_2 == "Income Statement"):
                         st.subheader("Visualization of the data[Income Statement]")
                         ratio_selected = st.multiselect("Select a ratio",dataframe_1.columns)
                         st.line_chart(dataframe_1[ratio_selected]) #type: ignore
                    elif(button_2 == "Balance Sheet"):
                        st.subheader("Visualization of the data[Balance Sheet]")
                        ratio_selected = st.multiselect("Select a ratio",dataframe_2.columns)
                        st.line_chart(dataframe_2[ratio_selected]) #type: ignore
                    
                except Exception as e:
                     
                     st.write(str(e))
                


        

