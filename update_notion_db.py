import requests
from datetime import datetime, timezone
from typing import Dict, Optional, List

def get_pages_in_db(headers: Dict[str, str], db_id: str, num_pages: Optional[int] = None) -> List[Dict[str, any]]:
    """ Retrieve pages from a Notion database. """

    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    return results


def create_page_in_db(headers: Dict[str, str], db_id: str, data: Dict[str, any]) -> requests.Response:
    """ Create a new page in a Notion database. """
    
    create_url = "https://api.notion.com/v1/pages"
    date = datetime.now().astimezone(timezone.utc).isoformat()
    payload = {'created_time': date, "parent": {"database_id": db_id}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)
    if res.status_code == 200:
        print(f"{res.status_code}: Page created successfully")
    else:
        print(f"{res.status_code}: Error during page creation")
    return res