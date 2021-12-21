from dotenv import dotenv_values


def print_export():
    values = dotenv_values(dotenv_path=".env")
    values = [f"export {key}={val}" for key, val in values.items()]
    print("\n".join(values))


if __name__ == "__main__":
    print_export()
