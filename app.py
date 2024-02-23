from flask import Flask, render_template, request
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

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


# Define a function to format the numbers
def format_inr(number):
    if number >= 1e7:  # If the number is greater than or equal to 10 million
        return 'INR {:.2f} Cr'.format(number / 1e7)  # Convert to crore
    elif number >= 1e5:  # If the number is greater than or equal to 100 thousand
        return 'INR {:.2f} Lakh'.format(number / 1e5)  # Convert to lakh
    else:
        return 'INR {:.2f}'.format(number)

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

    # Apply the formatting function to the columns containing monetary values
    df['Opportunity Amount (INR Cr)'] = df['Opportunity Amount (INR Cr)'].apply(format_inr)
    df['Order Value (INR Cr)'] = df['Order Value (INR Cr)'].apply(format_inr)

    e_df = df.copy()

    # Handle filtering based on the selected month
    selected_month = request.args.get('month')
    selected_name = request.args.get('name')
    if selected_month:
        df = df[df['Month'] == selected_month]


    # Line chart for conversion rate with dots and dropdown
    conversion_rate_chart = px.line(df, x='Month', y='Conversion Rate', color='Name',
                                    title='Conversion Rate Over Months',
                                    labels={'Name': 'Select Name', 'Conversion Rate': 'Conversion Rate'},
                                    template='plotly_white', markers=True)

    # Line chart for Order Value
    order_value_chart = px.line(df, x='Month', y='Order Value (INR Cr)', color='Name',
                                title='Order Value Over Months',
                                labels={'Name': 'Select Name', 'Order Value (INR Cr)': 'Order Value'},
                                template='plotly_white', markers=True)

    # Line chart for Opportunity Amount
    opportunity_chart = px.line(df, x='Month', y='Opportunity Amount (INR Cr)', color='Name',
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
        'df': e_df.to_html(index=False),
        'months': df['Month'].unique()  # Pass unique months for the dropdown menu
    }

    return render_template('dashboard.html', layout=layout)


#if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5001)
