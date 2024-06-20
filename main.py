import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import base64

# Set up the dashboard configuration
st.set_page_config(
    page_title="Bank Data Dashboard",
    page_icon="🏦",
    layout="wide",
)

# Define the data loading function with caching
def get_data() -> pd.DataFrame:
    return pd.read_csv("Schema.csv")

df = get_data()

# Preprocess the data
df["Date"] = pd.to_datetime(df["Date"]).dt.date
df["CD"]=df["CD"]*100
new_df = df.groupby(['Year', 'Month', 'Week']).agg({
    'DLCY': 'sum', 'DFCY': 'sum', 'DTOTAL': 'sum',
    'LLCY': 'sum', 'LFCY': 'sum', 'CD': 'mean',
    'type': 'first', 'Date': 'first', 'Ndate': 'first', 'FY': 'first'
}).reset_index()

new_df['Description'] = new_df['Year'].astype(str) + ' ' + new_df['Month'] + ' ' + new_df['Week']
new_df['DTOTAL'] = new_df['DLCY'] + new_df['DFCY']
new_df['LTOTAL'] = new_df['LLCY'] + new_df['LFCY']

summed_columns = ['DLCY', 'DFCY', 'DTOTAL', 'LLCY', 'LFCY', 'LTOTAL']
new_df[summed_columns] = new_df[summed_columns].map('{:.2f}'.format)
new_df = new_df.sort_values(by="Date").reset_index(drop=True)
numeric_columns = ['DLCY', 'DFCY', 'DTOTAL', 'LLCY', 'LFCY', 'LTOTAL']
new_df[numeric_columns] = new_df[numeric_columns].astype(float)

mask_month=new_df["type"]=="End"
month_df=new_df[mask_month]

mask_week=new_df["type"]=="Week"
week_df=new_df[mask_week]


# Add navigation sidebar
st.sidebar.title("Choose an option")
page = st.sidebar.radio("Go to", ["Home Page", "Search DL Data", "Weekly DL Data", "Monthly DL Data","BankWise DL Data"])

if page == "Home Page":
    st.title("Deposit and Lending of Commercial Banks")
    st.header(f"As of {new_df['Description'].iloc[-1]} ({new_df['Ndate'].iloc[-1]})")
    st.write("Amounts in Rs (Billions)")
    
    # Convert all numeric columns to float
    numeric_columns = ['DLCY', 'DFCY', 'DTOTAL', 'LLCY', 'LFCY', 'LTOTAL']
    new_df[numeric_columns] = new_df[numeric_columns].astype(float)

    # Main Page metrics calculation
    latest_entry = new_df.iloc[-1]
    previous_entry = new_df.iloc[-2]

    delta_DLCY = latest_entry['DLCY'] - previous_entry['DLCY']
    delta_DFCY = latest_entry['DFCY'] - previous_entry['DFCY']
    delta_DTOTAL = latest_entry['DTOTAL'] - previous_entry['DTOTAL']
    delta_LLCY = latest_entry['LLCY'] - previous_entry['LLCY']
    delta_LFCY = latest_entry['LFCY'] - previous_entry['LFCY']
    delta_LTOTAL = latest_entry['LTOTAL'] - previous_entry['LTOTAL']
    
    # Display metrics in two rows with three columns each
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Deposits LCY", value=f"{latest_entry['DLCY']:.2f}", delta=f"{delta_DLCY:.2f}")
    with col2:
        st.metric(label="Deposits FCY", value=f"{latest_entry['DFCY']:.2f}", delta=f"{delta_DFCY:.2f}")
    with col3:
        st.metric(label="Total Deposits", value=f"{latest_entry['DTOTAL']:.2f}", delta=f"{delta_DTOTAL:.2f}")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="Lending LCY", value=f"{latest_entry['LLCY']:.2f}", delta=f"{delta_LLCY:.2f}")
    with col5:
        st.metric(label="Lending FCY", value=f"{latest_entry['LFCY']:.2f}", delta=f"{delta_LFCY:.2f}")
    with col6:
        st.metric(label="Total Lending", value=f"{latest_entry['LTOTAL']:.2f}", delta=f"{delta_LTOTAL:.2f}")

    st.subheader("Latest Available Monthly PDF Report")

    # Path to the local PDF file
    pdf_path = "latest.pdf"

    # Function to read PDF file as bytes
    def get_pdf_bytes(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes

    # Get the PDF file content as bytes
    pdf_bytes = get_pdf_bytes(pdf_path)

    # Function to embed PDF file in Streamlit app
    def embed_pdf_viewer(pdf_bytes):
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_display = f'<embed src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf">'
        return pdf_display

    # Display the PDF file in Streamlit
    st.markdown(embed_pdf_viewer(pdf_bytes), unsafe_allow_html=True)


# Search Page
elif page == "Search DL Data":
    st.title("Search Data")
    search_filter = st.text_input("Search by Description")
    if search_filter:
        filtered_df = new_df[new_df['Description'].str.contains(search_filter, case=False, na=False)]
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "type": None, 
                "Date": "English Date",
                "Ndate":"Nepali Date", 
                "FY": "FY",
                "Year": st.column_config.NumberColumn(
                    "Year",
                    format="%.0f"
                ),
                "Month": "Month",
                "Week":"Week",
                "DTOTAL Growth":"Deposit Growth",
                "LTOTAL Growth":"Lending Growth",
           
                "DLCY": st.column_config.NumberColumn(
                    "Deposits LCY",
                    format="%.2f"
                ),
                "DFCY": st.column_config.NumberColumn(
                    "Deposit FCY",
                    format="%.2f"
                ),
                "DTOTAL": st.column_config.NumberColumn(
                    "Total Deposit",
                    format="%.2f"
                ),
                "LLCY": st.column_config.NumberColumn(
                    "Lending LCY",
                    format="%.2f"
                ),
                "LFCY": st.column_config.NumberColumn(
                    "Lending FCY",
                    format="%.2f"
                ),
                "LTOTAL": st.column_config.NumberColumn(
                    "Total Lending",
                    format="%.2f"
                ),
                "CD":st.column_config.NumberColumn(
                    "CD Ratio",
                    format="%.2f%%"

                ),
            },
            column_order=["FY","Year","Month","Week","Date","Ndate","DTOTAL","LTOTAL","CD","DTOTAL Growth","LTOTAL Growth"]     
                      
            )
    else:
        st.write("Enter a search term to filter the data.")




