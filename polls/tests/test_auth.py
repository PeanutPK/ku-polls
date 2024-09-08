import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from polls.models import Question, Choice
from mysite import settings


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class UserAuthTest(TestCase):
    """
    Test for cases that require authentication.
    """

    def setUp(self):
        """superclass setUp creates a Client object and
        initializes a test database"""
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        self.choice = []
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            self.choice.append(choice)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can log out using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_one_user_one_vote(self):
        """One user have one vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        self.client.login(username=self.username, password=self.password)

        # get three of four choices from the choice list created in setUp
        choice1 = self.choice[0]
        choice2 = self.choice[1]
        choice3 = self.choice[2]
        # vote choice 1
        self.client.post(vote_url, {"choice": choice1.id})

        self.assertEqual(choice1.vote_set.count(), 1)
        self.assertEqual(choice2.vote_set.count(), 0)
        self.assertEqual(choice3.vote_set.count(), 0)

        # vote choice 2
        self.client.post(vote_url, {"choice": choice2.id})

        self.assertEqual(choice1.vote_set.count(), 0)
        self.assertEqual(choice2.vote_set.count(), 1)
        self.assertEqual(choice3.vote_set.count(), 0)
