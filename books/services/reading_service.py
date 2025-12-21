from ..models import Book
from .fb2_parser import FB2Parser


class ReadingService:

    @staticmethod
    def get_book_text(book_id):
        try:
            book = Book.objects.get(id=book_id)
            parser = FB2Parser(book.file.path)
            data = parser.parse()
            return data.get('text', '')
        except Book.DoesNotExist:
            raise Exception("Книга не найдена")
        except Exception as e:
            raise Exception(f"Ошибка при чтении книги: {str(e)}")

    @staticmethod
    def update_progress(book_id, progress):
        try:
            book = Book.objects.get(id=book_id)
            progress_value = max(0, min(100, int(progress)))
            book.reading_progress = progress_value
            book.save(update_fields=['reading_progress'])
            return True
        except Book.DoesNotExist:
            raise Exception("Книга не найдена")
        except ValueError:
            raise Exception("Некорректное значение прогресса")
        except Exception as e:
            raise Exception(f"Ошибка при обновлении прогресса: {str(e)}")

    @staticmethod
    def get_reading_settings(book_id):
        try:
            book = Book.objects.get(id=book_id)
            return {
                'progress': book.reading_progress,
                'title': book.title,
                'author': book.author
            }
        except Book.DoesNotExist:
            raise Exception("Книга не найдена")
