import os
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup

# Trie for Keyword Matching
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_words(node, prefix)

    def _collect_words(self, node, prefix):
        words = []
        if node.is_end_of_word:
            words.append(prefix)
        for char, child in node.children.items():
            words.extend(self._collect_words(child, prefix + char))
        return words


# N-ary Tree for Content Hierarchy
class Node:
    def __init__(self, tag, content=None):
        self.tag = tag
        self.content = content
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)


# Red-Black Tree (simplified for ranking)
class RBTreeNode:
    def __init__(self, tag, relevance, color="red"):
        self.tag = tag
        self.relevance = relevance
        self.color = color
        self.left = None
        self.right = None

class RBTree:
    def __init__(self):
        self.root = None

    def insert(self, tag, relevance):
        new_node = RBTreeNode(tag, relevance)
        if not self.root:
            new_node.color = "black"
            self.root = new_node
        else:
            self.root = self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current, node):
        if not current:
            return node
        if node.relevance < current.relevance:
            current.left = self._insert_recursive(current.left, node)
        elif node.relevance > current.relevance:
            current.right = self._insert_recursive(current.right, node)
        return current

    def in_order_traversal(self, node):
        if node:
            yield from self.in_order_traversal(node.left)
            yield node.tag, node.relevance
            yield from self.in_order_traversal(node.right)


# Hybrid SEO System with SerpApi Integration
class HybridSEOSystem:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.trie = Trie()
        self.hierarchy = Node("SEO Elements")
        self.rank_tree = RBTree()
        self.analysis_results = []

    def reset(self):
        self.hierarchy = Node("SEO Elements")
        self.rank_tree = RBTree()
        self.analysis_results = []

    def search_webpages(self, keywords):
        """Fetch Bing search results using SerpApi."""
        self.reset()
        if not self.api_key:
            print("Error: Missing SERPAPI_KEY in environment variables.")
            return []

        try:
            search = GoogleSearch({
                "q": keywords,
                "engine": "bing",
                "api_key": self.api_key,
                "count": 5
            })
            results = search.get_dict()
            search_results = []

            for res in results.get("organic_results", []):
                title = res.get("title", "No Title")
                link = res.get("link", "#")
                snippet = res.get("snippet", "No description")
                search_results.append((title, link, snippet))
                self.fetch_and_analyze(link)

            return search_results
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return []

    def fetch_and_analyze(self, url):
        """Analyze a single webpage for SEO elements."""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Title
            title_tag = soup.find('title')
            title_content = title_tag.text if title_tag else "No title tag found"
            self.hierarchy.add_child(Node("Title", title_content))
            self.trie.insert("title")
            self.rank_tree.insert("Title", relevance=10)

            # Meta Description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            desc_content = meta_description['content'] if meta_description else "No meta description found"
            self.hierarchy.add_child(Node("Meta Description", desc_content))
            self.trie.insert("meta description")
            self.rank_tree.insert("Meta Description", relevance=8)

            # Open Graph Title
            og_title = soup.find('meta', property='og:title')
            og_title_content = og_title['content'] if og_title else "No Open Graph title found"
            self.hierarchy.add_child(Node("Open Graph Title", og_title_content))
            self.trie.insert("og title")
            self.rank_tree.insert("OG Title", relevance=6)

            # Store analysis
            self.analysis_results.append({
                "url": url,
                "title": title_content,
                "meta_description": desc_content,
                "og_title": og_title_content
            })

        except Exception as e:
            print(f"Error analyzing {url}: {e}")

    def get_analysis_for_url(self, url):
        """Return analysis for a specific URL."""
        for result in self.analysis_results:
            if result["url"] == url:
                return result
        return None
