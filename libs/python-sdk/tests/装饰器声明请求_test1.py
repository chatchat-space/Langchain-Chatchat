import inspect
from functools import wraps
import requests


class HTTPClient:
    def __init__(self, base_url='', headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def http_request(self, method):
        def decorator(url, **options):
            headers = options.get('headers', self.headers)

            def wrapper(func):
                @wraps(func)
                def inner(*args, **kwargs):
                    try:
                        # Prepare the request URL
                        full_url = self.base_url + url
                        instance = args[0]  # Assuming func is a method of the class
                        print(f"Instance: {instance}")
                        # Prepare the request data from function arguments
                        data = kwargs
                        print(kwargs)
                        # Send the HTTP request
                        response = method(full_url, headers=headers, json=data)
                        response.raise_for_status()

                        # Return the response JSON
                        return response.json()
                    except requests.exceptions.HTTPError as http_err:
                        print(f"HTTP error occurred: {http_err}")
                    except Exception as err:
                        print(f"An error occurred: {err}")

                return inner

            return wrapper

        return decorator

    def post(self, url, **options):
        print(self)

        # Define a function that applies the decorator
        def decorator(func):
            return self.http_request(requests.post)(url, **options)(func)

        return decorator


app: HTTPClient = HTTPClient()


# Example usage of the class and its decorators
class MyAPIClient(HTTPClient):
    def __init__(self):
        super().__init__(base_url="https://api.example.com", headers={"Authorization": "Bearer token"})

    @app.post(url='/api/kb/recreate_summary_vector_store')
    def recreate_summary_vector_store(self, a: int, b: int):
        ...


# Example call to the decorated method
if __name__ == "__main__":
    client = MyAPIClient()
    response = client.recreate_summary_vector_store(a=1, b=1)
    print(response)
