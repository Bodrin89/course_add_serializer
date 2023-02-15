import json

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from first_django import settings
from vacancies.models import Vacancy, Skill


def hello(request):
    return HttpResponse('Hello world')


class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(self, request, *args, **kwargs)

        if request.method == 'GET':
            search_text = request.GET.get('text', None)
            if search_text:
                self.object_list = self.object_list.filter(text=search_text)

            #  Сортировка по text и по slug ("-text" в обратном порядке)
            # select_related оптимизирует запрос к БД (делает JOIN) работает только с ForeignKey
            # prefetch_related оптимизирует запрос к БД (делает JOIN) работает с ManyToMany
            # values_list создает каждый раз отдельный запрос, по этому для обращения к ManyToMany ко всей
            # колонке сразу использовать map(str, vacancy.skills.all())
            self.object_list = self.object_list.select_related('user').prefetch_related('skills').order_by("text",
                                                                                                           "slug")
            #  Пагинация (1 параметр - это список всех вакансий, 2 параметр - это кол-во вакансий на странице)
            paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            vacancies = []
            for vacancy in page_obj:
                vacancies.append({
                    "id": vacancy.id,
                    "text": vacancy.text,
                    "slug": vacancy.slug,
                    "status": vacancy.status,
                    "created": vacancy.created,
                    "username": vacancy.user.username,
                    # "skills": list(vacancy.skills.values_list("name", flat=True))
                    "skills": list(map(str, vacancy.skills.all()))
                })

            response = {
                "items": vacancies,
                "num_page": paginator.num_pages,
                "total": paginator.count
            }

            return JsonResponse(response, safe=False)


class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        vacancy = self.get_object()

        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
            # "skills": list(vacancy.skills.values_list("name", flat=True))
            "skills": list(map(str, vacancy.skills.all()))
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ['user', 'slug', 'text', 'status', 'created', 'skills']

    def post(self, request, *args, **kwargs):
        vacancy_data = json.loads(request.body)

        vacancy = Vacancy.objects.create(
            slug=vacancy_data['slug'],
            text=vacancy_data['text'],
            status=vacancy_data['status'],
        )

        # Обработка ошибки 404
        vacancy.user = get_object_or_404(User, pk=vacancy_data['user_id'])

        #  Добавляем созданные записи в таблицу vacancy в поле skill (ManyToMany)
        for skill in vacancy_data['skills']:
            skill_obj, created = Skill.objects.get_or_create(name=skill, defaults={"is_active": True})
            vacancy.skills.add(skill_obj)

        vacancy.save()

        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
            "skills": list(map(str, vacancy.skills.all()))
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ['slug', 'text', 'status', 'skills']

    def patch(self, request, *args, **kwargs):
        super().post(self, request, *args, **kwargs)
        vacancy_data = json.loads(request.body)

        self.object.slug = vacancy_data['slug']
        self.object.text = vacancy_data['text']
        self.object.status = vacancy_data['status']

        for skill in vacancy_data['skills']:
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Not skill found"}, status=404)
            self.object.skills.add(skill_obj)

        self.object.save()

        #  self.object.skills.all().values_list("name", flat=True)
        #  values_list Метод, который возвращает список значений поля ("name" - это
        #  название столбца в таблице) список из списков)
        # flat=True превращает этот список в плоский
        return JsonResponse({
            "id": self.object.id,
            "text": self.object.text,
            "slug": self.object.slug,
            "status": self.object.status,
            "created": self.object.created,
            "user": self.object.user_id,
            "skills": list(self.object.skills.all().values_list("name", flat=True))
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = '/'  # URL на который перенаправляет пользователя после удаления записи

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({"status": "ok"}, status=200)


class UserVacancyDetailView(View):
    def get(self, request):
        #  annotate создает новую колонку (vacancies) в которой будет созданна
        #  групировка (Count('vacancy')- подсчет вакансий из поля vacancy)
        user_qs = User.objects.annotate(vacancies=Count('vacancy'))

        paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        users = []
        for user in page_obj:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies
            })

        response = {
            "items": users,
            "totat": paginator.count,
            "num_pages": paginator.num_pages,
            "avg": user_qs.aggregate(avg=Avg('vacancies'))['avg']  # Среднее кол-во вакансий
        }

        return JsonResponse(response)
