## Purpose 

This is a basic scrapper that get results from the [VivaReal's website](https://www.vivareal.com.br/), one of the main Brazilian portals for property's rental and sales.
Sadly, the portal doesn't provide any way to search apartments through maps, such as other competitors. 

This project aims to correct this deficiency, by scrapping all properties supplied through a filter using Selenium, sending address results to the Google Maps API to get geolocation coordinates, and finally, generate a map using Folium/ipyleaflet.

This project is published for educational purposes only. Check VivaReal policies regarding scrapping public information.

## Usage

Create a .env file in the main directory with the following entries:


```bash
google_key="your google api key for running queries on address, usinge the Geolocation API"
#Examples
# This is the type of building you are interested on
bairro="/apartamento_residencial/"
# this is the type of filter you want - you can inspect possible values 
# by running search on the VivaReal's website
filtro="#area-desde=60&preco-ate=2400&preco-desde=1000&preco-total=sim&vagas=1&ordenar-por=preco-total:ASC"
```

## An Example

After running a successful query, generating the database and creating the map, you should find a file named "apartments_map.html" on your main project directory.
By opening such a file, you will find a map like:

[Basic Map](https://github.com/nettoyoussef/find_apartment/plot_example.png)


## Dependencies

- SQLAlchemy (portable db administration)
- Folium (map generation)
- Selenium (web scrapper)
- numpy (pandas and data manipulation)
- pandas (to organized processed information)
- beautifulsoup (parsing the web results)
- python-decouple (for the .env file)

## Attribution/Inspiration

This work is inspired, steals and borrows a lot from this [https://mattrighetti.com/2022/04/05/i-need-to-find-an-appartment.html](Hacker News' featured post), from Mattia Righetti.
