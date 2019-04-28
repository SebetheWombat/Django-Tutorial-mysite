import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
	""" Create a question with the given 'question_text' and published the
		given number of 'days' offset to now """

	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionDetailViewTests(TestCase):
	def test_future_question(self):
		""" The detail view of a question with a pub_date in the future 
			returns a 404 non found. """
		future_question = create_question(question_text="Future question.", days=30)

		url = reverse('polls:detail', args=(future_question.id,))
		r = self.client.get(url)
		self.assertEqual(r.status_code, 404)

	def test_past_question(self):
		""" The detail view of a question with a pub_date in the past
			displays the question's text """
		past_question = create_question(question_text="Past question.", days=-5)
		url = reverse('polls:detail', args=(past_question.id,))
		r = self.client.get(url)
		self.assertContains(r, past_question.question_text)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		""" if no question exists, an appropriate message is displayed """
		r = self.client.get(reverse('polls:index'))
		self.assertEqual(r.status_code, 200)
		self.assertContains(r, "No polls are available.")
		self.assertQuerysetEqual(r.context['latest_question_list'], [])

	def test_past_question(self):
		""" Questions with a pub_date in the past are displayed on the index page """
		create_question(question_text="Past question.", days=-30)
		r = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			r.context['latest_question_list'],
			['<Question: Past question.>']
		)

	def test_future_question(self):
		""" Questions with a pub_date in the future aren't displayed on the index page """
		create_question(question_text="Future questin.", days=30)
		r = self.client.get(reverse('polls:index'))
		self.assertContains(r, "No polls are available.")
		self.assertQuerysetEqual(r.context['latest_question_list'], [])

	def test_future_and_past_questions(self):
		""" Even if both past and future questions exist, only past questions
			are displayed """

		create_question(question_text="Past question.", days=-30)
		create_question(question_text="Future question", days=30)
		r = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			r.context['latest_question_list'],
			['<Question: Past question.>']
		)

	def test_two_past_questions(self):
		""" The questions index page may display multiple questions """
		create_question(question_text="Past question 1.", days=-30)
		create_question(question_text="Past question 2.", days=-10)
		r= self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			r.context['latest_question_list'],
			['<Question: Past question 2.>', '<Question: Past question 1.>']
		)

class QuestionModelTests(TestCase):

	def test_was_published_recently_with_future_question(self):
		""" was_published_recently() returns False for questions 
			whose pub_date are in the future """
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		""" was_published_recently() returns False for questions
			whose pub_date is greater then 1 day ago """
		time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		past_question = Question(pub_date=time)
		self.assertIs(past_question.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		""" was_published_recently returns True for questions
			published up to 1 day ago """
		time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)