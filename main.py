import urllib.request
import requests
import pandas as pd
import numpy as np
import functions
import re
from geopy import Nominatim
from geopy import GoogleV3
import googlemaps
from sqlalchemy import create_engine
from time import sleep
import folium
import datetime
from decouple import config

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import ChromeOptions
from selenium.webdriver import FirefoxOptions

# db
engine = create_engine(
    "sqlite:////home/eliasy/project_repositories/find_apartment/apartments.sqlite",
    echo=True,
)

bairro = "/apartamento_residencial/"
filtro = (
    "#area-desde=60&preco-ate=2400&preco-desde=1000"
    + "&preco-total=sim&vagas=1&ordenar-por=preco-total:ASC"
)
temp = functions.get_results(bairro, filtro)
temp = pd.DataFrame(temp)
temp = temp.sort_values(by=["endereco"], axis=0)

# filter results already in the db
with engine.connect() as conn:
    apartment_links = pd.read_sql(
        "select link, endereco, lat, lon from apartments", conn
    )
type(apartment_links)
len(apartment_links)

key = temp.link.isin(apartment_links.link)
temp = temp.loc[~key, :]

# adiciona lat/lon de enderecos conhecidos
unique_adresses = apartment_links.loc[:, ["endereco", "lat", "lon"]].drop_duplicates()
temp = pd.merge(temp, unique_adresses, how="left", on="endereco")
temp.shape
temp.info()

## Address

# Geocoding an address
key = temp.lat.isna()
search_addresses = temp.loc[key, ["endereco"]].drop_duplicates()
# check
search_addresses.shape
search_addresses.endereco.isin(apartment_links.endereco).describe()

# Uses google geocoding API
gmaps = googlemaps.Client(key=config("google_key"))

geocode_entries = {}
dt_geocode = []
for i, entry in search_addresses.iterrows():
    print("Buscando endereco: {}".format(i))
    endereco = entry["endereco"]
    geocode_result = gmaps.geocode(endereco)
    geocode_entries[i] = {"query": endereco, "result": geocode_result}
    dt_geocode.append(
        {
            "endereco": endereco,
            "lat": geocode_result[0].get("geometry").get("location").get("lat"),
            "lon": geocode_result[0].get("geometry").get("location").get("lng"),
        }
    )
    sleep(0.05)

dt_geocode = pd.DataFrame(dt_geocode)
dt_geocode.info()

temp = (
    pd.merge(temp, dt_geocode, how="left", on=["endereco"])
    .assign(
        lat_x=lambda x: x.lat_x.fillna(x["lat_y"]),
        lon_x=lambda x: x.lon_x.fillna(x["lon_y"]),
    )
    .rename(columns={"lat_x": "lat", "lon_x": "lon"})
    .drop(["lat_y", "lon_y"], axis=1)
)

# add datetime and status
temp = temp.assign(date=datetime.datetime.now(), status="new")
temp.head()
temp.info()

# change all previous status to old
engine.connect().execute("UPDATE apartments SET status = 'old';")

# Save results on sqlite db
with engine.connect() as conn:
    temp.to_sql("apartments", conn, if_exists="append", index=False)

# get results from sqlite db
with engine.connect() as conn:
    apartments = pd.read_sql("select * from apartments where status ='new'", conn)

# apartments = temp
apartments = apartments.assign(
    cluster=lambda x: x.groupby("endereco").ngroup(),
    entries_by_cluster=lambda x: x.loc[:, ["status", "endereco"]]
    .groupby("endereco")
    .transform("count"),
    lat=lambda x: functions.randomize_location(x, "lat"),
    lon=lambda x: functions.randomize_location(x, "lon"),
    preco_tot=lambda x: (
        (
            x.aluguel.str.replace("[^0-9]", "")
            .replace("", "0")
            .replace(np.nan, "0")
            .astype("float64")
        )
        + (
            x.cond.str.replace("[^0-9]", "")
            .replace("", "0")
            .replace(np.nan, "0")
            .astype("float64")
        )
    ),
)
apartments.shape
apartments.info()

key = (
    (apartments.preco_tot > 0)
    & (apartments.preco_tot < 2400)
    & (apartments.area.replace("[^0-9]", "", regex=True).astype("float64") > 110)
)
apartments = apartments.loc[key, :]

apartments = [
    functions.Apartment(**entry.to_dict()) for _, entry in apartments.iterrows()
]

##### Map

functions.create_map(apartments)
create_map(apartments)
