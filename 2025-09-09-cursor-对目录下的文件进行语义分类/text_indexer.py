#!/usr/bin/env python3
"""
Text file indexer: scan a directory, classify text files by name, and
generate a hierarchical Markdown list.

Features:
- Detect text files via extension, MIME type, and a small binary sniff
- Grouping strategies: by first letter, by first character class, by extension, or semantic rules
- Natural sorting within groups
- CLI with helpful defaults

This script uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import mimetypes
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from math import sqrt
from typing import Callable, Dict, Iterable, List, Tuple, Any, Optional


# Common text file extensions (lowercase). The leading dot is included.
TEXT_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".log",
    ".json", ".ndjson", ".yml", ".yaml", ".xml", ".toml", ".ini", ".conf",
    ".html", ".htm", ".css", ".scss", ".less",
    ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".py", ".ipynb", ".r", ".rb", ".go", ".rs", ".java", ".kt", ".kts",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".fish",
    ".make", ".mk", ".cmake", ".bazel", ".bzl",
    ".sql", ".psql",
}

# Directories to skip by default
DEFAULT_IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__", ".idea", ".vscode",
    "venv", ".venv", "env", ".env",
}


# Fixed output order for semantic categories
CATEGORIES_ORDER = ["生活", "技术", "音乐", "数学", "自我发展", "其他"]
MAJOR_CATEGORIES = ["生活", "技术", "音乐", "数学", "自我发展"]

# Keyword weights for semantic classification
SEMANTIC_KEYWORDS: Dict[str, Dict[str, int]] = {
    "生活": {
        "生活": 5, "日常": 4, "衣食住行": 5, "饮食": 4, "做饭": 4, "菜谱": 4, "美食": 4,
        "旅行": 4, "旅游": 4, "出行": 3, "运动": 3, "健身": 3, "家庭": 4, "育儿": 4,
        "健康": 3, "理财": 3, "房屋": 3, "租房": 3, "居家": 4, "购物": 3, "日记": 4, "随笔": 3,
        "life": 4, "daily": 3, "diary": 4, "food": 3, "recipe": 4, "travel": 4, "fitness": 3,
        "health": 3, "family": 4, "home": 3, "shopping": 3, "budget": 3,
    },
    "技术": {
        "技术": 5, "编程": 5, "程序": 4, "代码": 5, "开发": 4, "算法": 5, "数据结构": 5, "架构": 4,
        "后端": 4, "前端": 4, "全栈": 4, "数据库": 4, "网络": 4, "操作系统": 4, "脚本": 4, "运维": 4,
        "git": 4, "shell": 4, "正则": 4, "测试": 3, "调试": 3, "debug": 3, "devops": 4, "ci": 3, "cd": 3,
        "linux": 4, "python": 4, "java": 4, "javascript": 4, "typescript": 4, "go": 4, "rust": 4,
        "docker": 4, "kubernetes": 4, "k8s": 4, "云": 3, "机器学习": 5, "深度学习": 5, "人工智能": 5, "ai": 4,
    },
    "音乐": {
        "音乐": 5, "歌曲": 4, "歌单": 4, "乐谱": 5, "五线谱": 4, "简谱": 4, "作曲": 4, "编曲": 4,
        "和弦": 4, "节奏": 3, "旋律": 3, "歌词": 4, "唱歌": 4, "钢琴": 4, "吉他": 4, "小提琴": 4, "鼓": 3,
        "music": 5, "song": 4, "playlist": 4, "score": 4, "chord": 4, "melody": 3, "rhythm": 3, "lyrics": 4,
        "piano": 4, "guitar": 4, "violin": 4, "drum": 3,
    },
    "数学": {
        "数学": 5, "代数": 4, "几何": 4, "微积分": 5, "概率": 5, "统计": 5, "线性代数": 5, "数论": 5, "拓扑": 5,
        "最优化": 4, "优化": 3, "方程": 3, "矩阵": 4, "微分": 3, "积分": 3, "证明": 3, "定理": 3, "离散": 4, "组合": 4,
        "math": 5, "algebra": 4, "geometry": 4, "calculus": 5, "probability": 5, "statistics": 5,
        "linear algebra": 5, "number theory": 5, "topology": 5, "optimization": 4, "matrix": 4,
        "equation": 3, "proof": 3, "theorem": 3, "discrete": 4, "combinatorics": 4,
    },
    "自我发展": {
        "自我发展": 5, "成长": 4, "自律": 4, "学习方法": 5, "学习": 4, "效率": 4, "时间管理": 5, "目标": 4,
        "计划": 3, "规划": 3, "习惯": 4, "阅读": 4, "读书": 4, "心理": 4, "冥想": 4, "正念": 4, "沟通": 4,
        "写作": 4, "演讲": 4, "领导力": 5, "职业": 3, "求职": 3,
        "self-improvement": 5, "growth": 4, "productivity": 4, "efficiency": 4, "time management": 5,
        "goal": 4, "planning": 3, "habit": 4, "reading": 4, "meditation": 4, "mindfulness": 4,
        "communication": 4, "writing": 4, "speech": 4, "leadership": 5, "career": 3,
    },
}


def _tokenize(text: str) -> List[str]:
    """Lightweight tokenizer:
    - Lowercase ASCII letters
    - Split on non-alphanumeric (keeps CJK as whole chars)
    - Keep CJK single characters and ASCII tokens length>=2
    """
    tokens: List[str] = []
    buf: List[str] = []

    def flush_buf():
        if not buf:
            return
        token = "".join(buf).lower()
        if len(token) >= 2:
            tokens.append(token)
        buf.clear()

    for ch in text:
        if ch.isascii() and ch.isalnum():
            buf.append(ch)
        else:
            flush_buf()
            # Keep CJK char as token
            if is_cjk(ch):
                tokens.append(ch)
    flush_buf()
    return tokens


def _hashing_vector(tokens: List[str], dim: int = 256) -> List[float]:
    vec = [0.0] * dim
    for tok in tokens:
        # Use md5 for stable hashing (stdlib only); map to bucket
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = -1.0 if (h >> 1) & 1 else 1.0
        vec[idx] += sign
    return vec


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for xa, xb in zip(a, b):
        dot += xa * xb
        na += xa * xa
        nb += xb * xb
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (sqrt(na) * sqrt(nb))


_VEC_DIM = 256
_CATEGORY_VECTORS: Dict[str, List[float]] | None = None


def _get_category_vectors() -> Dict[str, List[float]]:
    global _CATEGORY_VECTORS
    if _CATEGORY_VECTORS is None:
        _CATEGORY_VECTORS = {
            cat: _hashing_vector(_tokenize(cat), _VEC_DIM) for cat in CATEGORIES_ORDER
        }
    return _CATEGORY_VECTORS


def category_semantic_vec(filename: str) -> str:
    """Vector-similarity classifier.

    Preferred: cosine similarity between embedding vectors of the filename stem
    and category names (if embedding provider configured). Fallback to hashing
    vector similarity when embeddings are unavailable. "其他" is used as fallback
    if no positive similarity is found.
    """
    stem = os.path.splitext(filename)[0]

    emb_vec = _embed_text_cached(stem)
    # print(f"{stem}{emb_vec}")
    if emb_vec is not None:
        cat_embs = _get_category_embedding_vectors()
        best_cat = "其他"
        best_sim = -1.0
        for cat in MAJOR_CATEGORIES:
            sim = _cosine_similarity(emb_vec, cat_embs.get(cat, [])) if cat in cat_embs else 0.0
            if sim > best_sim:
                best_sim = sim
                best_cat = cat
        return best_cat if best_sim > 0.0 else "其他"

    # Fallback: hashing vector similarity
    tokens = _tokenize(stem)
    vec = _hashing_vector(tokens, _VEC_DIM)
    best_cat = "其他"
    best_sim = -1.0
    cat_vecs = _get_category_vectors()
    for cat in CATEGORIES_ORDER:
        sim = _cosine_similarity(vec, cat_vecs[cat])
        if sim > best_sim:
            best_sim = sim
            best_cat = cat
    return best_cat


def guess_is_text_file(file_path: str, *, sniff_bytes: int = 4096) -> bool:
    """Heuristically determine if a file is text.

    Strategy:
    1) Extension allowlist
    2) MIME type startswith text/ or is known text-y application/* subtype
    3) Sniff first N bytes and reject if NUL byte appears
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in TEXT_EXTENSIONS:
        return True

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith("text/"):
            return True
        # Some text-like application types
        text_like_suffixes = (
            "/json", "/xml", "/javascript", "/x-javascript", "/x-sh", "/x-shellscript",
        )
        if any(mime_type.endswith(suf) for suf in text_like_suffixes):
            return True

    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sniff_bytes)
            if b"\x00" in chunk:
                return False
            # If decodable as UTF-8 (even if replacement is needed) it's likely text
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                # Last resort: treat as binary
                return False
    except (OSError, PermissionError):
        # If we can't read it, don't include it
        return False


_NAT_SORT_TOKEN = re.compile(r"(\d+)")


def natural_sort_key(text: str) -> Tuple:
    """Return a key for natural sorting (numbers compared numerically)."""
    parts: List[str] = _NAT_SORT_TOKEN.split(text)
    key: List[Tuple[int, object]] = []
    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            key.append((0, part.lower()))
        else:
            try:
                key.append((1, int(part)))
            except ValueError:
                key.append((0, part))
    return tuple(key)


def is_cjk(char: str) -> bool:
    """Rough test if a character is CJK Unified Ideographs or related blocks."""
    code = ord(char)
    # Unified ideographs ranges (basic + extensions A-F, common ones)
    cjk_ranges = [
        (0x4E00, 0x9FFF),   # CJK Unified Ideographs
        (0x3400, 0x4DBF),   # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF), # Extension B
        (0x2A700, 0x2B73F), # Extension C
        (0x2B740, 0x2B81F), # Extension D
        (0x2B820, 0x2CEAF), # Extension E
        (0x2CEB0, 0x2EBEF), # Extension F
        (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    ]
    return any(start <= code <= end for start, end in cjk_ranges)


def first_significant_char(filename: str) -> str | None:
    """Return the first alphanumeric character in the filename (excluding extension), or None."""
    stem = os.path.splitext(filename)[0]
    for ch in stem:
        if ch.isalnum():
            return ch
    return None


def category_first_letter(filename: str) -> str:
    ch = first_significant_char(filename)
    if ch is None:
        return "其他"
    if ch.isalpha() and ch.encode("ascii", errors="ignore"):
        return ch.upper()
    if ch.isdigit():
        return "0-9"
    return "其他"


def category_first_char_class(filename: str) -> str:
    ch = first_significant_char(filename)
    if ch is None:
        return "其他"
    if ch.isalpha() and ch.encode("ascii", errors="ignore"):
        return "字母"
    if ch.isdigit():
        return "数字"
    if is_cjk(ch):
        return "汉字"
    return "其他"


def category_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return ext if ext else "无扩展名"


def _is_ascii_token(token: str) -> bool:
    try:
        token.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _build_keyword_pattern(token: str) -> re.Pattern:
    """Build a regex pattern for a keyword token.

    - For ASCII tokens, match with word boundaries and allow separators between words
      (space, underscore, hyphen).
    - For non-ASCII tokens (e.g., Chinese), perform simple substring matching.
    """
    if _is_ascii_token(token):
        parts = re.split(r"[\s_\-]+", token.strip())
        core = r"[\s_\-]*".join(re.escape(p) for p in parts if p)
        pattern = rf"(?<![A-Za-z0-9]){core}(?![A-Za-z0-9])"
        return re.compile(pattern, re.IGNORECASE)
    return re.compile(re.escape(token))


def category_semantic(filename: str) -> str:
    """Classify filename into one of the five semantic categories.

    Categories (fixed order): 生活、技术、音乐、数学、自我发展
    Strategy: weighted keyword scoring over the filename stem.
    """
    stem = os.path.splitext(filename)[0]
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORIES_ORDER}
    for cat, kw_map in SEMANTIC_KEYWORDS.items():
        for token, weight in kw_map.items():
            pattern = _build_keyword_pattern(token)
            matches = pattern.findall(stem)
            if matches:
                scores[cat] += weight * len(matches)

    # Choose the category with the highest score; tie-breaker by fixed order
    best_cat = None
    best_score = -1
    order_index = {cat: idx for idx, cat in enumerate(CATEGORIES_ORDER)}
    for cat, score in scores.items():
        if score > best_score:
            best_cat = cat
            best_score = score
        elif score == best_score and best_cat is not None:
            if order_index[cat] < order_index[best_cat]:
                best_cat = cat

    # Fallback when no keywords matched
    return best_cat if best_cat is not None and best_score > 0 else "其他"


def build_grouping_function(strategy: str) -> Callable[[str], str]:
    if strategy == "first-letter":
        return category_first_letter
    if strategy == "first-char-class":
        return category_first_char_class
    if strategy == "extension":
        return category_extension
    if strategy == "semantic":
        return category_semantic
    if strategy == "semantic-vec":
        return category_semantic_vec
    raise ValueError(f"未知的分组策略: {strategy}")


def sort_categories(categories: Iterable[str], strategy: str) -> List[str]:
    cats = list(categories)
    if strategy == "first-letter":
        def key(cat: str) -> Tuple[int, object]:
            if cat == "0-9":
                return (0, 0)
            if cat == "其他":
                return (2, "zzz")
            return (1, cat)
        return sorted(cats, key=key)
    if strategy == "semantic":
        index = {c: i for i, c in enumerate(CATEGORIES_ORDER)}
        return sorted(cats, key=lambda c: index.get(c, len(CATEGORIES_ORDER)))
    # For other strategies, simple natural or lexical sort is fine
    return sorted(cats, key=natural_sort_key)


def generate_markdown(
    groups: Dict[str, List[str]],
    *,
    strategy: str,
    scanned_dir: str,
    total_files: int,
) -> str:
    lines: List[str] = []
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"文件索引（目录：{scanned_dir}，时间：{timestamp}）")
    lines.append("")
    if total_files == 0:
        lines.append("- 未找到文本文件。")
        return "\n".join(lines) + "\n"

    for cat in sort_categories(groups.keys(), strategy):
        filenames = sorted(groups[cat], key=natural_sort_key)
        if not filenames:
            continue
        lines.append(f"- {cat}")
        for name in filenames:
            lines.append(f"  - {name}")
    return "\n".join(lines) + "\n"


def scan_directory(
    directory: str,
    *,
    include_hidden: bool,
    ignored_dirs: Iterable[str],
    output_file: str | None,
    grouping_strategy: str,
) -> Tuple[Dict[str, List[str]], int]:
    group_fn = build_grouping_function(grouping_strategy)
    groups: Dict[str, List[str]] = {}
    total = 0
    ignored_dirs_set = set(ignored_dirs)
    output_abs = os.path.abspath(output_file) if output_file else None

    for root, dirs, files in os.walk(directory):
        # Prune ignored directories
        pruned: List[str] = []
        for d in list(dirs):
            if d in ignored_dirs_set:
                pruned.append(d)
                continue
            if not include_hidden and d.startswith('.'):
                pruned.append(d)
        for d in pruned:
            try:
                dirs.remove(d)
            except ValueError:
                pass

        for fname in files:
            if not include_hidden and fname.startswith('.'):
                continue
            fpath = os.path.join(root, fname)
            # Skip the output file itself if it resides within scanned directory
            if output_abs and os.path.abspath(fpath) == output_abs:
                continue
            if not os.path.isfile(fpath):
                continue
            if guess_is_text_file(fpath):
                total += 1
                cat = group_fn(fname)
                groups.setdefault(cat, []).append(fname)
    return groups, total


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="扫描目录中的文本文件，并按名称分类生成 Markdown 层次列表。",
    )
    parser.add_argument(
        "directory",
        help="要扫描的目录路径",
    )
    parser.add_argument(
        "-o", "--output",
        help="输出 Markdown 文件路径（默认：在目录下生成 FILE_INDEX.md）",
        default=None,
    )
    parser.add_argument(
        "--group-by",
        choices=["first-letter", "first-char-class", "extension", "semantic", "semantic-vec"],
        default="semantic",
        help=(
            "分组策略：first-letter(按首个字母)；"
            "first-char-class(按首字符类别：字母/数字/汉字/其他)；"
            "extension(按扩展名)；"
            "semantic(语义：关键字匹配)；"
            "semantic-vec(语义：哈希向量+余弦相似度)"
        ),
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="包含隐藏文件和目录（以.开头）",
    )
    parser.add_argument(
        "--no-default-ignore",
        action="store_true",
        help="不要忽略默认目录（如 .git、node_modules 等）",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"错误：目录不存在：{directory}", file=sys.stderr)
        return 2

    output = args.output
    if output is None:
        output = os.path.join(directory, "FILE_INDEX.md")
    output = os.path.abspath(output)

    ignored = set() if args.no_default_ignore else set(DEFAULT_IGNORED_DIRS)

    groups, total = scan_directory(
        directory,
        include_hidden=args.include_hidden,
        ignored_dirs=ignored,
        output_file=output,
        grouping_strategy=args.group_by,
    )

    content = generate_markdown(
        groups,
        strategy=args.group_by,
        scanned_dir=directory,
        total_files=total,
    )

    try:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as exc:
        print(f"写入输出文件失败：{output}: {exc}", file=sys.stderr)
        return 3

    print(f"已生成：{output} （{total} 个文本文件）")
    return 0



EMBEDDING_PROVIDER_URL_ENV = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"  # e.g., https://api.openai.com/v1/embeddings
EMBEDDING_API_KEY_ENV = "sk-8cbd7d1f9aef4b408ade7d9c66481e03"       # API key if needed
EMBEDDING_MODEL_ENV = "text-embedding-v4"          # e.g., text-embedding-3-small
EMBEDDING_SIZE = 1024

_embedding_cache: Dict[str, List[float]] = {}
_category_embedding_cache: Optional[Dict[str, List[float]]] = None


def _http_post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: float = 15.0) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        return None


def _embedding_provider_config() -> Optional[Tuple[str, str, str]]:
    # Default to Ali DashScope OpenAI-compatible endpoint
    url = os.environ.get("EMBEDDING_PROVIDER_URL_ENV", "").strip() or \
          EMBEDDING_PROVIDER_URL_ENV
    # Prefer explicit API key, fallback to DASHSCOPE_API_KEY for convenience
    api_key = os.environ.get("EMBEDDING_API_KEY_ENV", "").strip() or \
              EMBEDDING_API_KEY_ENV.strip()
    model = os.environ.get("EMBEDDING_MODEL_ENV", "").strip() or EMBEDDING_MODEL_ENV
    if not api_key:
        # Without API key, treat as unconfigured so we fallback
        return None
    return url, api_key, model


def _embed_text(text: str) -> Optional[List[float]]:
    conf = _embedding_provider_config()
    if conf is None:
        return None
    url, api_key, model = conf
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {"input": text, "model": model, "dimension":EMBEDDING_SIZE, "encoding_format": "float"}
    resp = _http_post_json(url, payload, headers)
    # print(resp)
    if not resp:
        return None
    # OpenAI-compatible schema: { data: [ { embedding: [...] } ] }
    try:
        arr = resp.get("data", [])
        if not arr:
            return None
        emb = arr[0].get("embedding")
        if isinstance(emb, list) and all(isinstance(x, (int, float)) for x in emb):
            return [float(x) for x in emb]
    except Exception:
        return None
    return None


def _embed_text_cached(text: str) -> Optional[List[float]]:
    key = text
    if key in _embedding_cache:
        return _embedding_cache[key]
    vec = _embed_text(text)
    if vec is not None:
        _embedding_cache[key] = vec
    return vec


def _get_category_embedding_vectors() -> Dict[str, List[float]]:
    global _category_embedding_cache
    if _category_embedding_cache is not None:
        return _category_embedding_cache
    conf = _embedding_provider_config()
    cache: Dict[str, List[float]] = {}
    if conf is None:
        _category_embedding_cache = cache
        return cache
    for cat in MAJOR_CATEGORIES:
        vec = _embed_text_cached(cat)
        if vec is not None:
            cache[cat] = vec
    _category_embedding_cache = cache
    return cache



if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
