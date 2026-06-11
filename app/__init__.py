"""app package initializer.

Presence of this file makes `app` a package so absolute imports like
`from app import admin` work when Streamlit runs the script directly.
"""

__all__ = ["admin", "config", "db"]
