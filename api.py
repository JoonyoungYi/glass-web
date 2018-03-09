# -*- coding: utf-8 -*-

import json
import urllib.parse
import urllib.request

from flask import session
from models import Rating, User, Product, Alarm, LoginStatus

from config import *

###############################################################################
#
# INNER FUNCTIONS
#
###############################################################################


def get_login_status():
    return session.get('login_status')


def get_user_id():
    return session.get('user_id')


def request_get(url, data={}):
    #
    headers = {'Authorization': session.get('sessionkey', '')}
    url_values = urllib.parse.urlencode(data)
    full_url = API_BASE_URL + url + '?' + url_values

    #
    req = urllib.request.Request(full_url,
                                 headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')

    return html


def request_post(url, data={}):
    #
    headers = {'Authorization': session.get('sessionkey', '')}
    full_url = API_BASE_URL + url

    #
    values = urllib.parse.urlencode(data)
    req = urllib.request.Request(full_url,
                                 values.encode('utf-8'),
                                 headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')

    return html

###############################################################################
#
# APIS
#
###############################################################################

#


def AuthLoginFacebookApi(token):
    url = '/auth/login/facebook/'
    values = {'token': token}
    print(token)
    raw = request_post(url, values)

    raw_obj = json.loads(raw)
    session['sessionkey'] = raw_obj['sessionkey']
    session['user_id'] = raw_obj['user_id']

    if raw_obj['tutorial_finished']:
        session['login_status'] = LoginStatus.LOGIN_SUCCESS
    else:
        session['login_status'] = LoginStatus.LOGIN_TUTORIAL_UNFINISHED


def RatingDetailApi(rating_id):
    url = '/rating/detail/'
    values = {'rating_id': rating_id}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    if raw_obj.get('rating') == None:
        return None
    rating = Rating(raw_obj['rating'])
    return rating


def UserMeFeedListApi(offset):
    url = '/user/me/feed/list/'
    count = 20

    #
    values = {'offset': offset, 'count': count}
    raw = request_get(url, values)

    #
    raw_obj = json.loads(raw)
    ratings = []
    for rating_obj in raw_obj['ratings']:
        rating = Rating(rating_obj)
        ratings.append(rating)

    return ratings


def GlobalFeedListApi(offset):
    url = '/global/feed/list/'
    count = 20

    values = {'offset': offset, 'count': count}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    ratings = []
    for rating_obj in raw_obj['ratings']:
        rating = Rating(rating_obj)
        ratings.append(rating)

    return ratings


def UserRatingListApi(user_id, offset):
    url = '/user/rating/list/'
    count = 20

    values = {'user_id': user_id, 'offset': offset, 'count': count}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    ratings = []
    for rating_obj in raw_obj['ratings']:
        rating = Rating(rating_obj)
        ratings.append(rating)

    return ratings


def UserDetailApi(user_id):
    url = '/user/detail/'

    values = {'user_id': user_id}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    return User(raw_obj['user'])


def UserFollowingListApi(user_id):
    url = '/user/following/list/'
    values = {'user_id': user_id}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    users = []
    for user_obj in raw_obj.get('users', []):
        user = User(user_obj)
        if user.id == session['user_id']:
            continue
        users.append(user)
    return users


def UserFollowerListApi(user_id):
    url = '/user/follower/list/'
    values = {'user_id': user_id}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    users = []
    for user_obj in raw_obj.get('users', []):
        user = User(user_obj)
        if user.id == get_user_id():
            continue
        users.append(user)
    return users


def UserRankingListApi(user_id, product_type, offset):
    url = '/user/ranking/list/'
    lang = "ko"
    count = 20

    values = {
        'user_id': user_id,
        'offset': offset,
        'count': count,
        'lang': lang,
        'product_type': product_type
    }
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    products = []
    for j, product_obj in enumerate(raw_obj['products']):
        product = Product(product_obj)
        products.append(product)

    return products


def ComparisonListApi():
    url = '/comparison/list/'

    values = {}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    comparisons = []
    for comparison_obj in raw_obj.get('comparisons', []):
        product_a = Product(comparison_obj['product_a'])
        product_b = Product(comparison_obj['product_b'])
        comparisons.append((product_a, product_b))

    todo_number = raw_obj['step_todo_number']
    done_number = raw_obj['done_number']

    return comparisons, todo_number, done_number


def ProductDetailApi(product_id):
    url = '/product/detail/'
    lang = 'ko'

    values = {'lang': lang, 'product_id': product_id}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    product = Product(raw_obj['product'])
    return product


def ProductRatingListApi(product_id, offset):
    url = '/product/rating/list/'
    count = 20

    values = {'product_id': product_id, 'offset': offset, 'count': count}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    ratings = []
    for rating_obj in raw_obj['ratings']:
        rating = Rating(rating_obj)
        ratings.append(rating)

    return ratings


def UserMeAlarmListApi():
    url = '/user/me/alarm/list/'
    offset = 0
    count = 20

    values = {'offset': offset, 'count': count}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    alarms = []
    for alarm_obj in raw_obj['alarms']:
        alarm = Alarm(alarm_obj)
        alarms.append(alarm)

    return alarms


def RatingLikeToggleApi(rating_id):
    url = '/rating/like/toggle/'
    values = {'rating_id': rating_id}
    raw = request_post(url, values)

    raw_obj = json.loads(raw)
    return raw_obj['is_liked']


def UserFollowingToggleApi(user_id):
    url = '/user/following/toggle/'
    values = {'user_id': user_id}
    raw = request_post(url, values)

    raw_obj = json.loads(raw)
    return raw_obj['is_following']


def RatingMultiListApi(is_tutorial, product_type, offset):
    url = '/rating/multi/list/'
    count = 20

    values = {
        'is_tutorial': is_tutorial,
        'product_type': product_type,
        'offset': offset,
        'count': count
    }
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    products = []
    for product_obj in raw_obj['products']:
        product = Product(product_obj)
        products.append(product)

    todo_number = raw_obj['step_todo_number'] - raw_obj['step_done_number']
    done_number = raw_obj['done_number']

    return products, todo_number, done_number


def RatingMultiAddApi(product_id, star):
    url = '/rating/multi/add/'
    values = {'product_id': product_id, 'star': star}
    raw = request_post(url, values)

    raw_obj = json.loads(raw)
    return True


def ComparisonAddApi(win_product_id, lose_product_id):
    url = '/comparison/add/'
    values = {'win_product_id': win_product_id, 'lose_product_id': lose_product_id}
    raw = request_post(url, values)

    raw_obj = json.loads(raw)
    return True


def UserFacebookListApi():
    url = '/user/facebook/list/'
    raw = request_get(url)

    raw_obj = json.loads(raw)
    users = []
    for user_obj in raw_obj['users']:
        user = User(user_obj)
        users.append(user)
    return users


def RecommendListApi():
    url = '/recommend/list/'

    values = {'product_type': 0}
    raw = request_get(url, values)

    raw_obj = json.loads(raw)
    if raw_obj.get('products') is None:
        return []

    products = []
    for product_obj in raw_obj.get('products', []):
        product = Product(product_obj)
        products.append(product)

    return products


def AuthTutorialFinishApi():
    url = '/auth/tutorial/finish/'
    raw = request_post(url)

    session['login_status'] = LoginStatus.LOGIN_SUCCESS
    return True
