from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Noname')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_disc',
        )
        cls.group2 = Group.objects.create(
            title='test_title2',
            slug='test_slug2',
            description='test_disc2',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='test text',
            id=1,

        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'Noname'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertContains(response, '<img')

    def test_context_post_create(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_post_edit(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_post_detail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        post_new = response.context['post']
        self.assertEqual(post_new.text, self.post.text)
        self.assertEqual(post_new.author, self.post.author)
        self.assertEqual(post_new.group, self.post.group)

    def test_context_group_list(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        obj_new = response.context['page_obj'][0]
        group_new = response.context['group']
        self.assertEqual(obj_new.id, self.post.id)
        self.assertEqual(group_new.slug, self.group.slug)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        obj = response.context['page_obj']
        self.assertEqual(obj[0].id, self.post.id)

    def test_context_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        obj_new = response.context['page_obj'][0]
        profile_new = response.context['author']
        self.assertEqual(obj_new.id, self.post.id)
        self.assertEqual(profile_new, self.user)

    def test_create_new_post(self):
        reverses = [reverse('posts:index'),
                    reverse('posts:group_list',
                            kwargs={'slug': self.group.slug}),
                    reverse('posts:profile',
                            kwargs={'username': self.user.username})
                    ]
        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                response_post = response.context['page_obj'][0]
                self.assertEqual(response_post.id, self.post.id)

        response_group2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug}))
        response_post_group2 = response_group2.context['page_obj']
        self.assertEqual(len(response_post_group2), 0)

    def test_index_cache(self):
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.all().delete()
        response_1 = self.authorized_client.get(
            reverse('posts:index'))
        cache.clear()
        response_2 = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response_1.content)
        self.assertNotEqual(response_1.content, response_2.content)


POSTS_AMOUNT = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Noname')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_disc',
        )
        Post.objects.bulk_create(
            Post(
                author=cls.user,
                group=cls.group,
                text=f'post N{i}',
            )
            for i in range(POSTS_AMOUNT)
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create_user(username='P_test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_contains(self):

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'Noname'}): 'posts/profile.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
