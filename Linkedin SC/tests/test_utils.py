import pytest
from utils import dedupe_posts, clean_posts

def test_dedupe_posts():
    posts = [
        {"post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1/", "content": "A", "author_name": "X", "post_date": ""},
        {"post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1/", "content": "A dup", "author_name": "X", "post_date": ""},
        {"post_url": "", "content": "Same", "author_name": "Y", "post_date": "2025-08-17"},
        {"post_url": "", "content": "Same", "author_name": "Y", "post_date": "2025-08-17"},
    ]
    out = dedupe_posts(posts)
    assert len(out) == 2

def test_clean_posts():
    posts = [{"content": " Hello  \nWorld  ", "author_name": "  Jane  Doe  "}]
    out = clean_posts(posts)
    assert out[0]["content"] == "Hello World"
    assert out[0]["author_name"] == "Jane Doe"
