from . import v1, v2

_VERSIONS = {
    "v1": v1,
    "v2": v2,
}


def get_prompt_builder(version: str):
    try:
        module = _VERSIONS[version]
    except KeyError:
        raise ValueError(f"Unknown prompt version: {version!r}. Available: {list(_VERSIONS)}")
    return module.build_prompt
