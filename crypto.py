import requests
import os
from openai import OpenAI
import json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import base64
from dotenv import load_dotenv


load_dotenv()

class Crypto_Analysis:
    def __init__(self) -> None:
        self.token_url = "https://financialmodelingprep.com/api/v3/symbol/available-cryptocurrencies?apikey=ba164bccb40cdf9d0adc2a9a8cb39060"

    def get_symbol(self, coin_name):
        """Get the symbol for the given coin name"""
        response = requests.get(self.token_url)
        if response.status_code == 200:
            data = response.json()
            for coin in data:
                if coin["name"].lower() == coin_name.lower() + " usd":
                    return coin["symbol"]
        return None

            
    def fundamental_analysis(self, coin_name):
        """Get the fundamental analysis report for the given coin"""
        token = self.get_symbol(coin_name)
        url = f"https://financialmodelingprep.com/api/v3/quote/{token}?apikey=ba164bccb40cdf9d0adc2a9a8cb39060"
        response = requests.get(url)

        data = response.json()
        # Extracting specific fields
        output = {
            "Fundamental_Analysis_Report": {
                "values":{

                "symbol": data[0]["symbol"],
                "name": data[0]["name"],
                "price": data[0]["price"],
                "changesPercentage": data[0]["changesPercentage"],
                "change": data[0]["change"],
                "dayLow": data[0]["dayLow"],
                "dayHigh": data[0]["dayHigh"],
                "yearHigh": data[0]["yearHigh"],
                "yearLow": data[0]["yearLow"],
                "marketCap": data[0]["marketCap"],
                "priceAvg50": data[0]["priceAvg50"],
                "priceAvg200": data[0]["priceAvg200"],
                "volume": data[0]["volume"],
                "avgVolume": data[0]["avgVolume"],
                "open": data[0]["open"],
                "previousClose": data[0]["previousClose"],
                "sharesOutstanding": data[0]["sharesOutstanding"],
                "timestamp": data[0]["timestamp"]
                }
                
            }
        }

        prompt = f"""

        From the provided data write a small and brief summary whether the coin is overvalued or undervalued,
        Dont go into much details just give a understandable reason why it is overalued or undervalued or neither.
        {output}



        """

        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content


            output = {
            "Fundamental Analysis Report": {
                "values":{

                "symbol": data[0]["symbol"],
                "name": data[0]["name"],
                "price": data[0]["price"],
                "changesPercentage": data[0]["changesPercentage"],
                "change": data[0]["change"],
                "dayLow": data[0]["dayLow"],
                "dayHigh": data[0]["dayHigh"],
                "yearHigh": data[0]["yearHigh"],
                "yearLow": data[0]["yearLow"],
                "marketCap": data[0]["marketCap"],
                "priceAvg50": data[0]["priceAvg50"],
                "priceAvg200": data[0]["priceAvg200"],
                "volume": data[0]["volume"],
                "avgVolume": data[0]["avgVolume"],
                "open": data[0]["open"],
                "previousClose": data[0]["previousClose"],
                "sharesOutstanding": data[0]["sharesOutstanding"],
                "timestamp": data[0]["timestamp"]
                },

            "Summary": content
                
            }
        }

            

            
                    
        except Exception as e:
            print(f"Error processing LLM request: {e}")

        with open("formatted_output.json", "w") as json_file:
            json.dump(output, json_file, indent=4)

       

    def write_json(self, output):
        """Write the output to a JSON file for sentimental analysis"""

        # Parsing the output to match the desired JSON structure
        top_stories = []
        latest_stories = []
        # Split the output by sections
        
        sections = output.split("\n\n")
        current_section = None
        for section in sections:
            if "Top Stories:" in section:
                current_section = top_stories
            elif "Latest Stories:" in section:
                current_section = latest_stories
            elif "Summary:" in section:
                summary = section.replace("Summary:", "").strip()
            elif current_section is not None:
                # Split the section into title and text
                lines = section.split("\n")
                if len(lines) >= 2:
                    title = lines[0].replace("Title: ", "").strip()
                    text = lines[1].replace("Text: ", "").strip()
                    current_section.append({"Title": title, "Text": text})
        # Create the JSON structure
        sentimental_analysis = {
            "Sentimental_Analysis_Report": {
                "Top_Stories": top_stories,
                "Latest_Stories": latest_stories,
                "Summary" : summary
            }
        }
        # Write the JSON data to a file
        with open("sentimental_analysis.json", "w") as json_file:
            json.dump(sentimental_analysis, json_file, indent=4)

  
    def sentiment_analysis(self,coin_name):
        """Get the sentiment analysis report for the given coin"""

        token = self.get_symbol(coin_name)
        url = f"https://financialmodelingprep.com/api/v4/crypto_news?page=1&symbol={token}&apikey=ba164bccb40cdf9d0adc2a9a8cb39060"
        response = requests.get(url)

    
        if response.status_code == 200:  
            data = response.json()
            top_items = data[:10]
            combined_list = []
    
        for item in top_items:
        
            title = item.get('title', 'No Title Found')
            text = item.get('text', 'No Text Found')

            # Combine title and text into one string
            combined = f"Title: {title}\nText: {text}"

            # Append the combined string to the list
            combined_list.append(combined)


        prompt = f"""
        Mention the 3 top stories of the coin from the content provided plus 3 latest stories too.
        The output should be in this format:

        Top Stories:

          Title:
          Text:

        Latest Stories:

          Title:
          Text:

        Provide a summary of the key points from the extracted content.
        and evaluate the overall sentiment of the news articles. Indicate whether the sentiment is neutral, negative, or positive.
        Dont go into details just finish it in 2 to 3 lines maximum.

        Summary:


        {combined_list}
        
    """


        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            output = response.choices[0].message.content
            self.write_json(output)

            
                    
        except Exception as e:
            print(f"Error processing LLM request: {e}")


    def create_line_chart(self, coin_name):
        token = self.get_symbol(coin_name)
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{token}?apikey=ba164bccb40cdf9d0adc2a9a8cb39060"
        response = requests.get(url)
        if response.status_code == 200:
            historical_data = response.json()['historical']
            df_historical = pd.DataFrame(historical_data)
            df_historical['date'] = pd.to_datetime(df_historical['date'])
            df_historical.set_index('date', inplace=True)
            df_historical = df_historical.sort_index()  # Ensure data is sorted by date
            df_historical = df_historical[-30:]
            plt.figure(figsize=(12, 6))
            plt.plot(df_historical.index, df_historical['close'], color='green', linewidth=2)

            # Format the date on the x-axis
            date_form = DateFormatter("%Y-%m-%d")
            plt.gca().xaxis.set_major_formatter(date_form)
            plt.gca().xaxis.set_tick_params(rotation=45)

            # Set plot labels and title
            plt.xlabel('Date')
            plt.ylabel('Closing Price (USD)')
            plt.title(f'{token}/USD Closing Prices (Last 30 Days)')

            # Show plot
            plt.grid(True)
            plt.tight_layout()
            plt.savefig("line_chart.jpeg")
        else:
            raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")
        
    def create_sma_chart(self, coin_name):
        token = self.get_symbol(coin_name)
        url = f"https://financialmodelingprep.com/api/v3/technical_indicator/1day/{token}?type=sma&period=5&apikey=ba164bccb40cdf9d0adc2a9a8cb39060"
        technical_indicator_name = "sma"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df = df[:30]
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

                # Plot the data
            plt.figure(figsize=(14, 7))

            plt.plot(df.index, df['close'], label='Close Price', color='blue')
            
            if technical_indicator_name in df.columns:
                plt.plot(df.index, df[technical_indicator_name], label=f'{technical_indicator_name.upper()} (5)', color='orange')
            else:
                print(f"{technical_indicator_name.upper()} data not available.")
                exit()

            plt.title(f'last 1 month Closing Prices of {token}/USD and {technical_indicator_name.upper()} (5-day)')
            plt.xlabel('Date')
            plt.ylabel('Price (USD)')
            plt.legend()
            plt.grid(True)
            plt.savefig("sma.jpeg")

        else:
            raise Exception(f"Error fetching data: {response.status_code}")


    def save_analysis_to_json(self, content):
        """Save the technincal analysis to a JSON file"""
        
        # Split the content into sections based on the headings
        sections = content.split('\n\n')
        
        # Parsing the response content into the appropriate sections
        for section in sections:
            if "Current Trend:" in section:
                trend = section.replace("Current Trend:", "").strip()
            
            elif "Trend Strength and Potential Reversal Points:" in section:
                trend_strength = section.replace("Trend Strength and Potential Reversal Points:", "").strip()
            
            elif "Candlestick Patterns:" in section:
                pattern = section.replace("Candlestick Patterns:", "").strip()
                
            elif "Volume Analysis:" in section:
                volume = section.replace("Volume Analysis:", "").strip()

            elif "Unusual Volume Spikes:" in section:
                spike = section.replace("Unusual Volume Spikes:", "").strip()

            elif "Insights on Potential Bullish or Bearish Signals:" in section:
                insight = section.replace("Insights on Potential Bullish or Bearish Signals:", "").strip()

            elif "Risk Assessment:" in section:
                risk = section.replace("Risk Assessment", "").strip()

            elif "Technical Indicators:" in section:
                tech = section.replace("Technical Indicators:", "").strip()


        
        analysis_report = {
            "Technical_Analysis_Report": {
                "Current_Trend": trend,
                "Trend_Strength_and_Potential_Reversal_Points": trend_strength,
                "Candlestick_Patterns": pattern,
                "Volume_Analysis":  volume,
                "Unusual_Volume_Spikes": spike,
                "Insights_on_Potential_Bullish_or_Bearish_Signals": insight,
                "Risk_Assessment": risk,
                "Technical_Indicator:": tech
            }
        }

        # Save the structured report to a JSON file
        with open('candlestick_analysis_report.json', 'w') as json_file:
            json.dump(analysis_report, json_file, indent=4)
    
    def technical_analysis(self):
        """Get the technical analysis report for the given coin"""
        image_path = "coin_screenshot.jpeg"  
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


        with open(image_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        

        response = client.chat.completions.create(
        model='gpt-4o',
        response_format={"type": "text"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text":
                    """
                    You are an expert in analyzing candlestick charts and provide a detailed and accurate report from the provided images,
                    provide the content in one line for each heading, dont go into points.

                        Current Trend:
                        Identify whether the market is in an uptrend, downtrend, or moving sideways. This can be done by observing the direction of the price movement over time.

                        Trend Strength and Potential Reversal Points:
                        Evaluate the strength of the current trend and identify any potential reversal points.

                        Candlestick Patterns:
                        Analyze the presence of candlestick patterns in the market. These patterns can include:
                        Doji: Indicates indecision in the market, potential reversal signal.
                        Hammer: Bullish reversal pattern after a downtrend.
                        Engulfing Patterns: Bullish or bearish, indicating strong reversal potential.

                        Volume Analysis:
                        Analyze the volume of trading activity in the market. This can help identify trends and potential trading opportunities.
                        Confirm price movements with corresponding volume. An increase in volume confirms the strength of the price movement.
                        
                        Unusual Volume Spikes:
                        Identify significant volume spikes which can indicate strong buying/selling pressure and potential trend changes.

                        Insights on Potential Bullish or Bearish Signals:
                        Bullish patterns suggest potential buying opportunities.
                        Bearish patterns suggest potential selling opportunities.

                        Risk Assessment:
                        Identify levels for stop-loss orders to manage downside risk.
                        Suggest appropriate position sizing based on volatility and risk tolerance.

                        Technical Indicators:
                        Just provide with one word by analyzing all the above points and from the candlestick chart if the one should sell, strong sell, neutral, buy or strong buy.
                    


                    By following this framework, you can systematically analyze a candlestick chart and derive actionable insights for trading decisions.
                    """
                        },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=800,
    )

        self.save_analysis_to_json(response.choices[0].message.content)
    

    def moving_average(self):
        """Get the moving average report for the given coin"""

        image_path = "sma.jpeg"  
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


        with open(image_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        

        response = client.chat.completions.create(
        model='gpt-4o',
        response_format={"type": "text"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text":
                    """
                    Please analyze the following image of a cryptocurrency moving average chart and provide a detailed summary
                    by calculating the the n-day MA from picture and the current trend. Also mention any crossovers.
                    Write the output below the Summary heading with no new line include everything in a single paragraph including the crossover part.  
                    
                    Summary:


                    Also calculate the status whether one should buy sell, strong buy, strong sell or neutral.
                    Give one word answer only dont go into details

                    Status:

                    
                    Review the image carefully and provide a comprehensive report.

                    """
                        },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=800,
    )


        output = response.choices[0].message.content
    
        sections = output.split('\n\n')

        for section in sections:
            if 'Summary:' in section:
                summary = section.replace('Summary:', '').strip()
            elif 'Status:' in section:
                status = section.replace('Status:', '').strip()
        
        moving_average = {
            "Moving_Average_Analysis_Report": {
                "Summary": summary,
                "Status": status
            }
        }
         
        with open('moving_average.json', 'w') as json_file:
            json.dump(moving_average, json_file, indent=4)
        

    def closing_chart_analysis(self):
        """Get the five values from the line chat of the given coin"""
        image_path = "line_chart.jpeg"  
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


        with open(image_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        

        response = client.chat.completions.create(
        model='gpt-4o',
        response_format={"type": "text"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text":
                    """
                    Analyze the line chart of the specified cryptocurrency. The analysis should focus on identifying key price points. The output should be provided like the format below.
                    You are an expert in analyzing line charts adn getting the following values for each price point.
                    Ouput should be in this format, just provide the value, no wording or any other text:
                    
                    Support Price: <value>
                    Consolidation Points Price: <value>
                    Major Resistance Price: <value>
                    Psychological Break Price: <value>
                    Immediate Resistance: <value>
                    
                    
                

                    Replace `<value>` with the respective price points identified from the analysis. Ensure that each key is clearly defined and corresponds to the correct price point on the chart.
            
            

                    """
                        },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=800,
    )
        
        output = response.choices[0].message.content
        print(output)
        sections = output.split('\n')

        support_price = ''
        consolidation_points_price= ''
        major_resistance_price = ''
        psychological_break_price = ''
        immediate_resistance= ''
        
        for section in sections:
            if 'Support Price:' in section:
                support_price = section.replace('Support Price:', '').strip()
            elif 'Consolidation Points Price:' in section:
                consolidation_points_price = section.replace('Consolidation Points Price:', '').strip()
            elif 'Major Resistance Price:' in section:
                major_resistance_price = section.replace('Major Resistance Price:', '').strip()
            elif 'Psychological Break Price:' in section:
                psychological_break_price = section.replace('Psychological Break Price:', '').strip()
            elif 'Immediate Resistance:' in section:
                immediate_resistance = section.replace('Immediate Resistance:', '').strip()


        line_chart = {
            "Line_Chart_Analysis_Report": {
                "Support_Price": support_price,
                "Consolidation_Points_Price": consolidation_points_price,
                "Major_Resistance_Price": major_resistance_price,
                "Psychological_Break_Price": psychological_break_price,
                "Immediate_Resistance": immediate_resistance
            }
        }
         
        with open('line_chart.json', 'w') as json_file:
            json.dump(line_chart, json_file, indent=4)


    def generate_summary(self):
        """Generate a overall summary for the given coin"""

        with open("formatted_output.json", "r") as json_file:
            data1 = json.load(json_file)

        with open("candlestick_analysis_report.json", "r") as json_file:
            data2= json.load(json_file)

        with open("sentimental_analysis.json", "r") as json_file:
            data3 = json.load(json_file)

        with open("moving_average.json", "r") as json_file:
            data4 = json.load(json_file)

        with open("line_chart.json", "r") as json_file:
            data5 = json.load(json_file)


        data = {**data1, **data2, **data3, **data4, **data5}


        prompt = f"""
        You are an expert in generating summaries from the given data.
        provide a 10 lines paragraph summary of the data. Provide a deatailed summary.


        Also tell what can be the status from the overall summary whether one should buy, sell, strong sell, string buy or neutral

        The output format should be like this:

        Summary:
        Status:

        =========
        {data}
        ==========
        """

                            
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                    {
                    "role": "user",
                    "content": prompt
                    }
                ]
        )
        
        output = response.choices[0].message.content

        sections = output.split('\n\n')
        sum = ""
        status = ""
        
        # Parsing the response content into the appropriate sections
        for section in sections:
            if "Summary:" in section:
                sum = section.replace("Summary:", "").strip()
            
            elif "Status:" in section:
                status = section.replace("Status:", "").strip()

        overall_summary = {
            "Overall_Summary_Report": {
                "Summary": sum,
                "Status": status
            }
        }

        answer = {**data, **overall_summary}
        with open("summary.json", "w") as json_file:
            json.dump(answer, json_file, indent=4)






#         token = self.get_symbol(coin_name)
#         url = f"https://financialmodelingprep.com/api/v3/technical_indicator/1day/{token}?type=sma&period=5&apikey=ba164bccb40cdf9d0adc2a9a8cb39060"
#         technical_indicator_name = "sma"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             df = pd.DataFrame(data)
#             df = df[:30]
#             df['date'] = pd.to_datetime(df['date'])
#             df.set_index('date', inplace=True)

#                 # Plot the data
#             plt.figure(figsize=(14, 7))

#             plt.plot(df.index, df['close'], label='Close Price', color='blue')
            
#             if technical_indicator_name in df.columns:
#                 plt.plot(df.index, df[technical_indicator_name], label=f'{technical_indicator_name.upper()} (5)', color='orange')
#             else:
#                 print(f"{technical_indicator_name.upper()} data not available.")
#                 exit()

#             plt.title(f'last 1 month Closing Prices of {token}/USD and {technical_indicator_name.upper()} (5-day)')
#             plt.xlabel('Date')
#             plt.ylabel('Price (USD)')
#             plt.legend()
#             plt.grid(True)
#             plt.savefig("sma.jpeg")

#         else:
#             raise Exception(f"Error fetching data: {response.status_code}")