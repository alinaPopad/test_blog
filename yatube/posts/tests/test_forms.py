from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, User, Comment

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
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_img,
            content_type='image/jpg'
        )
        form_fields = {
            'text': 'test text',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        last_post = Post.objects.latest('id')
        print('post - ', last_post)

        #self.assertTrue(
            #Post.objects.filter(
                #text='test text',
                #group=self.group,
                #image='posts/small.jpg'
            #).exists()
        #)

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

    def test_post_details_comment_auth(self):
        comment_data = {
            'post': self.post.id,
            'text': 'первый тестовый коммент'
        }
        response = self.authorized_client.post(
            reverse(
            'posts:add_comment',
            kwargs={'post_id':self.post.pk,}
            ),
            data=comment_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk,}
            )
        )
        self.assertTrue(
            Comment.objects.filter(
            text='первый тестовый коммент'
            ).exists(), f'коммент не найден'
        )

    def test_post_detail_comment_guest(self):
        comment_data = {
            'post': self.post.pk,
            'text': 'текст для проверки'
        }
        self.guest_client.post(
            reverse(
            'posts:add_comment',
            kwargs={'post_id':self.post.pk,}
            ),
            data=comment_data,
            follow=True
        )
        self.assertFalse(
            Comment.objects.filter(
            text='текст для проверки'
            ).exists(), f'тут ничего не должно было быть'
        )
