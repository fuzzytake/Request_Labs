import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Book

BOOKS_PER_SHELF = 8

'''
# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 
'''


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    # @TODO: Write a route that retrieves all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    '''

    @app.route('/books', methods=['GET'])
    def get_books():

        books = Book.query.all()

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        formatted_books = [book.format() for book in books]
        current_books = formatted_books[start:end]

        return jsonify({
            'success': True,
            'books': current_books,
            'total_books': len(formatted_books)
        })

    '''
    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    '''

    @app.route('/books/<int:book_id>')
    def get_specific_book(book_id):
        book = Book.query.filter(Book.id == book_id).one_or_none()

        if book is None:
            abort(404)

        else:
            return jsonify({
                'success': True,
                'book': book.format()
            })

    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_book(book_id):

        body = request.get_json()

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            if book is None:
                abort(404)

            if 'rating' in body:
                book.rating = int(body.get('rating'))

            book.update()

            return jsonify({
                'success': True,
                'id': book.id
            })

        except:
            abort(400)

    '''
    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    
    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
    '''

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none() #make sure the book exist

            if book is None:
                abort(404)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify({
                'success': True,
                'deleted': book_id,
                'bookw': current_books,
                'total_books': len(Book.query.all()) #keep pagination updated
            })
        except:
            abort(422)

    '''
    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    '''

    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()

        new_title = body.get('title', None)
        new_author = body.get('author', None)
        new_rating = body.get('rating', None)
        search = body.get('search', None)

        try:
            if search:
                selection = Book.query.order_by(Book.id).filter(Book.title.ilike('%{}%'.format(search)))
                current_books = paginate_books(request, selection)

                return jsonify({
                    'success': True,
                    'books': current_books,
                    'total_books': len(selection.all())
                })

            else:
                book = Book(title=new_title, author=new_author, rating=new_rating)
                book.insert()

                selection = Book.query.order_by(Book.id).all()
                current_books = paginate_books(request, selection)

                return jsonify({
                    'success': True,
                    'created': book.id,
                    'books': current_books,
                    'total_books': len(Book.query.all())
                })

        except:
            abort(422)

    # @TODO: Review the above code for route handlers.
    #        Pay special attention to the status codes used in the aborts since those are relevant for this task!

    # @TODO: Write error handler decorators to handle AT LEAST status codes 400, 404, and 422.

    # TEST: Practice writing curl requests. Write some requests that you know will error in expected ways.
    #       Make sure they are returning as expected. Do the same for other misformatted requests or requests missing data.
    #       If you find any error responses returning as HTML, write new error handlers for them.
    # 1xx Informational / 2xx Success / 3xx Redirection / 4xx Client Error / 5xx Server Error

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app

'''
curl http://127.0.0.1:5000/books/8 -X PATCH -H "Content-Type: application/json" -d '{"rating":"1"}' 

'''

