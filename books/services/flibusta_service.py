import requests
from lxml import html
import os
from django.conf import settings


class FlibustaService:

    def __init__(self):
        self.flibusta_onion = settings.FLIBUSTA_ONION
        self.tor_proxy = {
            'http': f'socks5h://{settings.TOR_PROXY_HOST}:{settings.TOR_PROXY_PORT}',
            'https': f'socks5h://{settings.TOR_PROXY_HOST}:{settings.TOR_PROXY_PORT}'
        }
        self.session = requests.Session()
        self.session.proxies.update(self.tor_proxy)

    def search(self, query):
        if not query or not query.strip():
            return []

        try:
            search_url = f"{self.flibusta_onion}/booksearch"
            params = {'ask': query.strip()}

            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()

            tree = html.fromstring(response.content)

            results = []
            book_links = tree.xpath('//ul/li/a[contains(@href, "/b/")]')

            for link in book_links[:20]:
                title_text = link.text_content().strip()
                href = link.get('href')

                if not href or not title_text:
                    continue

                book_id = href.split('/b/')[-1].split('/')[0]

                author = 'Неизвестный автор'
                title = title_text

                if ' - ' in title_text:
                    parts = title_text.split(' - ', 1)
                    author = parts[0].strip()
                    title = parts[1].strip()

                results.append({
                    'id': book_id,
                    'title': title,
                    'author': author,
                    'url': f"{self.flibusta_onion}{href}"
                })

            return results

        except Exception as e:
            raise Exception(f"Ошибка поиска на Флибусте: {str(e)}")

    def download_book(self, book_id):
        try:
            download_url = f"{self.flibusta_onion}/b/{book_id}/fb2"

            response = self.session.get(download_url, timeout=60)
            response.raise_for_status()

            if 'application' not in response.headers.get('Content-Type', ''):
                raise Exception("Некорректный тип контента. Книга может быть недоступна.")

            filename = f"book_{book_id}.fb2"

            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                try:
                    filename = content_disposition.split('filename=')[1].strip('"')
                except:
                    pass

            temp_path = os.path.join(settings.MEDIA_ROOT, 'books', filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            with open(temp_path, 'wb') as f:
                f.write(response.content)

            return temp_path

        except Exception as e:
            raise Exception(f"Ошибка скачивания книги: {str(e)}")
