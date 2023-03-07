from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import permission_classes, api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from first_django import settings
from vacancies.models import Vacancy, Skill
from vacancies.permissions import VacancyCreatePermission
from vacancies.serializers import VacancyDetailSerializer, VacancyListSerializer, VacancyCreateSerializer, \
    VacancyUpdateSerializer, VacancyDestroySerializer, SkillSerializer


def hello(request):
    return HttpResponse('Hello world')


@extend_schema_view(
    list=extend_schema(description="Retrieve skill list", summary="Skill list"),
    create=extend_schema(description="Retrieve skill create", summary="Skill create")
)
class SkillsViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class VacancyListView(ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyListSerializer

    @extend_schema(
        description="Retrieve vacancy list",  # подробное описание view
        summary="Vacancy list"  # краткое описание view
    )
    def get(self, request, *args, **kwargs):
        vacancy_text = request.GET.get('text', None)
        # Поиск в таблице Vacancy во всех полях по вхождению подстроки в строку
        if vacancy_text:
            self.queryset = self.queryset.filter(text__icontains=vacancy_text)

        # # Поиск по связанной таблице Skill по полю name по вхождению подстроки в строку
        # # Метод filter по умолчанию работает как "И"
        # skill_name = request.GET.get('skill', None)
        # if skill_name:
        #     self.queryset = self.queryset.filter(skills__name__icontains=skill_name)

        #  Поиск по связанной таблице Skill по полю name по вхождению подстроки в строку с
        #  использованием "ИЛИ" в списке
        skills = request.GET.getlist('skill', None)  # getlist позволяет достать из GET целый список, простой get
        # вернет только первый элемент
        if skills:
            skill_q = None
            for skill in skills:
                if skill_q is None:
                    skill_q = Q(skills__name__icontains=skill)  # Q это служебный класс для сбора условий фильтрации
                else:
                    skill_q |= Q(skills__name__icontains=skill)
            if skill_q:
                self.queryset = self.queryset.filter(skill_q)

        return super().get(request, *args, **kwargs)


class VacancyDetailView(RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer
    permission_classes = [IsAuthenticated]


class VacancyCreateView(CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyCreateSerializer
    permission_classes = [IsAuthenticated, VacancyCreatePermission]


class VacancyUpdateView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyUpdateSerializer


class VacancyDeleteView(DestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDestroySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_vacancies(request):
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


class VacancyLikeView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer
    http_method_names = ["put"]  # метод, который будет отображаться в swagger

    @extend_schema(deprecated=True)  # deprecated - помечает в swagger метод как устаревший
    def put(self, request, *args, **kwargs):
        # pk__in Это фильтрация по pk который входит в список
        # F Это класc который достает значение поля. update - обновляет значение поля 'likes'
        Vacancy.objects.filter(pk__in=request.data).update(likes=F('likes') + 1)
        return JsonResponse(
            VacancyDetailSerializer(Vacancy.objects.filter(pk__in=request.data), many=True).data,
            safe=False
        )
