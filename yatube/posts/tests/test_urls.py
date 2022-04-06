from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='test group',
            slug='test',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            text='test post',
            group=cls.group,
        )
        cls.expect_for_guest = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user1.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        )
        cls.expect_for_auth = {
            '/create/': 'posts/create_edit_post.html',
        }
        cls.url_test_edit = f'/posts/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.auth_client1 = Client()
        self.auth_client1.force_login(URLTests.user1)
        self.auth_client2 = Client()
        self.auth_client2.force_login(self.user2)

    def test_urls_for_all(self):
        """Адреса доступны всем"""
        for adress, template in URLTests.expect_for_guest:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_auth(self):
        """Адреса доступны авторизованному"""
        for adress in URLTests.expect_for_auth.keys():
            with self.subTest(adress=adress):
                response = self.auth_client1.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.guest_client.get('/create/', follow=True)
                self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_for_auth_author(self):
        """Проверка доступности редактирования поста, только автору"""
        response = self.auth_client1.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('/posts/200/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_template_for_all(self):
        """Шаблоны для гостя"""
        for adress, template in URLTests.expect_for_guest:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_template_for_auth(self):
        """Шаблоны для авторизованного"""
        for adress, template in URLTests.expect_for_auth.items():
            with self.subTest(adress=adress):
                response = self.auth_client1.get(adress)
                self.assertTemplateUsed(response, template)

    def test_add_comment_only_auth_user(self):
        """Проверка, что комментировать
        пост могут только авторизованные пользователи
        """
        '/auth/login/?next=/posts/2/comment/'
        view = reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id},
        )
        response = self.auth_client1.get(view)
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )
        response = self.guest_client.get(view, follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    def test_404_get_custom_template(self):
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
