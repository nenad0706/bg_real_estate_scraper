# bg_real_estate_scraper
Webapp with built in scraper (Flask, MongoDB, ETL)

Fetch real estates for sale data from https://cityexpert.rs/prodaja-stanova-beograd and load into mongodb. 

* /index page shows list of municipalities.

* /details page shows some general data for municipality (average price, size..) and details for all real estates in tabelar 
view (street, floor, Structure, Furnished, Size (m²), Price(€), Price(€/m²), Filed, Url on cityexpert).

* By clicking on `scrape` button, user can trigger scraping process. Minimal allowed interval for scraping is 30 minutes. 
/scrape page shows success message, number of records in db and number of new records.
