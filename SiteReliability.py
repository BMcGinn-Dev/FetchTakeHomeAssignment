import yaml
import requests
import time
import os

# Function to ensure taht the file you are trying to receive the endpoints from exists. If an error, configure the proper file path.
def check_file_existence(file_path):
    if os.path.exists(file_path):
        print("File path exists!")
    else:
        print("File path does not exist.")
    return


# function to load all the endpoints, returns a LIST of the endpoint dictionary objects
def load_endpoints(file_path):
    with open(file_path, "r") as file:
        endpoints = yaml.safe_load(file)
    return endpoints


# Function that takes in the endpoints and returns a LIST of the urls strings within them
def get_urls(endpoints):
    urls = []
    for endpoint in endpoints:
        url = endpoint.get("url", "")
        if not url:
            if "headers" in endpoint and "url" in endpoint["headers"]:
                url = endpoint["headers"]["url"]
        urls.append(url)
    return urls


# Function to check health of the endpoints, returns a three element list of url, UP/DOWN, & latency
def check_health(url, idx):
    try:
        start_time = time.time()
        response = requests.get(url)
        latency = (time.time() - start_time) * 1000

        # print(f"URL: {url}, Status Code: {response.status_code}, Latency: {latency:.2f} ms") --> working print statement

        # Likely due to my connection & VPN, but when accessing www.fetchrewards.com, latency was almost always > 900ms. If you want to ensure the code still works
        # I recommend manually changing the latency barrier at the end of this line below
        if (
            response.status_code >= 200
            and response.status_code < 300
            and latency < 500   #had to change this is latency was too slow
        ):
            return [url, "UP", latency]
        else:
            return [url, "DOWN", latency]

    # Except block to check if point was never accessed
    except requests.RequestException as e:
        print(f"Failed to fetch endpoint {url} at index: {idx}")
        return [url, "DOWN", None]


# Function to log the counted of the current time health checks, returns a four element list of fetch_count, fetch_ups, rewards_count, rewards_ups
def log_results(health_checks):
    fetch_domain, fetch_count, fetch_ups = "fetch.com", 0, 0
    rewards_domain, rewards_count, rewards_ups = "www.fetchrewards.com", 0, 0

    for check in health_checks:
        url = check[0]
        up_down = check[1]

        if fetch_domain in url:
            fetch_count += 1
            if up_down == "UP":
                fetch_ups += 1
        elif rewards_domain in url:
            rewards_count += 1
            if up_down == "UP":
                rewards_ups += 1

    rotations = [fetch_count, fetch_ups, rewards_count, rewards_ups]

    return rotations


# Check if the script is being run directly
if __name__ == "__main__":
    print("Running the Site Reliability Program! \n --- Press Cntrl+C at any time to exit the program. ---  \n")

    # Instantiating required vars to default values
    file_path = "SampleInputFile.yaml"
    fetch_count, fetch_ups, rewards_count, rewards_ups = 0, 0, 0, 0
    health_checks = []
    curr_rotation = [0, 0, 0, 0]

    while True:
        endpoints = load_endpoints(file_path)

        urls = get_urls(endpoints)

        for i, url in enumerate(urls):
            health_checks.append(check_health(url, i))
    
        curr_rotation = log_results(health_checks)
        fetch_count = curr_rotation[0]
        fetch_ups = curr_rotation[1]
        rewards_count = curr_rotation[2]
        rewards_ups = curr_rotation[3]

        fetch_availability = round((100 * (fetch_ups/fetch_count)), 2)
        rewards_availability = round((100 * (rewards_ups/rewards_count)), 2)

        print(f"fetch.com has {fetch_availability}% availability percentage. ")
        print(f"www.fetchrewards.com has {rewards_availability}% availability percentage. ")

        time.sleep(15)
