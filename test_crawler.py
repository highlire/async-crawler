
import asyncio
import logging
import time

from src.async_crawler.crawler import AsyncCrawler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


async def main():

    crawler = AsyncCrawler(max_concurrent=3)

    urls = [
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/3",
        "https://httpbin.org/delay/4",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/3",
    ]

    try:
        start_time = time.perf_counter()

        results = await crawler.fetch_urls(urls)

        elapsed = time.perf_counter() - start_time

        for url, html in results.items():
            print(f"{url}: {len(html)} символов")

        print(f"\nОбщее время: {elapsed:.2f} секунд")
        print(f"Успешных загрузок: {sum(bool(x) for x in results.values())}")
        print(f"Всего URL: {len(results)}")

    finally:
        await crawler.session.close()


if __name__ == "__main__":
    asyncio.run(main())
