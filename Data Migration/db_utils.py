import re


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(value: str, label: str = "identifier") -> str:
    """Allow only simple SQL identifiers before interpolating them into SQL."""
    if not value or not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(
            f"Invalid {label!s}: {value!r}. Use letters, numbers, and underscores only."
        )
    return value


def quote_sqlserver_identifier(value: str) -> str:
    return f"[{validate_identifier(value)}]"


def qualify_sqlserver_table(table_name: str, schema: str | None = None) -> str:
    parts = [quote_sqlserver_identifier(table_name)]
    if schema:
        parts.insert(0, quote_sqlserver_identifier(schema))
    return ".".join(parts)
