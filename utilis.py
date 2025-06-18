import os
from pathlib import Path
from collections import Counter

# Basic extension to language mapping
EXT_TO_LANG = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",

}

def analyze_languages(repo_path: str) -> dict:
    """Analyzes file extensions to estimate language usage."""
    counter = Counter()

    for file_path in Path(repo_path).rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            lang = EXT_TO_LANG.get(ext)
            if lang:
                counter[lang] += 1

    total = sum(counter.values())
    if total == 0:
        return {}

    percentages = {lang: round((count / total) * 100, 2) for lang, count in counter.items()}
    return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))
