import pandas as pd
import plotly.express as px
import streamlit as st
import base64

# Set up the dashboard configuration
st.set_page_config(
    page_title="NBA DL Data Dashboard",
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


with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

    st.sidebar.markdown(
        f"""
        <style>
            .sidebar .sidebar-content {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .sidebar .sidebar-content img {{
                margin-top: 20px;
                margin-bottom: 10px;
                max-width: 150px; /* Adjust the max-width as needed */
                height: auto; /* Maintain aspect ratio */
            }}
        </style>
        <div class="sidebar">
            <div class="sidebar-content">
                <img src="data:image/png;base64,{data}" alt="Logo">
                <h4>Nepal Bankers' Association</h4>
                <p>Compiled by NBA</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
# Add navigation sidebar
st.sidebar.title("Choose an option")
page = st.sidebar.radio("Go to", ["Home Page", "Search DL Data", "Weekly DL Data", "Monthly DL Data","BankWise DL Data","CD Ratio"])

if page == "Home Page":
    st.title("Deposit and Lending of Commercial Banks")
    st.subheader("Compiled by Nepal Bankers' Association")
    st.header(f"As of {new_df['Description'].iloc[-1]} ({new_df['Ndate'].iloc[-1]})")
    st.write("Amounts in Rs (Billions)")
    st.write("Metrics are compared from previous week data")
    
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

    with st.expander("Click here for Monthly PDF Report from NBA",expanded=False):
        st.subheader("Latest Available Monthly PDF Reports")
        st.image(image="latest.png",use_column_width=True)
    
    with st.expander("DL Data Comparison", expanded=False):
        # Layout with two columns for date range selection
        col_from, col_to = st.columns(2)

        # Get the first and last entries of new_df
        first_entry = new_df.iloc[0]
        last_entry = new_df.iloc[-1]

        # From Year, Month, and Week selection
        with col_from:
            from_year_new = st.selectbox("From Year", sorted(new_df['Year'].unique()), index=sorted(new_df['Year'].unique()).index(first_entry['Year']), key="from_year_new")
            from_month_new = st.selectbox("From Month", new_df['Month'].unique(), index=sorted(new_df['Month'].unique()).index(first_entry['Month']), key="from_month_new")
            from_week_new = st.selectbox("From Week", sorted(new_df['Week'].unique()), index=sorted(new_df['Week'].unique()).index(first_entry['Week']), key="from_week_new")

        # To Year, Month, and Week selection
        with col_to:
            to_year_new = st.selectbox("To Year", sorted(new_df['Year'].unique()), index=sorted(new_df['Year'].unique()).index(last_entry['Year']), key="to_year_new")
            to_month_new = st.selectbox("To Month",(new_df['Month'].unique()), index=sorted(new_df['Month'].unique()).index(last_entry['Month']), key="to_month_new")
            to_week_new = st.selectbox("To Week", sorted(new_df['Week'].unique()), index=sorted(new_df['Week'].unique()).index(last_entry['Week']), key="to_week_new")

        # Filter the dataframe based on the selected date range
        from_index_new = new_df.index[(new_df['Year'] == from_year_new) & (new_df['Month'] == from_month_new) & (new_df['Week'] == from_week_new)].min()
        to_index_new = new_df.index[(new_df['Year'] == to_year_new) & (new_df['Month'] == to_month_new) & (new_df['Week'] == to_week_new)].max()

        filtered_df_new = new_df.loc[from_index_new:to_index_new]

        # Calculate percentage and value changes
        dtotal_change_new = (filtered_df_new['DTOTAL'].iloc[-1] - filtered_df_new['DTOTAL'].iloc[0]) / filtered_df_new['DTOTAL'].iloc[0] * 100
        ltotal_change_new = (filtered_df_new['LTOTAL'].iloc[-1] - filtered_df_new['LTOTAL'].iloc[0]) / filtered_df_new['LTOTAL'].iloc[0] * 100
        cd_change_new = (filtered_df_new['CD'].iloc[-1] - filtered_df_new['CD'].iloc[0]) / filtered_df_new['CD'].iloc[0] * 100

        # Calculate value changes
        dtotal_value_change = filtered_df_new['DTOTAL'].iloc[-1] - filtered_df_new['DTOTAL'].iloc[0]
        ltotal_value_change = filtered_df_new['LTOTAL'].iloc[-1] - filtered_df_new['LTOTAL'].iloc[0]
        cd_value_change = filtered_df_new['CD'].iloc[-1] - filtered_df_new['CD'].iloc[0]

        # Layout for displaying metrics in three columns
        
        metric_col1, metric_col2, metric_col3 = st.columns([1, 1, 1])

        # Row 1: "From" data
        metric_col1.metric(label="Starting Deposit", value=f"{filtered_df_new['DTOTAL'].iloc[0]:.2f}")
        metric_col2.metric(label="Starting Lending", value=f"{filtered_df_new['LTOTAL'].iloc[0]:.2f}")
        metric_col3.metric(label="Starting CD", value=f"{filtered_df_new['CD'].iloc[0]:.2f}%")

        # Row 2: "To" data
        metric_col1.metric(label="Ending Deposit", value=f"{filtered_df_new['DTOTAL'].iloc[-1]:.2f}")
        metric_col2.metric(label="Ending Lending", value=f"{filtered_df_new['LTOTAL'].iloc[-1]:.2f}")
        metric_col3.metric(label="Ending CD", value=f"{filtered_df_new['CD'].iloc[-1]:.2f}%")

        # Row 3: "Change" data
        metric_col1.metric(label="Deposit Change", value=f"{dtotal_value_change:.2f}", delta=f"{dtotal_change_new:.2f}%")
        metric_col2.metric(label="Lending Change", value=f"{ltotal_value_change:.2f}", delta=f"{ltotal_change_new:.2f}%")
        metric_col3.metric(label="CD Change", value=f"{cd_value_change:.2f}", delta=f"{cd_change_new:.2f}%")




# Search Page
elif page == "Search DL Data":
    st.title("Search Data")
    st.markdown("""

    Enter a keyword in the search box below to filter the data based on the description. You can use partial or full words to search. For example:
    
    - To find entries for a specific year, type the year, either in Nepali or English Date format(e.g., '2023' or '2081').
    - To find entries for a specific month, type the month (e.g., 'January' or 'Jan', or 'Baisakh').
    - To find entries for a specific year and month, type both (e.g.'2081 Baisakh').
    - To find entries for a specific year and month and week, type ('2081 Baisakh 1st Week' or '2081 Shrawan 3rd Week').
    - Or just simply enter the date (e.g. '2024-07-24' or '3/7/2081')
    
    Note: The search is case-insensitive.
    """)

    new_df['Long Date'] = pd.to_datetime(new_df['Date']).dt.strftime('%B %d, %Y')

    search_filter = st.text_input("Search by Description")
    if search_filter:
        filtered_df = new_df[
            (new_df['Description'].str.contains(search_filter, case=False, na=False)) |
            (new_df['Year'].astype(str).str.contains(search_filter, case=False, na=False)) |
            (new_df['Month'].str.contains(search_filter, case=False, na=False)) |
            (new_df['FY'].astype(str).str.contains(search_filter, case=False, na=False)) |
            (new_df['Date'].astype(str).str.contains(search_filter, case=False, na=False)) |
            (new_df['Ndate'].astype(str).str.contains(search_filter, case=False, na=False)) |
            (new_df['Long Date'].str.contains(search_filter, case=False, na=False)) 
            # Add more columns as needed
        ]
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
            # Description for search functionality





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
    month_df["Yearmonth"] = month_df["Year"].astype(str) + "-" + month_df["Month"].astype(str)


    # Layout with two columns for date range selection
    from_column, to_column = st.columns(2)

    # From Year and Month selection
    with from_column:
        from_year_m = st.selectbox("From Year", sorted(month_df['Year'].unique()))
        from_month_m = st.selectbox("From Month", sorted(month_df['Month'].unique()))

    # To Year and Month selection
    with to_column:
        to_year_m = st.selectbox("To Year", sorted(month_df['Year'].unique()), index=len(month_df['Year'].unique()) - 1)
        to_month_m = st.selectbox("To Month", sorted(month_df['Month'].unique()), index=len(month_df['Month'].unique()) - 1)

    # Find the index where the From Year and Month are first found
    from_index = month_df.index[(month_df['Year'] == from_year_m) & (month_df['Month'] == from_month_m)].min()

    # Find the index where the To Year and Month are found
    to_index = month_df.index[(month_df['Year'] == to_year_m) & (month_df['Month'] == to_month_m)].max()

    # Filter the dataframe based on the selected date range
    filtered_df_monthly = month_df.loc[from_index:to_index]

    # Layout with two columns for displaying data
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Deposit Trend")
        fig_deposit = px.line(
            filtered_df_monthly,
            x="Yearmonth",
            y="DTOTAL",
            labels={"DTOTAL": "Total Deposit", "Date": "Date"},
            line_shape="spline",
            markers=True
        )
        fig_deposit.update_layout(xaxis_title="Date", yaxis_title="Amount in Billions")
        st.plotly_chart(fig_deposit, use_container_width=True)

    with col2:
        st.subheader("Total Lending Trend")
        fig_lending = px.line(
            filtered_df_monthly,
            x="Yearmonth",
            y="LTOTAL",
            labels={"LTOTAL": "Total Lending", "Date": "Date"},
            line_shape="spline",
            markers=True
        )
        fig_lending.update_layout(xaxis_title="Date", yaxis_title="Amount in Billions")
        st.plotly_chart(fig_lending, use_container_width=True)










    st.header("Monthly Growth Comparison (Amount)")
    # Add dropdown for selecting a fiscal year for the bar chart
    fiscal_years = month_df['FY'].unique()
    selected_fy_for_bar = st.selectbox("Select Fiscal Year for Bar Chart", fiscal_years, index=len(fiscal_years)-1)

    # Filter data based on the selected fiscal year for the bar chart
    filtered_month_df_bar = month_df[month_df['FY'] == selected_fy_for_bar]

    # Convert 'DTOTAL' and 'LTOTAL' to numeric
    filtered_month_df_bar['DTOTAL'] = month_df['DTOTAL'].astype(float)
    filtered_month_df_bar['LTOTAL'] = month_df['LTOTAL'].astype(float)

    # Calculate the growth for deposits and loans
    filtered_month_df_bar['DTOTAL Growth'] = month_df['DTOTAL'].diff()
    filtered_month_df_bar['LTOTAL Growth'] = month_df['LTOTAL'].diff() 

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

    st.header("Monthly Growth Comparison (Percentage)")

    # Add multiselect for selecting fiscal years for the line charts
    selected_fys_for_line = st.multiselect("Select Fiscal Years for Line Charts", fiscal_years, default=fiscal_years[1])

    # Filter data based on the selected fiscal years for the line charts
    filtered_month_df_line = month_df[month_df['FY'].isin(selected_fys_for_line)]

    # Convert 'DTOTAL' and 'LTOTAL' to numeric
    filtered_month_df_line['DTOTAL'] = month_df['DTOTAL'].astype(float)
    filtered_month_df_line['LTOTAL'] = month_df['LTOTAL'].astype(float)
    if not filtered_month_df_line.empty:
        # Calculate percentage change for DTOTAL and LTOTAL
        filtered_month_df_line['DTOTAL Growth'] = month_df['DTOTAL'].pct_change() * 100
        filtered_month_df_line['LTOTAL Growth'] = month_df['LTOTAL'].pct_change() * 100

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
            fig_dtotal.update_layout(xaxis_title="",yaxis_title="%(Percentage)")
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
            fig_ltotal.update_layout(xaxis_title="",yaxis_title="%(Percentage)")
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
    with st.expander("Click here for latest Monthly DL Data"):
       
        end_df=df[df["type"]=="End"]
        
        # Find the last year and month in the DataFrame
        last_year = end_df['Year'].iloc[-1]
        last_month = end_df['Month'].iloc[-1]

        # Create the selectboxes
        chosen_year = st.selectbox("Choose Year", end_df['Year'].unique(), index=list(end_df['Year'].unique()).index(last_year))
        chosen_month = st.selectbox("Choose Month", end_df['Month'].unique(), index=list(end_df['Month'].unique()).index(last_month))
        st.header(f"As of {chosen_year} {chosen_month}")

        # Filter the DataFrame for entries with the chosen year and month
        selected_date_entries = end_df[(end_df["Year"] == chosen_year) & (end_df["Month"] == chosen_month)]
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


    with st.expander("Compare bankwise data", expanded=True):
        bankwise_df=df[df["type"]=="End"]
        # Find the maximum date in new_df
        max_date = bankwise_df["Date"].max()

        # Filter new_df for entries with the maximum date
        max_date_entries = bankwise_df[bankwise_df["Date"] == max_date]

        filtered_bank = st.multiselect("Choose a bank", sorted(bankwise_df['Bank'].unique()),default="Agricultural Development Bank Ltd",placeholder="Choose Banks for LineCharts")
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
        ind_bank_df=bankwise_df[bankwise_df['Bank']==ind_bank_select]
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
elif page == "CD Ratio":
    st.title("Credit to Deposit Ratio")

    # Create tabs for Monthly and Weekly data
    tab1, tab2 = st.tabs(["Monthly Data", "Weekly Data"])

    with tab1:
        st.subheader("Monthly Data")
        
        # Layout with two columns
        col1, col2 = st.columns([1, 1.5])
        latest_cd = new_df.iloc[-1]['CD'] 

        with col1:
            st.metric(label=f"As of {new_df['Description'].iloc[-1]} ({new_df['Ndate'].iloc[-1]})", value=f"{latest_cd:.2f}%")
            month_df_sort = month_df.sort_values(by="Date", ascending=False)
            st.dataframe(
                month_df_sort,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "type": None,
                    "Bank": None,
                    "Date": "English Date",
                    "Ndate": "Nepali Date",
                    "FY": "FY",
                    "Year": st.column_config.NumberColumn(
                        "Year",
                        format="%.0f"
                    ),
                    "Month": "Month",
                    "Week": None,
                    "DLCY": None,
                    "DFCY": None,
                    "DTOTAL": None,
                    "LLCY": None,
                    "LFCY": None,
                    "LTOTAL": None,
                    "CD": st.column_config.NumberColumn(
                        "CD Ratio",
                        format="%.2f%%"
                    ),
                },
                column_order=["FY", "Year", "Month", "CD"]
            )

        with col2:
            st.subheader("CD Ratio Over Time")
            # Filter by Fiscal Year (FY)
            selected_fy = st.selectbox("Select Fiscal Year", month_df["FY"].unique(), index=(len(month_df["FY"].unique())-1))

            filtered_month_df_cd = month_df[month_df["FY"] == selected_fy]

            fig_cd_ratio = px.line(
                filtered_month_df_cd,
                x="Month",
                y="CD",
                title=f"CD Ratio Over Time for FY {selected_fy}",
                line_shape="spline",
                markers=True
            )
            fig_cd_ratio.update_layout(xaxis_title="Date", yaxis_title="CD Ratio (%)")

            st.plotly_chart(fig_cd_ratio, use_container_width=True)

    with tab2:
        st.subheader("Weekly Data")
        
        # Layout with two columns
        col1, col2 = st.columns([1, 1.5])
        latest_cd = new_df.iloc[-1]['CD'] 

        with col1:
            st.metric(label=f"As of {new_df['Description'].iloc[-1]} ({new_df['Ndate'].iloc[-1]})", value=f"{latest_cd:.2f}%")
            week_df_sort = week_df.sort_values(by="Date", ascending=False)
            st.dataframe(
                week_df_sort,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "type": None,
                    "Bank": None,
                    "Date": "English Date",
                    "Ndate": "Nepali Date",
                    "FY": "FY",
                    "Year": st.column_config.NumberColumn(
                        "Year",
                        format="%.0f"
                    ),
                    "Month": "Month",
                    "Week": "Week",
                    "DLCY": None,
                    "DFCY": None,
                    "DTOTAL": None,
                    "LLCY": None,
                    "LFCY": None,
                    "LTOTAL": None,
                    "CD": st.column_config.NumberColumn(
                        "CD Ratio",
                        format="%.2f%%"
                    ),
                },
                column_order=["FY", "Year", "Month", "Week", "CD"]
            )

        with col2:
            st.subheader("CD Ratio Over Time")
            # Filter by Fiscal Year (FY)
            selected_fy = st.selectbox("Select Fiscal Year", week_df["FY"].unique(), index=(len(week_df["FY"].unique())-1))

            filtered_week_df_cd = week_df[week_df["FY"] == selected_fy]

            fig_cd_ratio_week = px.line(
                filtered_week_df_cd,
                x="Description",
                y="CD",
                title=f"CD Ratio Over Time for FY {selected_fy}",
                line_shape="spline",
                markers=True
            )
            fig_cd_ratio_week.update_layout(xaxis_title="Week", yaxis_title="CD Ratio (%)")

            st.plotly_chart(fig_cd_ratio_week, use_container_width=True)
