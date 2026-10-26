from typing import Annotated

from fastapi import Path

# Primary keys are 32-bit integers in PostgreSQL. IDs outside that range cannot exist
# and are rejected with 422 before they reach the database driver; IDs inside the
# range that do not exist (including 0 and negatives) still answer 404.
MAX_ID = 2**31 - 1

Id = Annotated[int, Path(ge=-MAX_ID - 1, le=MAX_ID, description="Numeric ID")]
