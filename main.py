import query_and_store

args = {
    "mode": "sandbox",
    "limit": 100,
    "db": "db.sqlite",
}


def router():
    query_and_store.init(args)
    # path_update_xlsx()


if __name__ == "__main__":
    router()
