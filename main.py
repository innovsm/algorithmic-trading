# importing section
import streamlit  as st
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
from spare_parts import ratios,get_company_list
from recommend_stock import bollinger_band

# setting the user interface
st.set_page_config(page_title="Stock Analysis",page_icon="📈",layout="wide")
# setting the color of the user interface




@st.cache_data
def load_data():
    df = pd.read_csv("selected_companies.csv")
    df['company'] = df['company'].str.lower()
    return df

with st.sidebar:
    #st.title("Bike Rental Prediction")
    button_1 = st.radio("page", ['Fundamental Analysis', "Stock Recommendation"])
    
if(button_1):
        
        if(button_1 == "Fundamental Analysis"):
            st.title("Fundamental Analysis")
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
        

        

    
        else:
            st.title("Stock Recommendation")
            # adding slider for selecting number of companies
            st.subheader("Select the number of companies")
            number_of_companies = st.slider("Number of companies",1,2012)
            button_1 = st.button("Run")
            # main function
            if(button_1):
                    get_company_list_1 = get_company_list()
                    data_1 = [i[1] for i in get_company_list_1]
                    dict_1 = {}
                    for i in data_1[0:number_of_companies]:
                        try:
                            target = bollinger_band(i)
                            target.run_test()
                            dict_1[i] = target.call
                        except:
                             pass
                    # creating a dataframe

                    df = pd.DataFrame(dict_1.items(),columns=['company','call'])
                    df = df[df['call'] != ""] #type: ignore
                    # creating a pie chart
                    st.subheader("final call")
                    st.write(df)
                        
        

