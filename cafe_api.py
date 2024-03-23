import requests


class CafeApi:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_random_cafe(self):
        """
        Return a random cafe
        :return: Cafe as dictionary
        """
        endpoint_url = self.endpoint + "/random"
        response = requests.get(url=endpoint_url)
        response.raise_for_status()
        return response.json()['cafe']

    def get_cafe_by_name(self, name):
        """
        Gets a cafe by name
        :return: cafe as dictionary
        """
        endpoint_url = self.endpoint + "/get_by_name?name=" + name
        response = requests.get(url=endpoint_url)
        response.raise_for_status()
        return response.json()['cafe']

    def add_cafe(self, name, location, img_url, map_url, coffee_price, has_wifi, has_sockets, has_toilet,
                 can_take_calls, seats):
        """
        Adds a cafe using API call then returns the parameters dictionary
        """
        endpoint_url = self.endpoint + "/add"

        parameters = {
            "name": name,
            "location": location,
            "img_url": img_url,
            "map_url": map_url,
            "coffee_price": coffee_price,
            "has_wifi": has_wifi,
            "has_sockets": has_sockets,
            "has_toilet": has_toilet,
            "can_take_calls": can_take_calls,
            "seats": seats,
        }
        r = requests.post(url=endpoint_url, data=parameters)
        r.raise_for_status()
        return parameters
