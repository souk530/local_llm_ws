import requests

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'deepseek-coder:8b',
        'prompt': '日本語で説明してください：量子化とは何ですか？'
    },
    stream=True
)
for chunk in response.iter_lines():
    print(chunk.decode(), end='')
