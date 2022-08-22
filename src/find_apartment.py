from decouple import config
from ipyleaflet import AwesomeIcon, Map, Marker
from ipywidgets import HTML
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import bs4
import datetime
import folium
import googlemaps
import ipyleaflet
import numpy as np
import pandas as pd
import re


def find_clean_entry(link, entry):
    string_value = link.find_all(attrs={entry})
    if string_value:
        string_value = string_value[0].text
        string_value = string_value.replace("\n", "")
        string_value = re.sub("\\s+", " ", string_value)
        string_value = re.sub("\\s+$|^\\s+", "", string_value)
        return string_value
    else:
        return None


def apartment_parser(link):
    ap = {
        "endereco": find_clean_entry(link, "property-card__address"),
        "aluguel": find_clean_entry(link, "property-card__price"),
        "cond": find_clean_entry(link, "js-condo-price"),
        "vagas": find_clean_entry(link, "property-card__detail-garage"),
        "banheiros": find_clean_entry(link, "property-card__detail-bathroom"),
        "quartos": find_clean_entry(link, "property-card__detail-room"),
        "area": find_clean_entry(link, "property-card__detail-area"),
        "amenidades": ", ".join(
            [i.text for i in link.find_all(attrs={"amenities__item"})]
        ),
        "link": (
            "https://www.vivareal.com.br"
            + link.find_all(attrs={"js-listing-labels-link"})[0].get("href")
        ),
    }
    return ap


def get_results(bairro, filtro):
    main_site = "https://www.vivareal.com.br/aluguel/sp/campinas/"
    button_next_page = '//button[@class="js-change-page" and @title="Próxima página"]'
    url = main_site + bairro + "/" + filtro
    browser = webdriver.Firefox()
    browser.get(url)
    sleep(3)
    aps_list = []
    next_page = False
    count = 1
    # extra timer for page to load
    sleep(1)
    while not next_page:
        print("Scrapping page: " + str(count))
        # next_page = re.sub("#", "?", next_page)
        # url = main_site + bairro + "/" + next_page + filtro
        # print(url)
        # browser.get(url)
        # browser.find_element(By.XPATH, button_next_page).click()
        # find button for next page to be loaded
        # extra timer for page to load
        sleep(2)
        # browser.find_element(By.XPATH, button_next_page).click()
        # element.click()
        # scrap housing info
        html = browser.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")
        links = soup.find_all(attrs={"property-card__container"})
        for entry in links:
            aps_list.append(apartment_parser(entry))
        # check next page
        paginas = soup.find_all(attrs={"pagination__item"})
        next_page = paginas[-1].find("button").has_attr("data-disabled")
        # click on next page
        element = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, button_next_page))
        )
        browser.execute_script("arguments[0].click();", element)
        count = count + 1
    browser.close()
    return aps_list


def randomize_location(x, coord):
    conditions = [
        ((x.entries_by_cluster > 1) & (x.entries_by_cluster < 5)),
        (x.entries_by_cluster > 5),
        (x.entries_by_cluster == 1),
    ]
    choices = [
        x[coord] + np.random.normal(0, 0.0001, x.shape[0]),
        x[coord] + np.random.normal(0, 0.0005, x.shape[0]),
        x[coord],
    ]
    return np.select(conditions, choices)


def addApartment(map_, a):
    popup = folium.Popup(a._popup_(), max_width=450)
    folium.Marker(
        location=[a.lat, a.lon],
        popup=popup,
        # I can use fontawesome to change the pin icon
        icon=folium.Icon(color="green", prefix="fa"),
    ).add_to(map_)


class Apartment:
    def __init__(self, **kwargs):
        self.endereco = kwargs.get("endereco")
        self.aluguel = kwargs.get("aluguel")
        self.cond = kwargs.get("cond")
        self.vagas = kwargs.get("vagas")
        self.banheiros = kwargs.get("banheiros")
        self.quartos = kwargs.get("quartos")
        self.area = kwargs.get("area")
        self.amenidades = kwargs.get("amenidades")
        self.link = kwargs.get("link")
        self.id_address = kwargs.get("id")
        self.lat = kwargs.get("lat")
        self.lon = kwargs.get("lon")
        self.cluster = kwargs.get("cluster")

    def _popup_(self):
        return f"""
        <h4>Info</h4>
        <b>Endereco:</b>      {self.endereco}<br>
        <b>Aluguel:</b>       {self.aluguel}<br>
        <b>Cond:</b>          {self.cond}<br>
        <b>Vagas:</b>         {self.vagas}<br>
        <b>Banheiros:</b>     {self.banheiros}<br>
        <b>Quartos:</b>       {self.quartos}<br>
        <b>Area:</b>          {self.area}<br>
        <b>Amenidades:</b>    {self.amenidades}<br>
        <b>Id_address:</b>    {self.id_address}<br>
        <b>Lat:</b>           {self.lat}<br>
        <b>Lon:</b>           {self.lon}<br>
        <a href="{self.link}" target="_blank">Link</a><br>
        """


