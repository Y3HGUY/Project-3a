import os
import pygal
import requests
import csv
from datetime import datetime
from flask import Flask, render_template, url_for

# Flask app initialization
app = Flask(__name__)

# Set API KEY for Alpha Vantage
#Static folder will get the SVG which is then uploaded to the html page
API_KEY = "GCBNV7ZGRCPKN9BE"
STATICFOLD = os.path.join(os.getcwd(), 'static')

#read csv file to load stock symbols
def load_symbols():
    symbols = []
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbols.append(row['Symbol'])
        return symbols

# Retrieve stock data from Alpha Vantage function
def retrieve_stock_data(stock_symbol, time_function, start_date, end_date):
    try:
        print(f"Retrieving data for {stock_symbol} from {start_date} to {end_date}")
        start_date_input = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_input = datetime.strptime(end_date, "%Y-%m-%d")


        if end_date_input < start_date_input:
            raise ValueError("Start date must be before end date.")
    except ValueError as e:
        print(f"Error in date input: {e}")
        return None

    # Build URL for Alpha Vantage API
    url = (f"https://www.alphavantage.co/query?function={time_function}"
           f"&symbol={stock_symbol}&apikey={API_KEY}&outputsize=full&datatype=json")
    print(f"API URL: {url}")
    api_response = requests.get(url)

    if api_response.status_code == 200:
        stock_data = api_response.json()
        time_type = {
            "TIME_SERIES_DAILY": "Time Series (Daily)",
            "TIME_SERIES_WEEKLY": "Weekly Time Series",
            "TIME_SERIES_MONTHLY": "Monthly Time Series"
        }.get(time_function)

        if not time_type:
            print("Time function not supported.")
            return None

        time_series_data = stock_data.get(time_type, {})
        date_range_data = {date: values for date, values in time_series_data.items()
                           if start_date <= date <= end_date}

        if not date_range_data:
            print(f"No data found between {start_date} and {end_date}.")
            return None


        print(f"Retrieved {len(date_range_data)} records.")
        return date_range_data
    else:
        print(f"Failed to retrieve data. HTTP Code: {api_response.status_code}")
        return None

# Function which generates the chart and saves to the static folder 
def generate_chart(data, chart_type, stock_symbol):
    print(f"Generating {chart_type} chart for {stock_symbol}")
    chart = pygal.Bar(title=f"{stock_symbol} Stock Prices") if chart_type == "1" else pygal.Line(title=f"{stock_symbol} Stock Prices")
    dates = sorted(data.keys())
    closing_prices = [float(data[date]['4. close']) for date in dates]

    chart.x_labels = dates
    chart.add(stock_symbol, closing_prices)

    # This it the path for saving the chart (SVG) to the static folder
    chart_file = os.path.join(STATICFOLD, f"{stock_symbol}_stock_chart.svg")



    # Guarantee/confirm that the static folder exists
    if not os.path.exists(STATICFOLD):
        os.makedirs(STATICFOLD)
        print(f"Created static folder: {STATICFOLD}")
        

    print(f"Saving chart to {chart_file}")
    chart.render_to_file(chart_file)
    return chart_file

# add index 
@app.route('/')
def index():
    symbols = load_symbols()
    return render_template('index.html',symbols=symbols)

# Flask route connection to chart
#route to generate and display chart
@app.route('/generate_chart', methods=['POST'])
def generate_chart_route():
    stock_symbol = requests.form['stock_symbol']
    chart_type =  requests.form['chart_type']
    time_series =  requests.form['time_series']
    start_date =  requests.form['start_date']
    end_date =  requests.form['end_date']
    
    # now change to route to web 
    # Retrieve stock data and generate the chart
    print("Retrieving stock data for chart generation...")
    stock_data = retrieve_stock_data(stock_symbol, time_series, start_date, end_date)
    if stock_data:
        chart_path = generate_chart(stock_data, chart_type, stock_symbol)
        chart_url = url_for('static', filename=os.path.basename(chart_path))
        print(f"Chart URL for HTML: {chart_url}")
        return render_template('graphing.html', chart_data=chart_url, stock_symbol=stock_symbol)
    else:
        return "No data available for the given stock symbol and date range."


if __name__ == "__main__":
    print("starting the Stock Data visualizer")
    app.run(host="0.0.0.0")