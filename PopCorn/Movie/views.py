from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from Movie.models import Show
from django.db import connection
from Movie.form import ReviewForm, RatingForm, SearchForm
from .serializers import *
from rest_framework import generics, filters, fields
from datetime import date
import math


# Create your views here.
def hompage(request):
    context = {}
    with connection.cursor() as cur:
        movies_query = "Select * from movie_show" \
                       " Where Status = 'R' or Status = 'U' and type = 'M' LIMIT 15"
        cur.execute(movies_query)
        context['theater_movies'] = cur.fetchall()

        tvseries_query = "Select * from movie_show " \
                         "Where Status = 'R' And type= 'T' LIMIT 15"
        cur.execute(tvseries_query)
        context['rs'] = cur.fetchall()

        movies_query = "Select * from movie_show where type= 'M'" \
                       " ORDER BY Avg_rating DESC LIMIT 15"
        cur.execute(movies_query)
        context['top_rated'] = cur.fetchall()

        most_reviewed_query = " With count_table(id,no) as " \
                              "(Select m.id,count(*) as no from movie_show m, movie_review r " \
                              "where m.type = 'M' " \
                              "and m.id = r.Show_id " \
                              "group by m.id) " \
                              " Select * from movie_show, count_table " \
                              "where movie_show.id = count_table.id " \
                              " order by no desc "
        cur.execute(most_reviewed_query)
        context['most_reviewed'] = cur.fetchall()

        movies_query = "Select * from movie_show where type= 'T'" \
                       " ORDER BY Avg_rating DESC"
        cur.execute(movies_query)
        context['tv_top_rated'] = cur.fetchall()

        most_reviewed_query = " With count_table(id,no) as " \
                              "(Select m.id,count(*) as no from movie_show m, movie_review r " \
                              "where m.type = 'T' " \
                              "and m.id = r.Show_id " \
                              "group by m.id " \
                              "order by no desc) " \
                              " Select * from movie_show, count_table " \
                              "where movie_show.id = count_table.id " \
                              " order by no desc "
        cur.execute(most_reviewed_query)
        context['tv_most_reviewed'] = cur.fetchall()
    print(context)
    context['searchform'] = SearchForm()
    return render(request, 'html/basehome.html', context)


def movies(request, filter, page):
    with connection.cursor() as cur:
        data = []
        page = str((int(page) - 1) * 10)
        if filter == 'top_rated':
            movies_query = f"Select * from movie_show where type= 'm'" \
                           f"ORDER BY Avg_rating DESC LIMIT 10 OFFSET {page}"
            cur.execute(movies_query)
        elif filter == 'all_alphabet':
            movies_query2 = f"Select * from Movie_Show where type= 'm'" \
                            f"ORDER BY Title ASC LIMIT 10 OFFSET {page}"
            cur.execute(movies_query2)
        elif filter == 'all_release_date':
            movies_query = f"Select * from Movie_Show where type= 'm'" \
                           f"ORDER BY ReleaseDate DESC LIMIT 10 OFFSET {page}"
            cur.execute(movies_query)
        elif filter == 'top_grossers':
            movies_query = f"Select * from Movie_Show where type= 'm'" \
                           f"ORDER BY Boc DESC LIMIT 10 OFFSET {page}"
            cur.execute(movies_query)
        movies_tuple = cur.fetchall()
        all_movies_query = "Select count(*) from Movie_Show";
        cur.execute(all_movies_query)
        all_mov = cur.fetchall()
        count_page = math.ceil(all_mov[0][0] / 10)
        for i in movies_tuple:
            query = "SELECT *" \
                    " FROM Movie_ShowCelebrity as msc, Celebrity_Celebrity as mc" \
                    " WHERE msc.Celebrity_id = mc.id " \
                    "AND msc.Show_id={}"
            query = query.format(i[0])
            cur.execute(query)
            Celebrity = cur.fetchall()
            mov1 = {
                'movie': i,
                'director': [],
                'producer': [],
                'writer': [],
                'actors': [],
            }
            print(Celebrity)
            for j in Celebrity:
                if j[1] == 'D':
                    mov1['director'].append(j)
                elif j[1] == 'A':
                    mov1['actors'].append(j)
                elif j[1] == 'P':
                    mov1['producer'].append(j)
                elif j[1] == 'W':
                    mov1['writer'].append(j)
            data.append(mov1)
        context = {
            "count": len(data),
            "data": data,
            "count_page": count_page,
            "count_page_range": range(1, count_page + 1),
            "filter": filter,
            'searchform': SearchForm(),
        }

        print(context['data'])
        return render(request, 'html/showlist.html', context)


