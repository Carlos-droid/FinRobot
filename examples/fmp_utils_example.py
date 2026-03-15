if __name__ == "__main__":
    from finrobot.utils import register_keys_from_json

    register_keys_from_json("config_api_keys")
    FMPUtils.get_sec_report("NEE", "2024")
