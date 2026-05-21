import tiktoken

MAX_TOKENS = 180_000


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def assert_within_limit(text: str, max_tokens: int = MAX_TOKENS) -> int:
    n = count_tokens(text)
    if n > max_tokens:
        raise ValueError(f"Prompt too large: {n} tokens (limit {max_tokens})")
    return n
