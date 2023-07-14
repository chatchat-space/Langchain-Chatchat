import requests

RapidAPIKey = "90bbe925ebmsh1c015166fc5e12cp14c503jsn6cca55551ae4"

class DeepSearch:
    def search(query: str = ""):
        query = query.strip()

        if query == "":
            return ""

        if RapidAPIKey == "":
            return "请配置你的 RapidAPIKey"

        url = "https://bing-web-search1.p.rapidapi.com/search"

        querystring = {"q": query,
                "mkt":"zh-cn","textDecorations":"false","setLang":"CN","safeSearch":"Off","textFormat":"Raw"}

        headers = {
            "Accept": "application/json",
            "X-BingApis-SDK": "true",
            "X-RapidAPI-Key": RapidAPIKey,
            "X-RapidAPI-Host": "bing-web-search1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        data_list = response.json()['value']

        if len(data_list) == 0:
            return ""
        else:
            result_arr = []
            result_str = ""
            count_index = 0
            for i in range(6):
                item = data_list[i]
                title = item["name"]
                description = item["description"]
                item_str = f"{title}: {description}"
                result_arr = result_arr + [item_str]

            result_str = "\n".join(result_arr)
            return result_str

