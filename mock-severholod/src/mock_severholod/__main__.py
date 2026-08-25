import uvicorn

from mock_severholod.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "mock_severholod.app:app",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    main()
