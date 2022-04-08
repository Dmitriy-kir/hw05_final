from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import Client
from ..models import Post, Comment
from .fixture import Fixture
from django.urls import reverse


class TestForms(Fixture):
    """Тестирование форм"""
    def setUp(self):
        self.auth_client = Client()
        self.guest_client = Client()
        self.auth_client.force_login(self.user1)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='test.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

    def test_check_new_post_created(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.auth_client.post(
            self.reverse_post_create,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image__contains='posts/test.gif',
            ).exists()
        )

    def test_check_editing_post(self):
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        response = self.auth_client.post(
            self.reverse_post_edit,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(id=self.post_with_group_1.id).text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.get(id=self.post_with_group_1.id).group.id,
            form_data['group']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_can_add_comment(self):
        comment_count = Comment.objects.filter(post_id=1).count()
        form_data = {
            'text': 'Test comment'
        }
        self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            comment_count + 1,
            Comment.objects.filter(post_id=1).count()
        )
        self.assertTrue(
            Comment.objects.filter(text=form_data['text'],
            ).exists()
        )

    def test_guest_user_can_add_comment(self):
        comment_count = Comment.objects.filter(post_id=1).count()
        form_data = {
            'text': 'Test comment'
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            comment_count,
            Comment.objects.filter(post_id=1).count()
        )
        self.assertFalse(
            Comment.objects.filter(text=form_data['text'],
            ).exists()
        )
