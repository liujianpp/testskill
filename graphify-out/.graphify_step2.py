import json
from graphify.detect import detect
from pathlib import Path
result = detect(Path('e:/AI/skills'))
print(json.dumps(result, ensure_ascii=False))
