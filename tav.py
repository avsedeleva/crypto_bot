import json

from tavily import TavilyClient

query = "QRL"
client = TavilyClient("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")
response = client.search(
    query=query,
    include_domains=["x.com"],  # Ограничиваем поиск Twitter
    max_results=20,
    search_depth="advanced",
    days=2
)
print(json.dumps(response, indent=4))
#print(response)