from typing import Any

from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter

from backend.agent.system_prompt import load_system_prompt
from backend.agent.tools.calculate_tool import calculate
from backend.agent.tools.get_contract_tool import get_contract
from backend.agent.tools.search_assets_tool import search_assets
from backend.agent.tools.search_sites_tool import search_sites
from backend.agent.tools.search_tickets_tool import search_tickets
from backend.agent.tools.update_card_tool import update_card
from backend.settings import Settings

TOOLS = [
    update_card,
    search_sites,
    search_assets,
    search_tickets,
    get_contract,
    calculate,
]


def build_model(settings: Settings) -> ChatOpenRouter:
    return ChatOpenRouter(
        model=settings.openai_model,
        api_key=settings.openai_api_key.get_secret_value(),
        temperature=0,
        timeout=90000,
        max_retries=2,
        max_tokens=4096,
        streaming=True,
        reasoning={"effort": "high"},
    )


def build_agent(settings: Settings) -> Any:
    return create_agent(
        model=build_model(settings),
        tools=TOOLS,
        system_prompt=load_system_prompt(),
        name="reflex-appeal",
    )
