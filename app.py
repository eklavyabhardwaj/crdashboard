import plotly.express as px
import plotly.graph_objects as go
import calendar
import sqlite3
from flask import  render_template, request
import pandas as pd
from flask import Flask, send_from_directory


app = Flask(__name__)

# Define the database file path
database_file = 'conversion_data.db'


# Function to fetch data from the database
def fetch_data():
    try:
        conn = sqlite3.connect(database_file)
        query = "SELECT * FROM conversion_rate"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None


@app.route('/ELEC.png')
def favicon():
    return send_from_directory('static', 'ELEC.png', mimetype='image/x-icon')


# Define a function to format the numbers
def format_inr(number):
    if number >= 1e7:  # If the number is greater than or equal to 10 million
        return 'INR {:.2f} Cr'.format(number / 1e7)  # Convert to crore
    elif number >= 1e5:  # If the number is greater than or equal to 100 thousand
        return 'INR {:.2f} Lakh'.format(number / 1e5)  # Convert to lakh
    else:
        return 'INR {:.2f}'.format(number)

def percent_conversion(value):

    return '{:.2f}%'.format(value)


@app.route('/')
def index():
    df = fetch_data()

    rename_column = {'month': 'Month',
                     'deal_pipeline': 'Name',
                     'total_opp_value': 'Opportunity Amount (INR Cr)',
                     'sales_order_total_value': 'Order Value (INR Cr)',
                     'conversion_rate': 'Conversion Rate'}

    df.rename(columns=rename_column, inplace=True)

    df = df[['Month', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]
    plot_df = df.copy()


    df['Date and Time'] = pd.to_datetime(df['Month'], format = '%B %Y')



    # Extract year from the 'Date and Time' column
    df['Year'] = df['Date and Time'].dt.year

    #df['Month'] = df['Date and Time'].dt.strftime('%Y-%m')  # Sortable year-month format




    df['Opportunity Amount (INR Cr)'] = df['Opportunity Amount (INR Cr)'].apply(format_inr)

    df['Order Value (INR Cr)'] = df['Order Value (INR Cr)'].apply(format_inr)

    df['Conversion Rate'] = df['Conversion Rate'].apply(percent_conversion)



    e_df = df.copy()


    #y_mdf = df.copy()

    # Filter by selected year
    unique_years = sorted(df['Year'].unique(), reverse=True)
    selected_year = request.args.get('year', default=unique_years[0], type=int)
    y_mdf = df[df['Year'] == selected_year].copy()  # Use y_mdf for the pivot table creation

    # Sort y_mdf by 'Date and Time'
    y_mdf.sort_values(by='Date and Time', inplace=True)

    # Create the pivot table from the filtered y_mdf
    pivot_df = y_mdf.pivot_table(index='Name', columns='Month', values='Conversion Rate', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df.index.name = None
    pivot_df.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df.index:
        pivot_df = pivot_df.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df[month] = None


    ##### Pivot Table for Conversion Rate
    # Sort the columns of the pivot table based on the sorted month list
    pivot_df = pivot_df.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)


    ##### Pivot table for opportunity value


    # Create the pivot table from the filtered y_mdf
    pivot_df1 = y_mdf.pivot_table(index='Name', columns='Month', values='Opportunity Amount (INR Cr)', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df1.index.name = None
    pivot_df1.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df1.index:
        pivot_df1 = pivot_df1.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df1.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df1[month] = None

    # Sort the columns of the pivot table based on the sorted month list
    pivot_df1 = pivot_df1.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)


    ### pivot table for sales order

    # Create the pivot table from the filtered y_mdf
    pivot_df2 = y_mdf.pivot_table(index='Name', columns='Month', values='Order Value (INR Cr)', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df2.index.name = None
    pivot_df2.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df2.index:
        pivot_df1 = pivot_df2.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df2.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df2[month] = None

    # Sort the columns of the pivot table based on the sorted month list
    pivot_df2 = pivot_df2.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)


    pivot_df1.fillna('N/A', inplace=True)
    pivot_df.fillna('N/A', inplace=True)
    pivot_df2.fillna('N/A', inplace=True)



    ### rest codes

    e_df = e_df.sort_values(by = 'Name')

    # Convert 'Month' column to datetime if it's not already in datetime format
    e_df['Month'] = pd.to_datetime(e_df['Month'])

    # Sort the DataFrame by 'Month' column in descending order (from latest to oldest)
    e_df = e_df.sort_values(by='Month', ascending=False)

    e_df['Month'] = e_df['Month'].dt.strftime('%B %Y')

    e_df = e_df[['Month', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]




    # Check if the quarter parameter is provided in the URL
    selected_month = request.args.get('month')

    # If the quarter is not provided, set it to the latest quarter
    if not selected_month and not df.empty:
        selected_month = e_df['Month'].iloc[0]

    # selected_name = request.args.get('name')
    if selected_month:
        e_df = e_df[e_df['Month'] == selected_month]
    else:
        e_df = e_df

    # Sort DataFrame by Name

    df = df.sort_values(by= 'Conversion Rate')


    # Line chart for conversion rate with dots and dropdown
    conversion_rate_chart = px.line(plot_df, x='Month', y='Conversion Rate', color='Name',
                                    title='Conversion Rate Over Months',
                                    labels={'Name': 'Select Name', 'Conversion Rate': 'Conversion Rate'},
                                    template='plotly_white', markers=True)

    # Line chart for Order Value
    order_value_chart = px.line(plot_df, x='Month', y='Order Value (INR Cr)', color='Name',
                                title='Order Value Over Months',
                                labels={'Name': 'Select Name', 'Order Value (INR Cr)': 'Order Value'},
                                template='plotly_white', markers=True)

    # Line chart for Opportunity Amount
    opportunity_chart = px.line(plot_df, x='Month', y='Opportunity Amount (INR Cr)', color='Name',
                                title='Opportunity Amount Over Months',
                                labels={'Name': 'Select Name', 'Opportunity Amount (INR Cr)': 'Opportunity Amount'},
                                template='plotly_white', markers=True)

    # Combined bar chart for order value and opportunity amount with dropdown
    combined_chart = go.Figure()



    # Update layout for combined chart
    combined_chart.update_layout(
        title='Combined Chart - Order Value vs Opportunity Amount Over Months',
        xaxis_title='Month',
        yaxis_title='Amount (INR Cr)',
        barmode='group'
    )

    layout = {
        'conversion_rate_chart': conversion_rate_chart.to_html(full_html=False),
        'order_value_chart': order_value_chart.to_html(full_html=False),
        'opportunity_chart': opportunity_chart.to_html(full_html=False),
        'combined_chart': combined_chart.to_html(full_html=False),
        'pivot_table':pivot_df.to_html(classes='pivot-table', index=True),
        'pivot_table1':pivot_df1.to_html(classes='pivot-table1',index = True),
        'pivot_table2':pivot_df2.to_html(classes= 'pivot-table2',index = True),
        'years': unique_years,
        'df': e_df.to_html(index=False),
        'months': df['Month'].unique()
        # Pass unique months for the dropdown menu

    }


    return render_template('dashboard.html', layout=layout)


# Update Flask route to render quarterly and yearly pages
@app.route('/quarterly',methods = ['GET','POST'])
def quarterly():
    df = fetch_data()

    rename_column = {'month': 'Month',
                     'deal_pipeline': 'Name',
                     'total_opp_value': 'Opportunity Amount (INR Cr)',
                     'sales_order_total_value': 'Order Value (INR Cr)',
                     'conversion_rate': 'Conversion Rate'}

    df.rename(columns=rename_column, inplace=True)

    df = df[['Month', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]


    df['Date and Time'] = pd.to_datetime(df['Month'], format='%B %Y')



    df['Quarter'] = df['Date and Time'].dt.to_period('Q').dt.asfreq('Q-APR')


    # Inside the quarterly route
    df['Quarter'] = df['Quarter'].astype(str)  # Convert Period objects to string



    # Group by 'Name' and 'Quarter' and calculate sum of 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', and mean of 'Conversion Rate'
    quarter_df = df.groupby(['Name', 'Quarter']).agg({
        'Opportunity Amount (INR Cr)': 'sum',
        'Order Value (INR Cr)': 'sum',
        'Conversion Rate': 'mean'
    }).reset_index()

    quarter_df.sort_values(by='Quarter', ascending=False, inplace=True)

    plot_df = quarter_df.copy()

    # Reorder the columns if necessary
    quarter_df = quarter_df[
        ['Quarter','Name',  'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]
    quarter_df['Opportunity Amount (INR Cr)'] = quarter_df['Opportunity Amount (INR Cr)'].apply(format_inr)

    quarter_df['Order Value (INR Cr)'] = quarter_df['Order Value (INR Cr)'].apply(format_inr)

    quarter_df['Conversion Rate'] = quarter_df['Conversion Rate'].apply(percent_conversion)
    # Convert 'Quarter' column to string
    # Pass only the first 5 rows of the DataFrame to the template


    # Find the latest quarter
    #latest_quarter = quarter_df['Quarter'].max()

    # Filter the DataFrame to include only the data for the latest quarter
    #quarter_df = q_df[q_df['Quarter'] == latest_quarter]


    # Check if the quarter parameter is provided in the URL
    selected_quarter = request.args.get('quarter')

    # If the quarter is not provided, set it to the latest quarter
    if not selected_quarter and not df.empty:
        selected_quarter = quarter_df['Quarter'].iloc[0]

    #selected_name = request.args.get('name')
    if selected_quarter:
        quarter_df = quarter_df[quarter_df['Quarter'] == selected_quarter]
    else:
        quarter_df = quarter_df



    # Line chart for conversion rate with dots and dropdown
    conversion_rate_chart = px.line(plot_df, x='Quarter', y='Conversion Rate', color='Name',
                                    title='Conversion Rate Over Months',
                                    labels={'Name': 'Select Name', 'Conversion Rate': 'Conversion Rate'},
                                    template='plotly_white', markers=True)

    # Line chart for Order Value
    order_value_chart = px.line(plot_df, x='Quarter', y='Order Value (INR Cr)', color='Name',
                                title='Order Value Over Months',
                                labels={'Name': 'Select Name', 'Order Value (INR Cr)': 'Order Value'},
                                template='plotly_white', markers=True)

    # Line chart for Opportunity Amount
    opportunity_chart = px.line(plot_df, x='Quarter', y='Opportunity Amount (INR Cr)', color='Name',
                                title='Opportunity Amount Over Months',
                                labels={'Name': 'Select Name', 'Opportunity Amount (INR Cr)': 'Opportunity Amount'},
                                template='plotly_white', markers=True)

    # Combined bar chart for order value and opportunity amount with dropdown
    combined_chart = go.Figure()

    # Update layout for combined chart
    combined_chart.update_layout(
        title='Combined Chart - Order Value vs Opportunity Amount Over Months',
        xaxis_title='Quarter',
        yaxis_title='Amount (INR Cr)',
        barmode='group'
    )

    layout = {
        'conversion_rate_chart': conversion_rate_chart.to_html(full_html=False),
        'order_value_chart': order_value_chart.to_html(full_html=False),
        'opportunity_chart': opportunity_chart.to_html(full_html=False),
        'combined_chart': combined_chart.to_html(full_html=False),
        'quarter_df': quarter_df.to_html(index=False),
        'quarters': df['Quarter'].unique()
        # Pass unique months for the dropdown menu

    }



    return render_template('quarterly.html',layout=layout)

@app.route('/yearly',methods = ['GET','POST'])
def yearly():
    df = fetch_data()

    rename_column = {'month': 'Month',
                     'deal_pipeline': 'Name',
                     'total_opp_value': 'Opportunity Amount (INR Cr)',
                     'sales_order_total_value': 'Order Value (INR Cr)',
                     'conversion_rate': 'Conversion Rate'}

    df.rename(columns=rename_column, inplace=True)

    df = df[['Month', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]

    df['Date and Time'] = pd.to_datetime(df['Month'], format='%B %Y')

    # Extract year from the 'Date and Time' column
    df['Year'] = df['Date and Time'].dt.year

    # Group by 'Name' and 'Year' and calculate sum of 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', and mean of 'Conversion Rate'
    yearly_summary_df = df.groupby(['Name', 'Year']).agg({
        'Opportunity Amount (INR Cr)': 'sum',
        'Order Value (INR Cr)': 'sum',
        'Conversion Rate': 'mean'
    }).reset_index()

    # Reorder the columns if necessary
    yearly_summary_df = yearly_summary_df[
        ['Year','Name',  'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]

    yearly_summary_df['Opportunity Amount (INR Cr)'] = yearly_summary_df['Opportunity Amount (INR Cr)'].apply(format_inr)

    yearly_summary_df['Order Value (INR Cr)'] = yearly_summary_df['Order Value (INR Cr)'].apply(format_inr)

    yearly_summary_df['Conversion Rate'] = yearly_summary_df['Conversion Rate'].apply(percent_conversion)


    df['Opportunity Amount (INR Cr)'] = df['Opportunity Amount (INR Cr)'].apply(format_inr)

    df['Order Value (INR Cr)'] = df['Order Value (INR Cr)'].apply(format_inr)

    y_mdf = df.copy()

    # Filter by selected year
    unique_years = sorted(df['Year'].unique(), reverse=True)
    selected_year = request.args.get('year', default=unique_years[0], type=int)
    y_mdf = df[df['Year'] == selected_year].copy()  # Use y_mdf for the pivot table creation
    y_mdf['Conversion Rate'] = y_mdf['Conversion Rate'].apply(percent_conversion)
    # Sort y_mdf by 'Date and Time'
    y_mdf.sort_values(by='Date and Time', inplace=True)

    # Create the pivot table from the filtered y_mdf
    pivot_df = y_mdf.pivot_table(index='Name', columns='Month', values='Conversion Rate', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df.index.name = None
    pivot_df.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df.index:
        pivot_df = pivot_df.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df[month] = None

    # Sort the columns of the pivot table based on the sorted month list
    pivot_df = pivot_df.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)

    ##### Pivot table for opportunity value

    # Create the pivot table from the filtered y_mdf
    pivot_df1 = y_mdf.pivot_table(index='Name', columns='Month', values='Opportunity Amount (INR Cr)', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df1.index.name = None
    pivot_df1.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df1.index:
        pivot_df1 = pivot_df1.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df1.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df1[month] = None

    # Sort the columns of the pivot table based on the sorted month list
    pivot_df1 = pivot_df1.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)

    ### pivot table for sales order

    # Create the pivot table from the filtered y_mdf
    pivot_df2 = y_mdf.pivot_table(index='Name', columns='Month', values='Order Value (INR Cr)', aggfunc='first')

    # If you want to remove the names of the index and columns for display purposes, you can do:
    pivot_df2.index.name = None
    pivot_df2.columns.name = None

    # Assuming 'Name' is the value in the index that you want to drop
    if 'Name' in pivot_df2.index:
        pivot_df1 = pivot_df2.drop('Name')

    # Get the list of all months in "January 2024" format for the selected year
    all_months = [f"{calendar.month_name[month]} {selected_year}" for month in range(1, 13)]

    # Convert the month names to datetime objects for sorting
    sorted_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%B %Y'))

    # Iterate over all months and check if each month exists in the pivot table
    for month in sorted_months:
        if month not in pivot_df2.columns:
            # If the month is missing, insert a new column with NaN values
            pivot_df2[month] = None

    # Sort the columns of the pivot table based on the sorted month list
    pivot_df2 = pivot_df2.reindex(sorted(sorted_months, key=lambda x: pd.to_datetime(x, format='%B %Y')), axis=1)

    pivot_df1.fillna('N/A', inplace=True)
    pivot_df.fillna('N/A', inplace=True)
    pivot_df2.fillna('N/A', inplace=True)

    #ye_df = yearly_summary_df.copy()

    ### Testing the data

    yearly_summary_df = yearly_summary_df[['Year','Name','Opportunity Amount (INR Cr)','Order Value (INR Cr)', 'Conversion Rate']]



    unique_years = sorted(df['Year'].unique(), reverse=True)
    selected_year = request.args.get('year', default=unique_years[0], type=int)
    ye_df = yearly_summary_df[yearly_summary_df['Year'] == selected_year].copy()  # Use y_mdf for the pivot table creation


    # Check if the quarter parameter is provided in the URL
    #selected_year = request.args.get('year')

    # If the quarter is not provided, set it to the latest quarter
    #if not selected_year and not yearly_summary_df.empty:
        #selected_year = ye_df['Year'].iloc[0]

    # selected_name = request.args.get('name')
    #if selected_year:
        #ye_df = ye_df[ye_df['Year'] == selected_year]
    #else:
        #ye_df = ye_df


    #print(selected_year)

    # Line chart for conversion rate with dots and dropdown
    conversion_rate_chart = px.line(yearly_summary_df, x='Year', y='Conversion Rate', color='Name',
                                    title='Conversion Rate Over Months',
                                    labels={'Name': 'Select Name', 'Conversion Rate': 'Conversion Rate'},
                                    template='plotly_white', markers=True)

    # Line chart for Order Value
    order_value_chart = px.line(yearly_summary_df, x='Year', y='Order Value (INR Cr)', color='Name',
                                title='Order Value Over Months',
                                labels={'Name': 'Select Name', 'Order Value (INR Cr)': 'Order Value'},
                                template='plotly_white', markers=True)

    # Line chart for Opportunity Amount
    opportunity_chart = px.line(yearly_summary_df, x='Year', y='Opportunity Amount (INR Cr)', color='Name',
                                title='Opportunity Amount Over Months',
                                labels={'Name': 'Select Name', 'Opportunity Amount (INR Cr)': 'Opportunity Amount'},
                                template='plotly_white', markers=True)

    # Combined bar chart for order value and opportunity amount with dropdown
    combined_chart = go.Figure()

    # Update layout for combined chart
    combined_chart.update_layout(
        title='Combined Chart - Order Value vs Opportunity Amount Over Months',
        xaxis_title='Year',
        yaxis_title='Amount (INR Cr)',
        barmode='group'
    )

    layout = {
        'conversion_rate_chart': conversion_rate_chart.to_html(full_html=False),
        'order_value_chart': order_value_chart.to_html(full_html=False),
        'opportunity_chart': opportunity_chart.to_html(full_html=False),
        'combined_chart': combined_chart.to_html(full_html=False),
        'pivot_table': pivot_df.to_html(classes='pivot-table', index=True),
        'pivot_table1': pivot_df1.to_html(classes='pivot-table1', index=True),
        'pivot_table2': pivot_df2.to_html(classes='pivot-table2', index=True),
        'yearly_summary_df': ye_df.to_html(index=False),
        'years': yearly_summary_df['Year'].unique()
        # Pass unique months for the dropdown menu

    }

    return render_template('yearly.html',layout=layout)


@app.route('/yty',methods = ['GET','POST'])
def yty():
    df1 = fetch_data()

    rename_column = {'month': 'Month',
                     'deal_pipeline': 'Name',
                     'total_opp_value': 'Opportunity Amount (INR Cr)',
                     'sales_order_total_value': 'Order Value (INR Cr)',
                     'conversion_rate': 'Conversion Rate'}

    df1.rename(columns=rename_column, inplace=True)

    df1 = df1[['Month', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]

    # Convert 'Month' to datetime
    df1['Date and Time'] = pd.to_datetime(df1['Month'], format='%B %Y')

    # Adjust fiscal year based on the month
    df1['Fiscal Year'] = df1['Date and Time'].apply(
        lambda x: 'FY ' + str(x.year)[-2:] if x.month < 4 else 'FY ' + str(x.year + 1)[-2:])

    df1 = df1[['Fiscal Year', 'Name', 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]




    # Group by 'Name' and 'Fiscal Year' and calculate sum of 'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', and mean of 'Conversion Rate'
    yearly_summary_df1 = df1.groupby(['Name', 'Fiscal Year']).agg({
        'Opportunity Amount (INR Cr)': 'sum',
        'Order Value (INR Cr)': 'sum',
        'Conversion Rate': 'mean'
    }).reset_index()

    # Reorder the columns if necessary
    yearly_summary_df1 = yearly_summary_df1[
        ['Fiscal Year','Name',  'Opportunity Amount (INR Cr)', 'Order Value (INR Cr)', 'Conversion Rate']]

    yearly_summary_df1['Opportunity Amount (INR Cr)'] = yearly_summary_df1['Opportunity Amount (INR Cr)'].apply(format_inr)

    yearly_summary_df1['Order Value (INR Cr)'] = yearly_summary_df1['Order Value (INR Cr)'].apply(format_inr)

    yearly_summary_df1['Conversion Rate'] = yearly_summary_df1 ['Conversion Rate'].apply(percent_conversion)

    ye_df1 = yearly_summary_df1.copy()

    # Check if the quarter parameter is provided in the URL
    selected_year = request.args.get('ytys')

    # If the quarter is not provided, set it to the latest quarter
    if not selected_year and not df1.empty:
        selected_year = ye_df1['Fiscal Year'].iloc[0]

    # selected_name = request.args.get('name')
    if selected_year:
        ye_df1 = ye_df1[ye_df1['Fiscal Year'] == selected_year]
    else:
        ye_df1 = ye_df1

    print(selected_year)

    # Line chart for conversion rate with dots and dropdown
    conversion_rate_chart = px.line(yearly_summary_df1, x='Fiscal Year', y='Conversion Rate', color='Name',
                                    title='Conversion Rate Over Months',
                                    labels={'Name': 'Select Name', 'Conversion Rate': 'Conversion Rate'},
                                    template='plotly_white', markers=True)

    # Line chart for Order Value
    order_value_chart = px.line(yearly_summary_df1, x='Fiscal Year', y='Order Value (INR Cr)', color='Name',
                                title='Order Value Over Months',
                                labels={'Name': 'Select Name', 'Order Value (INR Cr)': 'Order Value'},
                                template='plotly_white', markers=True)

    # Line chart for Opportunity Amount
    opportunity_chart = px.line(yearly_summary_df1, x='Fiscal Year', y='Opportunity Amount (INR Cr)', color='Name',
                                title='Opportunity Amount Over Months',
                                labels={'Name': 'Select Name', 'Opportunity Amount (INR Cr)': 'Opportunity Amount'},
                                template='plotly_white', markers=True)

    # Combined bar chart for order value and opportunity amount with dropdown
    combined_chart = go.Figure()

    # Update layout for combined chart
    combined_chart.update_layout(
        title='Combined Chart - Order Value vs Opportunity Amount Over Months',
        xaxis_title='Fiscal Year',
        yaxis_title='Amount (INR Cr)',
        barmode='group'
    )

    layout = {
        'conversion_rate_chart': conversion_rate_chart.to_html(full_html=False),
        'order_value_chart': order_value_chart.to_html(full_html=False),
        'opportunity_chart': opportunity_chart.to_html(full_html=False),
        'combined_chart': combined_chart.to_html(full_html=False),
        'yearly_summary_df1': ye_df1.to_html(index=False),
        'ytys': yearly_summary_df1['Fiscal Year'].unique()
        # Pass unique months for the dropdown menu

    }



    return render_template('yty.html',layout=layout)



#if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5001)