# Weeklly Page     
elif page == "Weekly DL Data":
    st.title("Weekly Data")
    
    
    # Convert 'DTOTAL' and 'LTOTAL' to numeric
    week_df['DTOTAL'] = week_df['DTOTAL'].astype(float)
    week_df['LTOTAL'] = week_df['LTOTAL'].astype(float)

    # Calculate the growth for deposits and loans
    week_df['DTOTAL Growth'] = week_df['DTOTAL'].diff()
    week_df['LTOTAL Growth'] = week_df['LTOTAL'].diff()

    # Add a slider to select the number of weeks to display
    num_weeks = st.slider("Select Number of Weeks", min_value=1, max_value=len(week_df), value=5)

    # Show only the selected number of weeks
    week_df_last_n = week_df.tail(num_weeks)

    # Melt the DataFrame and rename the values in the 'Total Type' column
    df_melted = week_df_last_n.melt(id_vars='Description', value_vars=['DTOTAL Growth', 'LTOTAL Growth'], var_name='Total Type', value_name='Growth')
    df_melted['Total Type'] = df_melted['Total Type'].replace({
        'DTOTAL Growth': 'Deposit Growth',
        'LTOTAL Growth': 'Lending Growth'
    })


    fig = px.bar(
        df_melted,
        x='Description',
        y='Growth',
        color='Total Type',
        barmode='group',
        title=f'Weekly Deposits and Loans Growth Over Time (Last {num_weeks} Data Points)',
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Month and Week",
        yaxis_title="Growth",
        legend=dict(
            title="",
            orientation="h",
            y=1.1,
            yanchor="bottom",
            x=0.5,
            xanchor="center",
            font=dict(
                size=12,
                color="black"
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        week_df, 
        use_container_width=True,
        hide_index=True,
        column_config={
                "type": None, 
                "Date": "English Date",
                "Ndate":"Nepali Date", 
                "FY": "FY",
                "Year": st.column_config.NumberColumn(
                    "Year",
                    format="%.0f"
                ),
                "Month": "Month",
                "Week":"Week",
                "DTOTAL Growth":"Deposit Growth",
                "LTOTAL Growth":"Lending Growth",
           
                "DLCY": st.column_config.NumberColumn(
                    "Deposits LCY",
                    format="%.2f"
                ),
                "DFCY": st.column_config.NumberColumn(
                    "Deposit FCY",
                    format="%.2f"
                ),
                "DTOTAL": st.column_config.NumberColumn(
                    "Total Deposit",
                    format="%.2f"
                ),
                "LLCY": st.column_config.NumberColumn(
                    "Lending LCY",
                    format="%.2f"
                ),
                "LFCY": st.column_config.NumberColumn(
                    "Lending FCY",
                    format="%.2f"
                ),
                "LTOTAL": st.column_config.NumberColumn(
                    "Total Lending",
                    format="%.2f"
                ),
                "CD":st.column_config.NumberColumn(
                    "CD Ratio",
                    format="%.2f%%"

                ),
            },
            column_order=["FY","Year","Month","Week","Date","Ndate","DTOTAL","LTOTAL","CD","DTOTAL Growth","LTOTAL Growth"]
        )

# Monthly Page
elif page == "Monthly DL Data":
    st.title("Monthly Data")

    # Add dropdown for selecting a fiscal year for the bar chart
    fiscal_years = month_df['FY'].unique()
    selected_fy_for_bar = st.selectbox("Select Fiscal Year for Bar Chart", fiscal_years)

    # Filter data based on the selected fiscal year for the bar chart
    filtered_month_df_bar = month_df[month_df['FY'] == selected_fy_for_bar]

    # Convert 'DTOTAL' and 'LTOTAL' to numeric
    filtered_month_df_bar['DTOTAL'] = filtered_month_df_bar['DTOTAL'].astype(float)
    filtered_month_df_bar['LTOTAL'] = filtered_month_df_bar['LTOTAL'].astype(float)

    # Calculate the growth for deposits and loans
    filtered_month_df_bar['DTOTAL Growth'] = filtered_month_df_bar['DTOTAL'].diff()
    filtered_month_df_bar['LTOTAL Growth'] = filtered_month_df_bar['LTOTAL'].diff() 

    # Melt the DataFrame and rename the values in the 'Total Type' column
    df_melted = filtered_month_df_bar.melt(id_vars='Month', value_vars=['DTOTAL Growth', 'LTOTAL Growth'], var_name='Total Type', value_name='Growth')
    df_melted['Total Type'] = df_melted['Total Type'].replace({
        'DTOTAL Growth': 'Deposit Growth',
        'LTOTAL Growth': 'Lending Growth'
    })

    fig = px.bar(
        df_melted,
        x='Month',
        y='Growth',
        color='Total Type',
        barmode='group',
        title='Monthly Deposits and Loans Growth Over Time',
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount in Billions",
        legend=dict(
            title="",
            orientation="h",
            y=1.1,
            yanchor="bottom",
            x=0.5,
            xanchor="center",
            font=dict(
                size=12,
                color="black"
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add multiselect for selecting fiscal years for the line charts
    selected_fys_for_line = st.multiselect("Select Fiscal Years for Line Charts", fiscal_years, default=fiscal_years[:1])

    # Filter data based on the selected fiscal years for the line charts
    filtered_month_df_line = month_df[month_df['FY'].isin(selected_fys_for_line)]

    # Convert 'DTOTAL' and 'LTOTAL' to numeric
    filtered_month_df_line['DTOTAL'] = filtered_month_df_line['DTOTAL'].astype(float)
    filtered_month_df_line['LTOTAL'] = filtered_month_df_line['LTOTAL'].astype(float)
    if not filtered_month_df_line.empty:
        # Calculate percentage change for DTOTAL and LTOTAL
        filtered_month_df_line['DTOTAL Growth'] = filtered_month_df_line['DTOTAL'].pct_change() * 100
        filtered_month_df_line['LTOTAL Growth'] = filtered_month_df_line['LTOTAL'].pct_change() * 100

        # Replace NaN values with 0 or a suitable value
        filtered_month_df_line['DTOTAL Growth'].fillna(0, inplace=True)
        filtered_month_df_line['LTOTAL Growth'].fillna(0, inplace=True)

        col1, col2 = st.columns(2)
        with col1:
            # Line chart for DTOTAL
            st.subheader("Monthly Deposit Growth")
            fig_dtotal = px.line(
                filtered_month_df_line,
                x="Month",
                y="DTOTAL Growth",
                color='FY',
                line_shape="spline",
                markers=True,
                text="DTOTAL Growth"  # Display the values as text
            )
            fig_dtotal.update_layout(xaxis_title="Month")
            fig_dtotal.update_traces(textposition="middle right", texttemplate='%{text:.2f}%')
            st.plotly_chart(fig_dtotal, use_container_width=True)

        with col2:
            # Line chart for LTOTAL
            st.subheader("Monthly Lending Growth")
            fig_ltotal = px.line(
                filtered_month_df_line,
                x="Month",
                y="LTOTAL Growth",
                color='FY',
                line_shape="spline",
                markers=True,
                text="LTOTAL Growth"  # Display the values as text
            )
            fig_ltotal.update_layout(xaxis_title="Month")
            fig_ltotal.update_traces(textposition="middle right", texttemplate='%{text:.2f}%')
            st.plotly_chart(fig_ltotal, use_container_width=True)
    else:
        st.write("No data available to display.")
    st.dataframe(
        filtered_month_df_line,
        use_container_width=True,
        hide_index=True,
            column_config={
                "type": None,
                "Bank":None,  
                "Date": "English Date",
                "Ndate":"Nepali Date",
                "FY": "FY",
                "Year": st.column_config.NumberColumn(
                    "Year",
                    format="%.0f"
                ),
                "Month": "Month",
                "Week":None ,
           
                "DLCY": st.column_config.NumberColumn(
                    "Deposits LCY",
                    format="%.2f"
                ),
                "DFCY": st.column_config.NumberColumn(
                    "Deposit FCY",
                    format="%.2f"
                ),
                "DTOTAL": st.column_config.NumberColumn(
                    "Total Deposit",
                    format="%.2f"
                ),
                "LLCY": st.column_config.NumberColumn(
                    "Lending LCY",
                    format="%.2f"
                ),
                "LFCY": st.column_config.NumberColumn(
                    "Lending FCY",
                    format="%.2f"
                ),
                "LTOTAL": st.column_config.NumberColumn(
                    "Total Lending",
                    format="%.2f"
                ),
                "CD":st.column_config.NumberColumn(
                    "CD Ratio",
                    format="%.2f%%"

                ),
                "DTOTAL Growth":st.column_config.NumberColumn(
                    "Deposit Growth",
                    format="%.2f%%"
                ),
                "LTOTAL Growth":st.column_config.NumberColumn(
                    "Lending Growth",
                    format="%.2f%%"
                ),
            },
             column_order=["FY","Year","Month","Week","Date","Ndate","DTOTAL","LTOTAL","CD","DTOTAL Growth","LTOTAL Growth"]  
        )

elif page == "BankWise DL Data":
    st.title("BankWise Data")
    with st.expander("Click here for latest DL Data"):
        st.header(f"As of {new_df['Description'].iloc[-1]} ({new_df['Ndate'].iloc[-1]})")
        # Find the maximum date in new_df
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        max_date = df["Date"].max()

        st.write("or")

        selected_date=st.date_input("Choose a date", value=max_date, max_value=max_date)
        st.write("DL data are collected on weekends at Fridays")

        # Filter new_df for entries with the maximum date
        selected_date_entries = df[df["Date"] == selected_date]
        st.dataframe(
            selected_date_entries,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": None,
                "FY": None,
                "Year": None,
                "Month": None,
                "Week": None,
                "type": None,
                "Ndate": None,             
                "Bank": {"title": "Bank Name"},
                "DLCY": st.column_config.NumberColumn(
                    "Deposits LCY",
                    format="%.2f"
                ),
                "DFCY": st.column_config.NumberColumn(
                    "Deposit FCY",
                    format="%.2f"
                ),
                "DTOTAL": st.column_config.NumberColumn(
                    "Total Deposit",
                    format="%.2f"
                ),
                "LLCY": st.column_config.NumberColumn(
                    "Lending LCY",
                    format="%.2f"
                ),
                "LFCY": st.column_config.NumberColumn(
                    "Lending FCY",
                    format="%.2f"
                ),
                "LTOTAL": st.column_config.NumberColumn(
                    "Total Lending",
                    format="%.2f"
                ),
                "CD":st.column_config.NumberColumn(
                    "CD Ratio",
                    format="%.2f%%"

                ),
            },
        )


    with st.expander("Compare banks", expanded=True):
        bankwise_df=df[df["type"]=="End"]
        # Find the maximum date in new_df
        max_date = bankwise_df["Date"].max()

        # Filter new_df for entries with the maximum date
        max_date_entries = bankwise_df[bankwise_df["Date"] == max_date]

        filtered_bank = st.multiselect("Choose a bank", sorted(bankwise_df['Bank'].unique()),default="Agricultural Development Bank Ltd")
        st.write("Choose time period for comparison")

        # Create two columns layout
        from_column, to_column = st.columns(2)

        # From Year and Month selection
        with from_column:
            from_year = st.selectbox("From Year", sorted(bankwise_df['Year'].unique()))
            from_month = st.selectbox("From Month", sorted(bankwise_df['Month'].unique()))

        # To Year and Month selection
        with to_column:
            to_year = st.selectbox("To Year", sorted(bankwise_df['Year'].unique()), index=len(bankwise_df['Year'].unique()) - 1)
            to_month = st.selectbox("To Month", sorted(bankwise_df['Month'].unique()), index=len(bankwise_df['Month'].unique()) - 1)

        # Find the index where the From Year and Month are first found
        from_index = bankwise_df.index[(bankwise_df['Year'] == from_year) & (bankwise_df['Month'] == from_month)].min()

        # Find the index where the To Year and Month are found
        to_index = bankwise_df.index[(bankwise_df['Year'] == to_year) & (bankwise_df['Month'] == to_month)].max()

        # Filter the dataframe based on the selected date range and bank
        filtered_df_bank = bankwise_df.loc[from_index:to_index]
        filtered_df_bank["ChartDate"] = bankwise_df['Year'].astype(str) + '-' + bankwise_df['Month'].astype(str)


        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Deposit")
            fig_dtotal = px.line(
                filtered_df_bank[filtered_df_bank['Bank'].isin(filtered_bank)],
                x="ChartDate",
                y="DTOTAL",
                color="Bank",
                line_shape="spline",
                markers=True
            )
            fig_dtotal.update_layout(
                xaxis_title="Date",
                yaxis_title="Amount in Billions (Rs)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_dtotal, use_container_width=True)

        with col2:
            st.subheader("Lending")
            fig_ltotal = px.line(
                filtered_df_bank[filtered_df_bank['Bank'].isin(filtered_bank)],
                x="ChartDate",
                y="LTOTAL",
                color="Bank",
                line_shape="spline",
                markers=True
            )
            fig_ltotal.update_layout(
                xaxis_title="Date",
                yaxis_title="Amount in Billions (Rs)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_ltotal, use_container_width=True)
        
    with st.expander("Individual Bank", expanded=True):
        ind_bank_select=st.selectbox("Select a bank", options=sorted(bankwise_df['Bank'].unique()))
        ind_bank_df=df[df['Bank']==ind_bank_select]
        st.dataframe(
            ind_bank_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "type": None,
                "Bank":None,  
                "Date": "English Date",
                "Ndate":"Nepali Date",
                "FY": "FY",
                "Year": st.column_config.NumberColumn(
                    "Year",
                    format="%.0f"
                ),
                "Month": "Month",
                "Week":"Week",
           
                "DLCY": st.column_config.NumberColumn(
                    "Deposits LCY",
                    format="%.2f"
                ),
                "DFCY": st.column_config.NumberColumn(
                    "Deposit FCY",
                    format="%.2f"
                ),
                "DTOTAL": st.column_config.NumberColumn(
                    "Total Deposit",
                    format="%.2f"
                ),
                "LLCY": st.column_config.NumberColumn(
                    "Lending LCY",
                    format="%.2f"
                ),
                "LFCY": st.column_config.NumberColumn(
                    "Lending FCY",
                    format="%.2f"
                ),
                "LTOTAL": st.column_config.NumberColumn(
                    "Total Lending",
                    format="%.2f"
                ),
                "CD":st.column_config.NumberColumn(
                    "CD Ratio",
                    format="%.2f%%"

                ),
            },
        )