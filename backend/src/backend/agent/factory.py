from langchain_openai import ChatOpenAI

from backend.agent.tools.get_contract_tool import get_contract
from backend.agent.tools.patch_facts_tool import patch_facts
from backend.agent.tools.search_assets_tool import search_assets
from backend.agent.tools.search_sites_tool import search_sites
from backend.agent.tools.search_tickets_tool import search_tickets
from backend.settings import Settings

TOOLS = [patch_facts, search_sites, search_assets, search_tickets, get_contract]


def build_model(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key.get_secret_value(),
        base_url=settings.openai_base_url,
        temperature=0,
        timeout=40,
        max_retries=0,
        max_tokens=4096,
        streaming=False,
        extra_body={"reasoning": {"max_tokens": 256}},
    )
