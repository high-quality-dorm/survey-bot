import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from .db.database import get_session
from .db.queries import create_survey
from .schemas import schemas


class JSONParser:
    def __init__(self, file: Path):
        self.filepath = file

    def parse(self) -> schemas.SurveyJSON:
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return schemas.SurveyJSON(**data)

    async def create_survey_in_db(self, session: AsyncSession) -> None:
        survey = self.parse()
        await create_survey(session, survey)


if __name__ == "__main__":
    import asyncio
    from survio.db.database import create_tables
    async def main():
        await create_tables()
        path = Path(__file__).parents[4] / "test.json"

        parser = JSONParser(path)

        async for session in get_session():
            await parser.create_survey_in_db(session)
            print(f"Опрос успешно создан из: {path.name}")
            break

    asyncio.run(main())
