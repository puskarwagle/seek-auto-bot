# main.py
import asyncio
import argparse
import sys

from core.bot import SeekBot  # no more circular imports
from api.main import main as start_dashboard


async def run_cli_bot():
    bot = SeekBot()
    try:
        success = await bot.start()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        await bot.stop()
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Seek Bot Runner")
    parser.add_argument("--cli", action="store_true", help="Run bot in CLI mode")
    args = parser.parse_args()

    if args.cli:
        # Run CLI bot loop
        exit_code = asyncio.run(run_cli_bot())
        sys.exit(exit_code)
    else:
        # Run FastAPI dashboard server
        start_dashboard()


if __name__ == "__main__":
    main()
