import query_and_store
import update_excel
import types
import sys

args = types.SimpleNamespace(
    db="db.sqlite",
)


def router() -> None:
    """
    parse cmd args and route user to relevant script
    """
    if len(sys.argv) < 2:
        print("enter command")
    elif sys.argv[1] == "query_and_store":
        query_and_store.main(args)
    elif sys.argv[1] == "update_excel":
        update_excel.main(args)


if __name__ == "__main__":
    router()