def tvseries(request, filter):
    with connection.cursor() as cur:
        data = []
        if filter == 'top_rated':
            movies_query = "Select * from Movie_Show where type= 'T'" \
                           " ORDER BY Avg_rating DESC"
            cur.execute(movies_query)
        elif filter == 'all_alphabet':
            movies_query2 = "Select * from Movie_Show where type= 'T'" \
                            "ORDER BY Movie_title ASC"
            cur.execute(movies_query2)
        elif filter == 'all_release_date':
            movies_query = "Select * from Movie_Show where type= 'T'" \
                           "ORDER BY ReleaseDate DESC"
            cur.execute(movies_query)
        elif filter == 'top_grossers':
            movies_query = "Select * from Movie_Show where type= 'T'" \
                           "ORDER BY Boc DESC"
            cur.execute(movies_query)

        movies_tuple = cur.fetchall()
        for i in movies_tuple:
            query = "SELECT *" \
                    " FROM Movie_ShowCelebrity as msc, Celebrity_Celebrity as mclb" \
                    " WHERE msc.Celebrity_id = mclb.id " \
                    "AND msc.Show_id={}"
            query = query.format(i[0])
            cur.execute(query)
            Celebrity = cur.fetchall()
            mov1 = {
                'movie': i,
                'director': [],
                'producer': [],
                'writer': [],
                'actors': [],
            }
            print(Celebrity)
            for j in Celebrity:
                if j[1] == 'D':
                    mov1['director'].append(j)
                elif j[1] == 'A':
                    mov1['actors'].append(j)
                elif j[1] == 'P':
                    mov1['producer'].append(j)
                elif j[1] == 'W':
                    mov1['writer'].append(j)
            data.append(mov1)

        context = {
            "count": len(data),
            "data": data,
            'searchform': SearchForm(),
        }
        print(context['data'])
    return render(request, 'html/showlist.html', context)
    stars_query = "Select AVG(rcv.stars) " \
                  "from Movie_ratings rcv " \
                  "where rcv.movie_id = {}"
    stars_query = stars_query.format(movie_id)
    cur.execute(stars_query)
    stars = cur.fetchall()[0]
    context = {
        'reviews': reviews,
        "count": len(data),
        "data": mov1,
        'stars': stars,
        'reviewform': reviewform,
        'searchform': SearchForm()
    }
    return render(request, 'html/single_movie.html', context)


def singledetailmovie(request, movie_id):
    with connection.cursor() as cur:
        if request.method == 'POST':
            reviewform = ReviewForm(request.POST)
            ratingform = RatingForm(request.POST)
            if reviewform.is_valid():
                title = reviewform.cleaned_data['Title']
                statement = reviewform.cleaned_data['Statement']
                postquery = "Insert into Movie_Review(show_id,user_id,title,statement,PostDate) " \
                            "values " \
                            " ({},{},'{}','{}','{}')"
                postquery = postquery.format(movie_id, request.user.id, title, statement, date.today())
                cur.execute(postquery)
            if ratingform.is_valid():
                if (ratingform.cleaned_data['stars']):
                    starsrcvd = int(ratingform.cleaned_data['stars'])
                    ratingquery = f"Insert into Movie_Rating(show_id, user_id, stars) values ({movie_id},{request.user.id},{starsrcvd})"
                    cur.execute(ratingquery)
        else:
            reviewform = ReviewForm()
            ratingform = RatingForm()

        movies_query = "Select * from Movie_Show where type= 'm' and id ={}"
        movies_query = movies_query.format(movie_id)
        cur.execute(movies_query)
        movies_tuple = cur.fetchall()
        i = movies_tuple[0]
        data = []
        query = "SELECT *" \
                " FROM Movie_ShowCelebrity as msc, Celebrity_Celebrity as mclb" \
                " WHERE msc.Celebrity_id = mclb.id " \
                "AND msc.Show_id={}"
        query = query.format(i[0])
        cur.execute(query)
        Celebrity = cur.fetchall()
        mov1 = {
            'movie': i,
            'director': [],
            'producer': [],
            'writer': [],
            'actors': [],
        }
        for j in Celebrity:
            if j[1] == 'D':
                mov1['director'].append(j)
            elif j[1] == 'A':
                mov1['actors'].append(j)
            elif j[1] == 'P':
                mov1['producer'].append(j)
            elif j[1] == 'W':
                mov1['writer'].append(j)
        review_query = "Select * " \
                       "from Movie_review as rcv " \
                       "where rcv.show_id = {}"
        review_query = review_query.format(movie_id)
        cur.execute(review_query)
        reviews = cur.fetchall()
        star_ivd_query = f"Select stars from Movie_rating where user_id = {request.user.id} and show_id= {movie_id}"
        cur.execute(star_ivd_query)
        star_result = cur.fetchall()
        star_count = len(star_result)
        if (star_count == 0):
            star_ivd = None
        else:
            star_ivd = star_result[0][0]

        print('data', mov1)
    context = {
        'reviews': reviews,
        "count": len(data),
        "data": mov1,
        'reviewform': reviewform,
        'ratingform': ratingform,
        'star_count': star_count,
        "star_ivd": star_ivd,
        'searchform': SearchForm(),
    }
    print(data)
    return render(request, 'html/single_movie.html', context)