def create_map(apartments, filename):
    cps_coords = [-22.8923728, -47.2079813]
    map_ = folium.Map(location=cps_coords, zoom_start=10)

    interesting_coords = [-22.914183, -47.063295]

    # add central marker
    marker1 = folium.Marker(
        location=interesting_coords,
        popup="Point of interest",
        # don't use single quotes, only double quotes
        icon=folium.Icon(name="circle", color="red", icon_color="black"),
    )
    marker1.add_to(map_)

    # add circles at central point
    folium.Circle(
        location=interesting_coords, radius=5000, color="green", opacity=0.5, weight=2
    ).add_to(map_)
    folium.Circle(
        location=interesting_coords, radius=10000, color="yellow", opacity=0.5, weight=2
    ).add_to(map_)
    folium.Circle(
        location=interesting_coords, radius=15000, color="orange", opacity=0.5, weight=2
    ).add_to(map_)
    folium.Circle(
        location=interesting_coords, radius=20000, color="red", opacity=0.5, weight=2
    ).add_to(map_)

    # add apartments
    for entry in apartments:
        addApartment(map_, entry)

    # save map
    map_.save(filename)


def create_map_ipyleaflet(apartments):
    cps_coords = [-22.8923728, -47.2079813]
    map_ = Map(center=cps_coords)

    interesting_coords = [-22.9174636, -47.0597494]

    # add central marker
    marker1 = Marker(
        location=interesting_coords,
        popup=HTML(value="Point of interest"),
        # don't use single quotes, only double quotes
        icon=AwesomeIcon(name="circle", marker_color="red", icon_color="black"),
    )
    map_.add_layer(marker1)

    # add circles at central point
    ipyleaflet.Circle(
        location=interesting_coords, radius=5000, color="green", opacity=0.5, weight=2
    ).add_to(map_)
    ipyleaflet.Circle(
        location=interesting_coords, radius=10000, color="yellow", opacity=0.5, weight=2
    ).add_to(map_)
    ipyleaflet.Circle(
        location=interesting_coords, radius=15000, color="orange", opacity=0.5, weight=2
    ).add_to(map_)
    ipyleaflet.Circle(
        location=interesting_coords, radius=20000, color="red", opacity=0.5, weight=2
    ).add_to(map_)

    # add apartments
    for entry in apartments:
        addApartment(map_, entry)

    # save map
    map_.save("map.html")


def scrape_properties(bairro, filtro, engine):
    new_property = get_results(bairro, filtro)
    new_property = pd.DataFrame(new_property)
    new_property = new_property.sort_values(by=["endereco"], axis=0)

    # filter results already in the db
    with engine.connect() as conn:
        apartment_links = pd.read_sql(
            "select link, endereco, lat, lon from apartments", conn
        )
    type(apartment_links)
    len(apartment_links)

    key = new_property.link.isin(apartment_links.link)
    new_property = new_property.loc[~key, :]

    # add lat/lon of known addresses
    unique_adresses = apartment_links.loc[
        :, ["endereco", "lat", "lon"]
    ].drop_duplicates()
    new_property = pd.merge(new_property, unique_adresses, how="left", on="endereco")
    # checks
    print(new_property.shape)
    print(new_property.info())

    # Address
    # Geocoding an address
    key = new_property.lat.isna()
    search_addresses = new_property.loc[key, ["endereco"]].drop_duplicates()

    # checks
    print("Address shape: ")
    print(search_addresses.shape)
    print("How many addresses are already on the database: ")
    print(search_addresses.endereco.isin(apartment_links.endereco).describe())

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
    # checks
    print("Google Maps geocoding info: ")
    print(dt_geocode.info())

    new_property = (
        pd.merge(new_property, dt_geocode, how="left", on=["endereco"])
        .assign(
            lat_x=lambda x: x.lat_x.fillna(x["lat_y"]),
            lon_x=lambda x: x.lon_x.fillna(x["lon_y"]),
        )
        .rename(columns={"lat_x": "lat", "lon_x": "lon"})
        .drop(["lat_y", "lon_y"], axis=1)
    )

    # add datetime and status
    new_property = new_property.assign(date=datetime.datetime.now(), status="new")
    print("Final dataset head: ")
    new_property.head()
    print("Final dataset info: ")
    new_property.info()

    # change all previous status to old
    print("Updating dataset...")
    engine.connect().execute("UPDATE apartments SET status = 'old';")

    # Save results on sqlite db
    print("Saving new results...")
    with engine.connect() as conn:
        new_property.to_sql("apartments", conn, if_exists="append", index=False)


def gen_map(engine, filename):
    # get results from sqlite db
    with engine.connect() as conn:
        apartments = pd.read_sql("select * from apartments where status ='new'", conn)

    # apartments = temp
    apartments = apartments.assign(
        cluster=lambda x: x.groupby("endereco").ngroup(),
        entries_by_cluster=lambda x: x.loc[:, ["status", "endereco"]]
        .groupby("endereco")
        .transform("count"),
        lat=lambda x: randomize_location(x, "lat"),
        lon=lambda x: randomize_location(x, "lon"),
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
    print("Map dataset shape: ")
    apartments.shape
    print("Map dataset info: ")
    apartments.info()

    apartments = [Apartment(**entry.to_dict()) for _, entry in apartments.iterrows()]

    # Map
    create_map(apartments, filename)
