from django.core.management.base import BaseCommand
from app.models import *
from faker import Faker


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--ratio', type=int)

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        if ratio is None:
            ratio = 10000

        faker = Faker('en_US')

        users = []
        profiles = []
        for i in range(ratio):
            user = User()
            user.password = faker.password(length=8)
            user.last_login = faker.date_time()
            user.is_superuser = False
            user.username = faker.unique.user_name()
            user.first_name = faker.first_name()
            user.last_name = faker.last_name()
            user.email = faker.unique.free_email()
            user.is_staff = False
            user.is_active = True
            user.date_joined = faker.date_time()
            users.append(user)

            profile = Profile()
            profile.user = user
            profile.avatar = 'static/img/avatar.png'
            profiles.append(profile)

        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)

        del profiles

        print("__users  and profiles in db__")

        tags = []
        for i in range(ratio):
            tag = Tag()
            tag.name = faker.unique.user_name()
            tags.append(tag)

        Tag.objects.bulk_create(tags)
        print("__tags in db__")

        questions = []
        for i in range(ratio * 10):
            question = Question()
            question.title = faker.sentence()
            question.content = faker.paragraph(nb_sentences=3)
            question.author = users[i % ratio]
            question.pub_date = faker.date()
            number = faker.random_int(min=-500, max=500)
            question.rating = number
            print(number)
            questions.append(question)

        Question.objects.bulk_create(questions)

        cur_tag_id = 1
        for q in questions:
            q.tags.add(tags[cur_tag_id])
            q.tags.add(tags[(cur_tag_id + 1) % len(tags)])
            q.tags.add(tags[(cur_tag_id + 2) % len(tags)])
            cur_tag_id += 3
            cur_tag_id %= ratio

        del tags

        print("__questions in db__")

        answers = []
        for i in range(ratio * 100):
            answer = Answer()
            answer.author = users[i % ratio]
            answer.question = questions[i % (ratio * 10)]
            answer.rating = faker.random_int(min=-500, max=500)
            answer.content = faker.paragraph(nb_sentences=2)
            answer.pub_date = faker.date()
            answers.append(answer)

        Answer.objects.bulk_create(answers)
        print("__answers in db__")

        questionLikes = []
        answerLikes = []

        cnt = 0
        for user in users:
            for question in questions[:201]:
                questionLike = QuestionLike()
                questionLike.user = user
                questionLike.question = question
                if cnt % 2 == 0:
                    questionLike.value = "l"
                else:
                    questionLike.value = "d"
                questionLikes.append(questionLike)
                cnt = cnt + 1
                print("add ql")
            for answer in answers[:201]:
                answerLike = AnswerLike()
                answerLike.user = user
                answerLike.answer = answer
                if cnt % 2 == 0:
                    answerLike.value = "l"
                else:
                    answerLike.value = "d"
                answerLikes.append(answerLike)
                cnt = cnt + 1
                print("add al")

        QuestionLike.objects.bulk_create(questionLikes)
        AnswerLike.objects.bulk_create(answerLikes)
        print("__likes in db__")

