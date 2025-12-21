import zipfile
import base64
from io import BytesIO
from lxml import etree
from PIL import Image
from django.core.files.base import ContentFile


class FB2Parser:

    def __init__(self, file_path):
        self.file_path = file_path
        self.ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}

    def parse(self):
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read()

            if content[:2] == b'PK':
                with zipfile.ZipFile(BytesIO(content)) as zf:
                    fb2_file = None
                    for name in zf.namelist():
                        if name.endswith('.fb2'):
                            fb2_file = name
                            break
                    if fb2_file:
                        content = zf.read(fb2_file)

            tree = etree.fromstring(content)

            title = self._get_title(tree)
            author = self._get_author(tree)
            cover_data = self._get_cover(tree)
            text = self._get_text(tree)

            return {
                'title': title,
                'author': author,
                'cover': cover_data,
                'text': text
            }
        except Exception as e:
            raise Exception(f"Ошибка при парсинге FB2: {str(e)}")

    def _get_title(self, tree):
        title_elem = tree.find('.//fb:book-title', self.ns)
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        return 'Без названия'

    def _get_author(self, tree):
        first_name = tree.find('.//fb:author/fb:first-name', self.ns)
        last_name = tree.find('.//fb:author/fb:last-name', self.ns)
        middle_name = tree.find('.//fb:author/fb:middle-name', self.ns)

        author_parts = []
        if first_name is not None and first_name.text:
            author_parts.append(first_name.text.strip())
        if middle_name is not None and middle_name.text:
            author_parts.append(middle_name.text.strip())
        if last_name is not None and last_name.text:
            author_parts.append(last_name.text.strip())

        return ' '.join(author_parts) if author_parts else 'Неизвестный автор'

    def _get_cover(self, tree):
        coverpage = tree.find('.//fb:coverpage/fb:image', self.ns)
        if coverpage is None:
            return None

        href = coverpage.get('{http://www.w3.org/1999/xlink}href')
        if not href:
            return None

        href = href.lstrip('#')

        binary = tree.find(f'.//fb:binary[@id="{href}"]', self.ns)
        if binary is None or not binary.text:
            return None

        try:
            image_data = base64.b64decode(binary.text.strip())
            image = Image.open(BytesIO(image_data))

            max_size = (400, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            output = BytesIO()
            image_format = image.format if image.format else 'JPEG'
            image.save(output, format=image_format)
            output.seek(0)

            return ContentFile(output.read(), name='cover.jpg')
        except Exception:
            return None

    def _get_text(self, tree):
        body = tree.find('.//fb:body', self.ns)
        if body is None:
            return ''

        sections = []
        for section in body.findall('.//fb:section', self.ns):
            section_text = self._extract_section_text(section)
            if section_text:
                sections.append(section_text)

        return '\n\n'.join(sections)

    def _extract_section_text(self, section):
        texts = []

        for elem in section.iter():
            if elem.tag in ['{http://www.gribuser.ru/xml/fictionbook/2.0}p',
                           '{http://www.gribuser.ru/xml/fictionbook/2.0}title']:
                if elem.text:
                    texts.append(elem.text.strip())

        return '\n'.join(texts)
