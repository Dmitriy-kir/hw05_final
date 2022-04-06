import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class Fixture(TestCase):
    """Фиксатуры для тестирования"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.user3 = User.objects.create_user(username='user3')
        Follow.objects.create(user=cls.user1, author=cls.user3)
        cls.group = Group.objects.create(
            title='test group',
            slug='test',
            description='test description',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post_with_group_1 = Post.objects.create(
            author=cls.user1,
            text='test post 1 with group',
            group=cls.group,
            image=cls.uploaded
        )
        posts_with_group = list(Post(
            author=cls.user1,
            group=cls.group,
            text='Test post {0} with group'.format(i)) for i in range(50)
        )
        cls.posts_with_group = Post.objects.bulk_create(posts_with_group)
        posts_without_group = list(Post(
            author=cls.user1,
            text='Test post {0} with group'.format(i)) for i in range(50)
        )
        cls.posts_without_group = Post.objects.bulk_create(posts_without_group)
        posts_with_group_and_image = list(Post(
            author=cls.user1,
            group=cls.group,
            image=cls.uploaded,
            text='Test post {0} with group and image'.format(i))
            for i in range(50)
        )
        cls.posts_with_group_and_image = Post.objects.bulk_create(
            posts_with_group_and_image
        )
        cls.reverse_index = reverse('posts:index')
        cls.reverse_group_list = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.reverse_profile = reverse(
            'posts:profile',
            kwargs={'username': cls.user1.username}
        )
        cls.reverse_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post_with_group_1.id}
        )
        cls.reverse_post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post_with_group_1.id}
        )
        cls.reverse_post_create = reverse('posts:post_create')
        cls.expect_templates = {
            cls.reverse_index: 'posts/index.html',
            cls.reverse_group_list: 'posts/group_list.html',
            cls.reverse_profile: 'posts/profile.html',
            cls.reverse_post_detail: 'posts/post_detail.html',
            cls.reverse_post_edit: 'posts/create_edit_post.html',
            cls.reverse_post_create: 'posts/create_edit_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
