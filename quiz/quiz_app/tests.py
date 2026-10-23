from django.contrib.auth import get_user_model
from django.test import TestCase


class LeaderboardViewTests(TestCase):
    def test_leaderboard_url_renders_leaderboard_page(self):
        user = get_user_model().objects.create_user(username='leaderboard-test')
        self.client.force_login(user)

        response = self.client.get('/leaderboard/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard.html')
        self.assertContains(response, 'All-Time Global Leaderboard')
