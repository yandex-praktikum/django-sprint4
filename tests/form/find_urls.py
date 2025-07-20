from typing import List, Sequence, Dict, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag, SoupStrainer

from conftest import KeyVal


def find_links_between_lines(
    page_content: str,
    urls_start_with: str,
    start_lineix: int,
    end_lineix: int,
    link_text_in: Optional[str] = None,
) -> List[Tag]:
    if not link_text_in:
        link_text_in = "\n".join(
            page_content.split("\n")[
                (start_lineix if start_lineix >= 0 else 0): (
                    end_lineix if end_lineix >= 0 else None
                )
            ]
        )
    result_links = []

    parse_tags = SoupStrainer(["a", "form", "button"])
    soup = BeautifulSoup(page_content, features="html.parser", parse_only=parse_tags)

    for tag in soup:
        if tag.name == "a":
            href = tag.get("href")
            if (
                href
                and "logout" not in href
                and tag.text.strip() in link_text_in
                and href.startswith(urls_start_with)
                and (tag.sourceline >= start_lineix or start_lineix < 0)
                and (tag.sourceline <= end_lineix or end_lineix < 0)
            ):
                result_links.append(tag)

        elif tag.name == "form":
            action = tag.get("action", "")
            button = tag.find("button")
            if (
                button
                and "logout" not in action
                and action.startswith(urls_start_with)
                and button.text.strip() in link_text_in
            ):
                result_links.append(tag)

    return result_links


def get_url_display_names(
    urls_start_with: KeyVal, item_id: int, link_tags: Sequence[Tag]
) -> Dict[str, str]:
    """Map urls to their generic form (e.g.
    /post/<post_id>/comment_edit/<comment_id>/)"""
    result = {}

    def get_url_template(url: str) -> str:
        return url.replace(urls_start_with.val, urls_start_with.key).replace(
            f"{item_id}", "<comment_id>"
        )

    for i in range(len(link_tags)):
        url = link_tags[i].get("href")
        result[url] = get_url_template(url)
    return result
