from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from .playqueue import PlayQueue


class MockSong:

    def __init__(self, id):
        self.id = id


class SessionTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_append(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song = MockSong(3)

        queue = PlayQueue(request)
        queue.append(song)

        self.assertEqual(queue.queue, [3])

    def test_clear(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song = MockSong(3)

        queue = PlayQueue(request)
        queue.append(song)
        queue.clear()

        self.assertRaises(KeyError, lambda: request.session['play_queue'])

    def test_remove(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song1 = MockSong(3)
        song2 = MockSong(4)
        song3 = MockSong(5)
        queue = PlayQueue(request)
        queue.append(song1)
        queue.append(song2)
        queue.append(song3)

        queue.remove(0)
        self.assertEqual(queue.queue, [4, 5])

    def test_prepend(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song1 = MockSong(3)
        song2 = MockSong(4)
        song3 = MockSong(5)
        queue = PlayQueue(request)
        queue.append(song1)
        queue.append(song2)
        queue.prepend(song3)

        self.assertEqual(queue.queue, [5, 3, 4])

    def test_extend(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song1 = MockSong(3)
        song2 = MockSong(4)
        queue = PlayQueue(request)
        queue.append(song1)
        queue.append(song2)
        queue.extend([10, 11])

        self.assertEqual(queue.queue, [3, 4, 10, 11])

    def test_exchange(self):
        request = self.factory.get('accounts/')
        self.add_session_to_request(request)
        song1 = MockSong(3)
        song2 = MockSong(4)
        queue = PlayQueue(request)
        queue.append(song1)
        queue.append(song2)

        queue.exchange([20, 26])

        self.assertEqual(queue.queue, [20, 26])
