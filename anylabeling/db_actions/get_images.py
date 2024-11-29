import json
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Get the path of the .env file relative to the executable
env_path = os.path.join(os.path.dirname(__file__), ".env")

# Load .env from the correct path
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("Warning: .env file not found, using default environment variables.")

# Retrieve environment variables with default values
SUPABASE_URL = os.getenv("SUPABASE_URL", "default_url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "default_key")

# test if the variables are correctly loaded
print(f"Supabase URL: {SUPABASE_URL}")
print(f"Supabase Key: {SUPABASE_KEY}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("connected to database")

default_path = "/Users/macbook/Desktop/test_anylabeling/test_dir"


def get_scan(scan_id: str):
    response = (
        supabase.table("Scan").select().eq("id", scan_id).execute().json()
    )
    return json.loads(response)


# for a scan id, we want to retrieve the scan result associated (in the table ScanResults)


def get_scan_result(scan_id: str):
    response = (
        supabase.table("ScanResult")
        .select()
        .eq("scanId", scan_id)
        .execute()
        .json()
    )
    return json.loads(response)


def download_unreviewed_scans(limit_date=None, organisation_id=None):
    response = (
        supabase.table("ScanResult")
        .select()
        .eq("validated", "FALSE")
        .execute()
        .model_dump_json()
    )

    scan_results = json.loads(response)
    scan_ids = [result["scanId"] for result in scan_results["data"]]

    if organisation_id is not None:
        scans_response = (
            supabase.table("Scan")
            .select()
            .in_("id", scan_ids)
            .eq("organizationId", organisation_id)
            .execute()
            .model_dump_json()
        )
        return json.loads(scans_response)

    if limit_date:
        scans_response = (
            supabase.table("Scan")
            .select()
            .in_("id", scan_ids)
            .gte("createdAt", limit_date)
            .execute()
            .model_dump_json()
        )
    else:
        scans_response = (
            supabase.table("Scan")
            .select()
            .in_("id", scan_ids)
            .execute()
            .model_dump_json()
        )
    return json.loads(scans_response)


def get_picture_url(scan_id: str):
    response = (
        supabase.table("Scan")
        .select("pictureUrl")
        .eq("id", scan_id)
        .execute()
        .json()
    )
    return json.loads(response)


# we want to save a picture in the storage


def download_picture(scan_id: str, destination=""):
    url = get_picture_url(scan_id)["data"][0]["pictureUrl"]
    response = requests.get(url)
    # we create the directory if it does not exist
    if not os.path.exists(destination):
        os.makedirs(destination)
    if not destination.endswith(f"{scan_id}.jpg"):
        destination = (
            f"{destination}/{scan_id}.jpg"
            if destination
            else f"./{scan_id}.jpg"
        )
    with open(destination, "wb") as file:
        file.write(response.content)


def download_data_line_json(scan_id: str, destination=""):
    scan = get_scan(scan_id)
    scan_result = get_scan_result(scan_id)
    scan["scan_result"] = scan_result
    # we create the directory if it does not exist
    if not os.path.exists(destination):
        os.makedirs(destination)
    if not destination.endswith(f"{scan_id}.json"):
        destination = (
            f"{destination}/{scan_id}.json"
            if destination
            else f"./{scan_id}.json"
        )
    with open(destination, "w") as file:
        json.dump(scan, file)


def download_pictures_from_table(data, destination=default_path):
    for scan in data["data"]:
        download_picture(scan["id"], destination)


def download_data_line_json_from_table(data, destination="annotations"):
    for scan in data["data"]:
        download_data_line_json(scan["id"], destination)


if __name__ == "__main__":

    default_path = "/Users/macbook/Desktop/test_anylabeling/test_dir"

    limit_date = "2024-10-08"
    unreviewed_scans = download_unreviewed_scans(limit_date=limit_date)
    nb_unreviewed_scans = len(unreviewed_scans["data"])

    print(f"{nb_unreviewed_scans} unreviewed scans")
    print(f"Downloading pictures and annotations from {limit_date} to now ...")
    download_pictures_from_table(unreviewed_scans)
    print(f"{nb_unreviewed_scans} pictures downloaded")
    print("Downloading annotations...")
    download_data_line_json_from_table(unreviewed_scans)
    print(f"{nb_unreviewed_scans} annotations downloaded")
