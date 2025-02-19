import csv
import re
import pandas as pd
from transformers import pipeline
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st
from transformers import AutoTokenizer

# Load pre-trained RoBERTa-based sentiment analysis model from Hugging Face
classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None


# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

def analyze_sentiment(csv_file):
    # Read in the YouTube comments from the CSV file
    comments = []
    sentiment_labels = []
    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comment = row.get('Comment', '')  # Safely get the 'Comment' field
            
            # Ensure the comment is a string and not empty
            if not isinstance(comment, str) or not comment.strip():
                print(f"Skipping invalid comment: {comment}")
                continue
            
            # Add try-except block to handle errors during sentiment classification
            try:
                sentiment = classifier(comment.strip())[0]  # Get sentiment from RoBERTa
                sentiment_score = sentiment['label']
                
                # Classify the sentiment as Positive, Negative, or Neutral based on the model output
                if sentiment_score == 'LABEL_2':  # Positive label
                    sentiment_labels.append('Positive')
                elif sentiment_score == 'LABEL_0':  # Negative label
                    sentiment_labels.append('Negative')
                else:  # Neutral
                    sentiment_labels.append('Neutral')
                
                comments.append(comment)
            except Exception as e:
                print(f"Error processing comment: {comment} - {str(e)}")
                continue

    # Create a DataFrame with the comments and their sentiment labels
    sentiment_df = pd.DataFrame({
        'Comment': comments,
        'Sentiment': sentiment_labels
    })

    # Count the number of each sentiment
    sentiment_counts = sentiment_df['Sentiment'].value_counts()

    # Return the results and the DataFrame
    results = {
        'num_neutral': sentiment_counts.get('Neutral', 0),
        'num_positive': sentiment_counts.get('Positive', 0),
        'num_negative': sentiment_counts.get('Negative', 0),
        'sentiment_df': sentiment_df
    }

    return results


def bar_chart(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Create a Pandas DataFrame with the results
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [num_positive, num_negative, num_neutral]
    })

    # Create the bar chart using Plotly Express
    fig = px.bar(df, x='Sentiment', y='Number of Comments', color='Sentiment', 
                 color_discrete_sequence=['#87CEFA', '#FFA07A', '#D3D3D3'],
                 title='Sentiment Analysis Results')
    fig.update_layout(title_font=dict(size=20))


    # Show the chart
    st.plotly_chart(fig, use_container_width=True)    
    
def plot_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Plot the pie chart
    labels = ['Neutral', 'Positive', 'Negative']
    values = [num_neutral, num_positive, num_negative]
    colors = ['yellow', 'green', 'red']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                 marker=dict(colors=colors))])
    fig.update_layout(title={'text': 'Sentiment Analysis Results', 'font': {'size': 20, 'family': 'Arial', 'color': 'grey'},
                              'x': 0.5, 'y': 0.9},
                      font=dict(size=14))
    st.plotly_chart(fig)
    
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Create scatter plot using Plotly
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')

    # Customize layout
    fig.update_layout(
        title='Scatter Plot',
        xaxis_title=x_column,
        yaxis_title=y_column,
        font=dict(size=18)
    )

    # Display plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def print_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Determine the overall sentiment
    if num_positive > num_negative:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif num_negative > num_positive:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW

    # Print the overall sentiment in color
    print('\n'+ Style.BRIGHT+ color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL)
