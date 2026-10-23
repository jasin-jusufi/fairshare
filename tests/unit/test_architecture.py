from importlinter.cli import lint_imports


def test_clean_architecture_contracts_hold() -> None:
    assert lint_imports() == 0
