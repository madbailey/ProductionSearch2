import common_imports as ci

def read_config():
    try:
        with open("config.json", "r") as config_file:
            config = ci.json.load(config_file)
    except FileNotFoundError:
        ci.tk.messagebox.showerror("Error", "config.json is not found.")
        return {}
    except ci.json.JSONDecodeError:
        ci.tk.messagebox.showerror("Error", "config.json is not formatted correctly.")
        return {}

    return config