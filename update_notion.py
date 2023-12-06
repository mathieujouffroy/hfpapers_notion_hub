import json
import requests
from typing import List, Dict

def get_page_by_id(headers: Dict[str, str], page_id: str) -> Dict:
    """ Fetch a Notion page by its ID. """

    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def get_blocks_by_id(headers: Dict[str, str], block_id: str) -> List[Dict]:
    """ Fetch child blocks of a given block or page by its ID. """
    
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get("results", [])


def display_block_info(headers: Dict[str, str], block: Dict, index: int, prefix: str = ""):
    """ Display information about a Notion block. """

    block_type = block.get("type")
    block_id = block.get("id")
    
    if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "toggle", "numbered_list_item", "bulleted_list_item"]:
        rich_text = block.get(f"{block_type}", {}).get("rich_text", [])
        text_content = ""
        for text_segment in rich_text:
            text_dict = text_segment.get("text", {}) if text_segment else None
            text = text_dict.get("content", "") if text_dict else ""
            link = text_dict.get("link", {}) if text is not None else None
            url = link.get("url", "") if link is not None else ""       
            text_content += f"{text} \nurl: {url}"

        print(f"{prefix}block_id:{index} - {block_type}: {text_content}")

        if block.get("has_children", False):
            child_blocks = get_blocks_by_id(headers, block_id)
            for i, child_block in enumerate(child_blocks):
                display_block_info(headers, child_block, i, prefix=f"child ")
    else:
        print(f"\n{prefix}other: {block_type}")


def display_page_info(headers: Dict[str, str], page: Dict):
    """ Display information about a Notion page and its blocks. """

    page_id = page["id"]
    page_url = page["url"]
    last_update_time = page["last_edited_time"]
    props = page["properties"]
    title = props["title"]["title"][0]["plain_text"]

    print(f"\nPage title: {title}")
    print(f"Page ID: {page_id}")
    print(f"Page URL: {page_url}")
    print(f"Last update: {last_update_time}")
    
    # Fetch and display blocks (content) of the page
    blocks = get_blocks_by_id(headers, page_id)
    print("\nBlocks (Content):")
    for i, block in enumerate(blocks):
        display_block_info(headers, block, i, "\n")


def add_content_to_page(
    page_id: str,
    headers: Dict[str, str],
    upvotes: int,
    date: str,
    paper_name: str,
    title: str,
    link_url: str,
    child_content: str
):
    """
    Add content to a Notion page.

    Args:
        page_id (str): The ID of the Notion page to which the content will be added.
        headers (Dict[str, str]): Headers for the HTTP request.
        upvotes (int): The number of upvotes for the paper.
        date (str): The date associated with the paper.
        paper_name (str): The name of the paper.
        title (str): The title of the paper.
        link_url (str): The URL associated with the content.
        child_content (str): The content to be added as a child block.

    Returns:
        None
    """

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    payload = json.dumps({
        "children": [
            {
                "object": "block",
                "type": "toggle",
                "has_children": True,
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Up {upvotes} - ",
                            },
                            "annotations": {"color": "blue"}
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": f"{date} - ",
                            }
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": paper_name,
                                "link": {
                                    "url": link_url
                                }
                            },
                            "annotations": {
                                'bold': True,
                                "color": "orange"
                            }
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": title,
                                "link": {
                                    "url": link_url
                                }
                            },
                            "annotations": {
                                "color": "orange"
                            }
                        }
                    ]
                }
            },
        ]
    })  
    response = requests.patch(url, headers=headers, data=payload)
    #print(response.json()["results"])
    created_block_id = response.json()["results"][0]["id"]  
    parent_url = f"https://api.notion.com/v1/blocks/{created_block_id}/children"
    child_payload = json.dumps({
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": child_content
                            }
                        }
                    ]
                }
            }
        ]
    })
    response = requests.patch(parent_url, headers=headers, data=child_payload)
    #print(response.json())

