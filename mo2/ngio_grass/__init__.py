"""NGIO Grass Cache - MO2 plugin."""

# One number for the plugin and its archive: (major, minor, patch, beta number or 0 for a final).
VERSION = (2, 0, 0, 1)


def version_string() -> str:
    major, minor, patch, beta = VERSION
    return f"{major}.{minor}.{patch}" + (f"-beta.{beta}" if beta else "")


def createPlugin():
    from .plugin import NgioGrassTool

    return NgioGrassTool()
