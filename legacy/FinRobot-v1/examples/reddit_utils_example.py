if __name__ == "__main__":

    from finrobot.utils import register_keys_from_json

    register_keys_from_json("../../config_api_keys")

    # df = RedditUtils.get_reddit_posts(query="AAPL OR Apple Inc OR #AAPL OR (Apple AND stock)", start_date="2023-05-01", end_date="2023-06-01", limit=1000)
    df = RedditUtils.get_reddit_posts(
        query="NVDA", start_date="2023-05-01", end_date="2023-06-01", limit=1000
    )
    print(df.head())
    df.to_csv("reddit_posts.csv", index=False)
