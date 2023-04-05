from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testUser')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_desc',
        )
        cls.new_group = Group.objects.create(
            title='new_title',
            slug='new_slug',
            description='new_desc',
        )
        cls.post = Post.objects.create(
            text='test text',
            group=cls.group,
            author=cls.user,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_fields = {
            'text': 'test text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text='test text',).exists())

    def test_post_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test text1',
            'group': self.new_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        mod_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(1,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(
            mod_post.text,
            self.post.text,
            'text не изменился'
        )
        self.assertNotEqual(
            mod_post.group,
            self.post.group,
            'group не изменилась'
        )
        self.assertTrue(Post.objects.filter(text='test text1',).exists())
