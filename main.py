import os
import configargparse
import pandas as pd
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import defaultdict
from datetime import datetime

def load_data(file_path):
    df = pd.read_excel(file_path)
    df = df.where(pd.notna(df), None)
    return df

def organize_wine_data(df):
    wine_collection = defaultdict(list)
    for _, row in df.iterrows():
        category = row["Категория"]
        wine_info = {
            "Название": row["Название"],
            "Сорт": row["Сорт"],
            "Цена": row["Цена"],
            "Картинка": row["Картинка"],
            "Акция": row["Акция"],
        }
        wine_collection[category].append(wine_info)
        
    return wine_collection


def get_year_word(number):
    if 11 <= number % 100 <= 19:
        return "лет"
    last_digit = number % 10
    if last_digit == 1:
        return "год"
    if 2 <= last_digit <= 4:
        return "года"
    return "лет"

def calculate_winery_age(founding_year=1920):
    current_year = datetime.now().year
    return current_year - founding_year

def render_html(wine_dict, years):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('./static/template.html')
    formatted_years = f"{years} {get_year_word(years)}"
    
    return template.render(
        years_since_foundation=formatted_years,
        wine_categories=dict(wine_dict)
    )

def save_html(content, filename='./static/index.html'):
    with open(filename, 'w', encoding="utf8") as file:
        file.write(content)

def run_server():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

def main():
    parser = configargparse.ArgumentParser(description="Wine catalog web server")
    parser.add("--data", type=str, default=os.getenv("WINE_DATA_FILE", "wine_guide.xlsx"),
               help="Path to the data file (Excel), can be set via env WINE_DATA_FILE")
    args = parser.parse_args()
    
    df = load_data(args.data)
    wine_collection = organize_wine_data(df)
    
    
    winery_age = calculate_winery_age()
    
    
    rendered_page = render_html(wine_collection, winery_age)
    save_html(rendered_page)
    run_server()

if __name__ == "__main__":
    main()