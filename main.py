#!/bin/python3

# libraries
from sqlalchemy import create_engine
from decouple import config
import src.find_apartment

# db
engine = create_engine(
    "sqlite:////home/eliasy/project_repositories/find_apartment/apartments.sqlite",
    echo=True,
)

# Examples:
# bairro="/apartamento_residencial/"
# filtro="#area-desde=60&preco-ate=2400&preco-desde=1000&preco-total=sim&vagas=1&ordenar-por=preco-total:ASC"
bairro = config("bairro")
filtro = config("filtro")

if __name__ == "__main__":
    # scrapping and map creation
    print("Initializing script...")
    src.find_apartment.scrape_properties(bairro, filtro, engine)
    src.find_apartment.gen_map(engine, "./apartments_map.html")
