from __future__ import annotations

from copy import deepcopy
from functools import wraps
from typing import Any

_PATCHED = False
_BLOCKED_KEYS = {"cache_breakpoint", "cache_control"}


def _strip_unsupported_groq_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_unsupported_groq_fields(item)
            for key, item in value.items()
            if key not in _BLOCKED_KEYS
        }
    if isinstance(value, list):
        return [_strip_unsupported_groq_fields(item) for item in value]
    return value


def patch_litellm_for_groq() -> None:
    global _PATCHED
    if _PATCHED:
        return

    import litellm

    # ── First line of defence: turn off LiteLLM's own prompt-caching injection ──
    litellm.cache = None
    # Disable the flag that tells LiteLLM to inject cache_control breakpoints
    if hasattr(litellm, "enable_prompt_caching"):
        litellm.enable_prompt_caching = False

    original_completion = litellm.completion
    original_acompletion = getattr(litellm, "acompletion", None)

    def _clean_kwargs_for_groq(kwargs: dict) -> dict:
        kwargs = dict(kwargs)
        model = kwargs.get("model", "")

        if isinstance(model, str) and model.startswith("groq/"):
            if kwargs.get("messages"):
                kwargs["messages"] = _strip_unsupported_groq_fields(
                    deepcopy(kwargs["messages"])
                )
            if kwargs.get("extra_body"):
                kwargs["extra_body"] = _strip_unsupported_groq_fields(
                    deepcopy(kwargs["extra_body"])
                )
            kwargs.pop("cache_breakpoint", None)
            kwargs.pop("cache_control", None)
        return kwargs

    @wraps(original_completion)
    def safe_completion(*args: Any, **kwargs: Any) -> Any:
        if not kwargs.get("model") and args:
            kwargs["model"] = args[0]
            args = args[1:]
        kwargs = _clean_kwargs_for_groq(kwargs)
        return original_completion(*args, **kwargs)

    @wraps(original_acompletion)
    async def safe_acompletion(*args: Any, **kwargs: Any) -> Any:
        if not kwargs.get("model") and args:
            kwargs["model"] = args[0]
            args = args[1:]
        kwargs = _clean_kwargs_for_groq(kwargs)
        return await original_acompletion(*args, **kwargs)

    litellm.completion = safe_completion
    if original_acompletion is not None:
        litellm.acompletion = safe_acompletion

    _PATCHED = True