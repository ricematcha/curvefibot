import requests


def get_pools():
    coins = ["BTC", "ETH", "XRP", "LTC", "BCH", "ADA", "DOT", "LINK", "BNB", "XLM"]

    # crypto_data = requests.get(
    #     "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD".format(",".join(coins))).json()["RAW"]
    crypto_data = requests.get(
        "https://api.curve.fi/api/getPools/ethereum/main").json()

    data = crypto_data['data']
    poolData = data['poolData']
    tvlAll = data['tvlAll']
    tvl = data['tvl']

    lpList = []
    for dict in poolData:
        lpData = {
            "id": dict["id"],
            "address": dict["address"],
            "totalSupply": dict["totalSupply"],
            "coins": dict["coins"],
            "usdTotal": dict["usdTotal"]
        }
        lpList.append(lpData)

    return lpList

if __name__ == "__main__":
    print(get_pools())