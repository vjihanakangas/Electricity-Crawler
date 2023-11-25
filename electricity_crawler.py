from datetime import datetime
import requests
from bs4 import BeautifulSoup
from influxdb import InfluxDBClient

# InfluxDB settings
influxdb_host = 'your_ip'
influxdb_port = your_port
influxdb_database = 'your_database'

# Create an InfluxDB client and write the data
client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
client.switch_database(influxdb_database)

# URL to scrape
url = 'https://www.porssisahkoa.fi/'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    hintaObjects = []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find divs with the first specified class
    divs_class1 = soup.find_all('div', class_='MuiGrid2-root MuiGrid2-direction-xs-row MuiGrid2-grid-xs-4 mui-style-xw2ziw')

    for div in divs_class1:
        hintaObject_1 = []
        # Find the H4 tag within the div
        h4_element = div.find('h4')

        if h4_element:
            # Print the title
            title = h4_element.get_text().strip()
            hintaObject_1.append(title)

            # Find and print the three child divs
            child_divs = div.find_all('div')
            for child_div in child_divs:
                hintaObject_1.append(child_div.get_text().strip())
        else:
            print("H4 tag not found within the div.")
        hintaObjects.append(hintaObject_1)

    # Find divs with the second specified class
    divs_class2 = soup.find_all('div', class_='MuiBox-root mui-style-10woeex')

    for div in divs_class2:
        # Find the div containing the title and other information
        inner_div = div.find('div')
        hintaObject_2 = []
        if inner_div:
            # Extract the <h1> tag separately
            h1_element = inner_div.find('h1')
            if h1_element:
                title = h1_element.get_text().strip()
                hintaObject_2.append(title)

            # Extract and print the other <div> tags
            other_divs = inner_div.find_all('div')
            for other_div in other_divs:
                hintaObject_2.append(other_div.get_text().strip())
        else:
            print("Inner div not found within the div.")
    hintaObjects.append(hintaObject_2)

    for object in hintaObjects:
        print(object)

    for object in hintaObjects:
        title = ""
        if (object[0] == "Halvin hinta"):
            title = "halvin_hinta"
        elif (object[0] == "Kallein hinta"):
            title = "kallein_hinta"
        elif (object[0] == "Keskihinta"):
            title = "keskihinta"
        elif (object[0] == "Hinta nyt"):
            title = "hinta_nyt"
        data = [
                {
                    "measurement": title,
                    "tags": {
                        "symbol": "ELECTRICITY"
                    },
                    "time": datetime.now(),
                    "fields": {
                        "time_slot": object[1],
                        "price_value": round(float(object[2].replace(",", ".").replace("−", "-")), 2) + 0.45
                    }
                }
            ]

        # Write data to InfluxDB
        client.write_points(data)

        print(f"Successfully uploaded to InfluxDB. Database: {influxdb_database}, Time: {datetime.now()}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
