import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.agent.run_hub import RunChannel, RunHub
from backend.repositories.appeal_repository import AppealRepository

logger = logging.getLogger(__name__)


class FakeAgentRunner:
    def __init__(self, hub: RunHub, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._hub = hub
        self._sf = session_factory

    async def start(self, appeal_id: int, reply_text: str | None = None) -> None:
        del reply_text
        channel = self._hub.open(appeal_id)
        asyncio.create_task(self._run(appeal_id, channel))

    async def _run(self, appeal_id: int, channel: RunChannel) -> None:
        try:
            await channel.emit({"type": "run_started", "appeal_id": appeal_id})
            async with self._sf() as session:
                repo = AppealRepository(session)
                appeal = await repo.get(appeal_id)
                if appeal is None:
                    await channel.emit({"type": "run_error", "detail": "Обращение не найдено"})
                    return
                appeal.run_status = "idle"
                await repo.commit()
            await channel.emit(
                {
                    "type": "run_finished",
                    "run_status": "idle",
                    "outcome": None,
                    "status": "new",
                    "auto_in_prod": False,
                }
            )
        except Exception:
            logger.exception("fake run failed")
            await channel.emit({"type": "run_error", "detail": "Прогон упал"})
        finally:
            channel.close()