def searchbox(request):
    context = {}
    with connection.cursor() as cur:
        print(request.method)
        if request.method == 'POST':
            searchform = SearchForm(request.POST)
            if searchform.is_valid():
                query = searchform.cleaned_data['search']
                select = searchform.cleaned_data['select']
                print(query, select)
                if select == '0':
                    searchquery = "Select * from movie_show " \
                                  " where MATCH(Title) " \
                                  " AGAINST('{}' IN NATURAL LANGUAGE MODE)"
                    searchquery = searchquery.format(query)
                    cur.execute(searchquery)
                    context['shows'] = cur.fetchall()
                    searchquery = "Select * from Celebrity_celebrity " \
                                  " where MATCH(Name) " \
                                  " AGAINST('{}' IN NATURAL LANGUAGE MODE)"
                    searchquery = searchquery.format(query)
                    cur.execute(searchquery)
                    context['celeb'] = cur.fetchall()
                elif select == '1':
                    searchquery = "Select * from movie_show " \
                                  " where MATCH(Title) " \
                                  " AGAINST('{}' IN NATURAL LANGUAGE MODE) " \
                                  "AND Type = 'M' "
                    searchquery = searchquery.format(query)
                    cur.execute(searchquery)
                    context['shows'] = cur.fetchall()
                elif select == '2':
                    searchquery = "Select * from movie_show " \
                                  " where MATCH(Title) " \
                                  " AGAINST('{}' IN NATURAL LANGUAGE MODE) " \
                                  "AND Type = 'T' "
                    searchquery = searchquery.format(query)
                    cur.execute(searchquery)
                    context['shows'] = cur.fetchall()
                elif select == '3':
                    searchquery = "Select * from Celebrity_celebrity " \
                                  " where MATCH(Name) " \
                                  " AGAINST('{}' IN NATURAL LANGUAGE MODE)"
                    searchquery = searchquery.format(query)
                    cur.execute(searchquery)
                    context['celeb'] = cur.fetchall()
            context['searchform'] = SearchForm(request.POST)
        else:
            context['searchform'] = SearchForm()
    return render(request, 'html/searchresults.html', context)


def favmod(request, mov_id):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#========================================================================

class ShowListView(generics.ListCreateAPIView):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer


class ShowView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShowSerializer
    queryset = Show.objects.all()



class CelebrityListView(generics.ListCreateAPIView):
    queryset = Celebrity.objects.all()
    serializer_class = CelebritySerializer

    # serializer_class = CelebritySerializer
    # queryset = Celebrity.objects.all()

    # def get_queryset(self):
    #     awards = Award.objects.all()
    #     for award in awards:
    #         queryset = Celebrity.objects.filter(
    #             award=award
    #         )
    #     return queryset


class CelebrityView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CelebritySerializer
    queryset = Celebrity.objects.all()
    
class AwardListView(generics.ListCreateAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer


class AwardView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AwardSerializer
    queryset = Award.objects.all()


class CelebrityListView(generics.ListCreateAPIView):
    queryset = Celebrity.objects.all()
    serializer_class = CelebritySerializer


#=====================================================================================
