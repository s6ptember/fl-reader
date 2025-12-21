import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files import File
from .models import Book
from .services.flibusta_service import FlibustaService
from .services.fb2_parser import FB2Parser
from .services.reading_service import ReadingService


@require_http_methods(["GET"])
def library_view(request):
    books = Book.objects.all()
    return render(request, 'books/library.html', {'books': books})


@require_http_methods(["GET"])
def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    try:
        text = ReadingService.get_book_text(book_id)
        return render(request, 'books/reader.html', {
            'book': book,
            'text': text
        })
    except Exception as e:
        return render(request, 'books/error.html', {'error': str(e)})


@require_http_methods(["POST"])
def update_progress_view(request, book_id):
    try:
        progress = request.POST.get('progress', 0)
        ReadingService.update_progress(book_id, progress)
        return JsonResponse({'success': True, 'progress': progress})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def search_view(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': []})

    try:
        service = FlibustaService()
        results = service.search(query)
        return JsonResponse({'success': True, 'results': results})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def download_book_view(request):
    book_id = request.POST.get('book_id')
    title = request.POST.get('title', 'Без названия')
    author = request.POST.get('author', 'Неизвестный автор')

    if not book_id:
        return JsonResponse({'success': False, 'error': 'Не указан ID книги'}, status=400)

    try:
        service = FlibustaService()
        file_path = service.download_book(book_id)

        parser = FB2Parser(file_path)
        book_data = parser.parse()

        book = Book()
        book.title = book_data.get('title', title)
        book.author = book_data.get('author', author)
        book.flibusta_id = book_id

        with open(file_path, 'rb') as f:
            book.file.save(os.path.basename(file_path), File(f), save=False)

        if book_data.get('cover'):
            book.cover = book_data['cover']

        book.save()

        if os.path.exists(file_path):
            os.remove(file_path)

        return JsonResponse({
            'success': True,
            'book_id': str(book.id),
            'title': book.title,
            'author': book.author
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["DELETE", "POST"])
def delete_book_view(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)

        if book.file:
            if os.path.exists(book.file.path):
                os.remove(book.file.path)

        if book.cover:
            if os.path.exists(book.cover.path):
                os.remove(book.cover.path)

        book.delete()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
