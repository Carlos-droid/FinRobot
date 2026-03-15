if __name__ == "__main__":

    from finrobot.utils import register_keys_from_json

    register_keys_from_json("../../config_api_keys")
    # print(FinnHubUtils.get_company_profile("AAPL"))
    # print(FinnHubUtils.get_basic_financials_history("AAPL", "annual", "2019-01-01", "2021-01-01"))
    print(FinnHubUtils.get_basic_financials("AAPL"))
