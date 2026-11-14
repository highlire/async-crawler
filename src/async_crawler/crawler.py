
import asyncio
import aiohttp
import logging


logger = logging.getLogger(__name__)

class AsyncCrawler:

    def __init__(self, max_concurrent: int = 10):

        # Проверка входного параметра
        if not isinstance(max_concurrent, int) or isinstance(max_concurrent, bool):
            raise TypeError("max_concurrent должен быть целым числом")

        if max_concurrent <= 0:
            raise ValueError("max_concurrent должен быть больше нуля")

        # Сохраняем ограничение конкурентности
        self.max_concurrent = max_concurrent

        # Создаём семафор для ограничения одновременных задач
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Настраиваем таймауты HTTP-запросов
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=15
        )

        # Создаём пул HTTP-соединений, connector/limit - кол-во соединений, semaphore - кол-во корутин
        connector = aiohttp.TCPConnector(
            limit=max_concurrent
        )

        # Создаём общую HTTP-сессию
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )

    async def fetch_url(self, url: str) -> str:

        # Проверяем входные данные
        if not isinstance(url, str):
            raise TypeError("URL должен быть строкой")

        if not url.strip():
            raise ValueError("URL не может быть пустым")

        logger.info("Начало загрузки: %s", url)

        try:
            # Получаем разрешение на выполнение запроса
            async with self.semaphore:

                # Выполняем HTTP-запрос
                async with self.session.get(url) as response:

                    # Проверяем HTTP-статус ответа
                    response.raise_for_status()

                    # Получаем HTML-контент страницы
                    html = await response.text()

                    logger.info(
                        "Успешная загрузка: %s (HTTP %s)",
                        url,
                        response.status
                    )

                    return html

        except aiohttp.ClientResponseError as error:
            logger.warning(
                "HTTP ошибка при загрузке %s: статус %s",
                url,
                error.status
            )

        except asyncio.TimeoutError:
            logger.warning(
                "Таймаут при загрузке: %s",
                url
            )

        except aiohttp.ClientError as error:
            logger.warning(
                "Сетевая ошибка при загрузке %s: %s",
                url,
                error
            )

        return ""


    
    async def fetch_urls(self, urls: list[str]) -> dict[str, str]:

        # Создаём список корутин для загрузки URL
        tasks = [
            self.fetch_url(url)
            for url in urls
        ]

        # Запускаем корутины конкурентно и ожидаем их завершения
        results = await asyncio.gather(*tasks)

        # Объединяем URL и полученные HTML в словарь
        return dict(zip(urls, results))

    async def close(self):
        await self.session.close()
