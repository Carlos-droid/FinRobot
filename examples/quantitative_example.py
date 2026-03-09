if __name__ == "__main__":
    # Example usage:
    start_date = "2011-01-01"
    end_date = "2012-12-31"
    ticker = "MSFT"
    # BackTraderUtils.back_test(
    #     ticker, start_date, end_date, "SMA_CrossOver", {"fast": 10, "slow": 30}
    # )
    BackTraderUtils.back_test(
        ticker,
        start_date,
        end_date,
        "test_module:TestStrategy",
        {"exitbars": 5},
    )
