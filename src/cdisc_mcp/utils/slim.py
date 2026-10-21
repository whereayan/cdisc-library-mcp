"""Response slimming: make CDISC API payloads agent-friendly.

Raw Library API responses carry hypermedia noise that costs tokens without
helping an LLM:

* ``_links`` / ``links`` blocks with ``href``/``title``/``type`` triples;
* ``@search.score`` / ``@search.highlights`` metadata on search hits.

``slim()`` drops the ``@``-prefixed metadata and collapses every link block
into one compact ``refs`` map (``label -> href``), so drill-down paths survive
while the payload shrinks. Pass ``raw=true`` at the tool layer to opt out.
"""

from typing import Any

_LINK_KEYS = frozenset({"_links", "links"})
_SELF_KEYS = frozenset({"self"})


def _link_label(item: dict[str, Any]) -> str:
    """Pick the most informative label for a link item."""
    for key in ("linkName", "title", "name", "type"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "ref"


def _collect_refs(node: Any, out: dict[str, str]) -> None:
    """Flatten an arbitrary link block into {label: href} pairs."""
    if isinstance(node, dict):
        href = node.get("href")
        if isinstance(href, str) and href:
            label = _link_label(node)
            name, n = label, 2
            while name in out:
                name = f"{label}-{n}"
                n += 1
            out[name] = href
            return
        for key, value in node.items():
            if key in _SELF_KEYS:
                continue
            _collect_refs(value, out)
    elif isinstance(node, list):
        for value in node:
            _collect_refs(value, out)


def slim(obj: Any) -> Any:
    """Recursively strip hypermedia/search noise from an API payload.

    * dict keys starting with ``@`` are dropped (search score/highlights);
    * ``_links`` / ``links`` blocks are replaced by a flat ``refs`` map
      (``self`` links are dropped as redundant);
    * everything else is preserved and recursed into.
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        refs: dict[str, str] = {}
        for key, value in obj.items():
            if isinstance(key, str) and key.startswith("@"):
                continue
            if key in _LINK_KEYS:
                _collect_refs(value, refs)
                continue
            out[key] = slim(value)
        if refs:
            out["refs"] = refs
        return out
    if isinstance(obj, list):
        return [slim(item) for item in obj]
    return obj


__all__ = ["slim"]
