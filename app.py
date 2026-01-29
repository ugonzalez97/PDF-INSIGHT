from utils import get_metadata
from utils import write_metadata_to_json
from utils import get_all_readers


def run():
    print("Starting application")

    all_metadata = {}
    for filename, reader in get_all_readers("data"):
        all_metadata[filename] = get_metadata(reader)

    write_metadata_to_json(all_metadata, f"complete_metadata.json")

    print("Application finished")


if __name__ == "__main__":
    run()
