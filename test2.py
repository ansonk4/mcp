import re
response_text = """
```json
{
    "text": "Here is the analysis result.",
    "image_path": "/tmp/graph_12345.png"
}
```
"""
json_match = re.search(r"```json\s*({.*?})\s*```", response_text, re.DOTALL)
if json_match:
    json_str = json_match.group(1)
    print(json_str)