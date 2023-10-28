import os
import argparse
from get_hfpapers import fetch_top_hf_papers, fetch_paper_details
from update_notion import get_page_by_id, display_page_info, add_content_to_page, get_blocks_by_id

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if NOTION_TOKEN is None:
    raise EnvironmentError("NOTION_TOKEN not set")
#DATABASE_ID = os.environ.get("DATABASE_ID")
#if DATABASE_ID is None:
#    raise EnvironmentError("DATABASE_ID is not set")

HEADERS = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# Main function
def main():
    parser = argparse.ArgumentParser(description="Fetch and update Notion page with Hugging Face papers.")
    parser.add_argument("--page-id", type=str, default="594e4ca3564c44a5aac4778fd06ba679", help="Notion page ID to update")
    parser.add_argument("--past_days", type=int, default=2, help="Number of days in the past from the current date to retrieve papers from")
    args = parser.parse_args()

    # retrieve page and display info
    page = get_page_by_id(HEADERS, args.page_id)
    display_page_info(HEADERS, page)
    
    # fetch top papers from Hugging Face
    papers = fetch_paper_details(fetch_top_hf_papers(args.past_days))

    # add each paper to the Notion page
    for paper in papers:
        add_content_to_page(
            args.page_id,
            HEADERS,
            paper["upvotes"],
            paper["date"],
            paper["name"],
            paper["title"],
            paper["url"],
            paper["abstract"]
        )

if __name__ == "__main__":
    main()
