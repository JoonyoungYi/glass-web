# -*- coding: utf-8 -*-

from functools import wraps
import json
import os

from flask import Flask
from flask import request, session, g
from flask import redirect, url_for, abort, render_template, jsonify
from models import Rating, User, Product, Tutorial, LoginStatus
from api import AuthLoginFacebookApi, UserMeFeedListApi, RatingDetailApi, \
    UserRatingListApi, UserDetailApi, UserRankingListApi, \
    ProductDetailApi, ProductRatingListApi, UserMeAlarmListApi, \
    RatingLikeToggleApi, UserFollowingListApi, UserFollowerListApi, \
    get_login_status, UserFollowingToggleApi, RatingMultiListApi, \
    RatingMultiAddApi, get_user_id, ComparisonListApi, \
    ComparisonAddApi, UserFacebookListApi, RecommendListApi, \
    GlobalFeedListApi, AuthTutorialFinishApi

from config import *

#
app = Flask(__name__)

if SECRET_KEY is None:
    app.secret_key = os.urandom(32)
else:
    app.secret_key = SECRET_KEY


class ReverseProxied(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('SCRIPT_NAME', '')
        if script_name:
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)


def login_required(check_tutorial=True):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            login_status = get_login_status()
            if login_status is None or login_status == LoginStatus.LOGIN_FAIL:
                return redirect(url_for('login'))
            elif (check_tutorial and
                  login_status == LoginStatus.LOGIN_TUTORIAL_UNFINISHED):
                return redirect(url_for('tutorial_multi'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper


@app.errorhandler(401)
def handler_401(e):
    return redirect(url_for(g.redirect_page))


@app.route('/')
def main():
    login_status = get_login_status()
    if login_status is None or login_status == LoginStatus.LOGIN_FAIL:
        return render_template('main.html')
    elif (login_status == LoginStatus.LOGIN_TUTORIAL_UNFINISHED):
        return redirect(url_for('tutorial_multi'))
    else:
        return redirect(url_for('newsfeed'))


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/newsfeed/')
@login_required()
def newsfeed():
    #
    offset = request.args.get('offset', 0, type=int)

    #
    ratings = UserMeFeedListApi(offset)
    for j, rating in enumerate(ratings):
        rating.index = j + offset + 1

    #
    if not ratings and offset != 0:
        return ""
    elif offset == 0:
        return render_template('newsfeed.html',
                               ratings=ratings,
                               progressbar=(len(ratings) >= 20))
    else:
        return render_template('newsfeed_more.html',
                               ratings=ratings)


@app.route('/explore/')
@login_required()
def explore():
    #
    offset = request.args.get('offset', 0, type=int)

    #
    ratings = GlobalFeedListApi(offset)
    for j, rating in enumerate(ratings):
        rating.index = j + offset + 1

    #
    if not ratings and offset != 0:
        return ""
    elif offset == 0:
        return render_template('newsfeed.html',
                               ratings=ratings,
                               progressbar=(len(ratings) >= 20))
    else:
        return render_template('newsfeed_more.html',
                               ratings=ratings)


@app.route('/recommend/')
@login_required()
def recommend():
    #
    products = RecommendListApi()

    #
    if products:
        products[0].is_main = True
        for j, product in enumerate(products):
            product.index = j + 1
        return render_template('newsfeed_recommend.html',
                               products=products)
    else:
        return ""


@app.route('/product/<int:product_id>/')
@login_required()
def product(product_id):
    #
    offset = request.args.get('offset', 0, type=int)

    #
    ratings = ProductRatingListApi(product_id, offset)
    for j, rating in enumerate(ratings):
        rating.index = j + offset + 1

    #
    if not ratings and offset != 0:
        return ""
    elif offset == 0:
        product = ProductDetailApi(product_id)
        return render_template('product.html',
                               product=product,
                               ratings=ratings,
                               progressbar=(len(ratings) >= 20))
    else:
        return render_template('product_more.html',
                               ratings=ratings)


@app.route('/profile/<int:user_id>/')
@login_required()
def profile(user_id):
    #
    offset = request.args.get('offset', 0, type=int)

    #
    ratings = UserRatingListApi(user_id, offset)
    for j, rating in enumerate(ratings):
        rating.index = j + offset + 1

    #
    if not ratings and offset != 0:
        return ""
    elif offset == 0:
        user = UserDetailApi(user_id)

        beer_products = UserRankingListApi(user_id, 1, 0)
        for j, product in enumerate(beer_products):
            product.index = j + 1

        whisky_products = UserRankingListApi(user_id, 2, 0)
        for j, product in enumerate(whisky_products):
            product.index = j + 1

        return render_template('profile.html',
                               ratings=ratings,
                               user=user,
                               beer_products=beer_products[:3],
                               whisky_products=whisky_products[:3],
                               progressbar=(len(ratings) >= 20))
    else:
        return render_template('profile_more.html',
                               ratings=ratings)


@app.route('/profile/<int:user_id>/following/')
@login_required()
def following(user_id):
    #
    users = UserFollowingListApi(user_id)
    users_col = [[] for i in range(4)]
    if users:
        for j, user in enumerate(users):
            users_col[j % 4].append(user)
    else:
        users_col = None

    #
    return render_template('users.html',
                           users_col=users_col)


@app.route('/profile/<int:user_id>/follower/')
@login_required()
def follower(user_id):
    #
    users = UserFollowerListApi(user_id)
    users_col = [[] for i in range(4)]
    if users:
        for j, user in enumerate(users):
            users_col[j % 4].append(user)
    else:
        users_col = None

    #
    return render_template('users.html',
                           users_col=users_col)


@app.route('/profile/<int:user_id>/ranking/<product_type_str>/')
@login_required()
def ranking(user_id, product_type_str):
    #
    product_type = 0
    if product_type_str == 'beer':
        product_type = 1
    elif product_type_str == 'whisky':
        product_type = 2

    #
    offset = request.args.get('offset', 0, type=int)

    #
    products = UserRankingListApi(user_id, product_type, offset)
    for j, product in enumerate(products):
        product.index = j + offset + 1

    #
    if not products and offset != 0:
        return ""
    elif offset == 0:
        return render_template('ranking.html',
                               products=products,
                               progressbar=(len(products) >= 20),
                               path=request.path,
                               is_me=(get_user_id() == user_id),
                               product_type_str=product_type_str)
    else:
        return render_template('ranking_more.html',
                               products=products)


@app.route('/rating/<int:rating_id>/')
@login_required()
def rating(rating_id):
    #
    rating = RatingDetailApi(rating_id)
    return render_template('rating.html',
                           rating=rating)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get('token')
        AuthLoginFacebookApi(token)

        login_status = get_login_status()
        if login_status is None or login_status == LoginStatus.LOGIN_FAIL:
            return redirect(url_for('login'))
        elif login_status == LoginStatus.LOGIN_TUTORIAL_UNFINISHED:
            return redirect(url_for('tutorial_multi'))
        else:
            return redirect(url_for('main'))
    else:
        return render_template('login.html',
                               facebook_app_id=FACEBOOK_APP_ID)


@app.route('/tutorial/multi/')
@login_required(False)
def tutorial_multi():
    #
    login_status = get_login_status()
    if login_status == LoginStatus.LOGIN_SUCCESS:
        return redirect(url_for('main'))

    #
    offset = request.args.get('offset', 0, type=int)

    #
    products, todo_number, done_number = RatingMultiListApi(True, 0, offset)
    for j, product in enumerate(products):
        product.index = j + offset + 1

    #
    tutorial = Tutorial()
    tutorial.next_step = url_for('tutorial_comparison')
    tutorial.next_step_activated = (done_number > 10)

    #
    if not products and offset != 0:
        return ""
    elif offset == 0:
        return render_template('multi.html',
                               products=products,
                               progressbar=(len(products) >= 20),
                               path=request.path,
                               tutorial=tutorial,
                               todo_number=todo_number,
                               done_number=done_number)
    else:
        return render_template('multi_more.html',
                               products=products)


@app.route('/multi/<product_type_str>/')
@login_required()
def multi(product_type_str):
    #
    offset = request.args.get('offset', 0, type=int)

    #
    product_type = 0
    if product_type_str == 'beer':
        product_type = 1
    elif product_type_str == 'whisky':
        product_type = 2

    #
    products, todo_number, done_number = RatingMultiListApi(False, product_type, offset)
    for j, product in enumerate(products):
        product.index = j + offset + 1

    #
    if not products and offset != 0:
        return ""
    elif offset == 0:
        return render_template('multi.html',
                               products=products,
                               progressbar=(len(products) >= 20),
                               path=request.path,
                               todo_number=todo_number,
                               done_number=done_number)
    else:
        return render_template('multi_more.html',
                               products=products)


@app.route('/comparison/')
@login_required()
def comparison():
    #
    comparisons, todo_number, done_number = ComparisonListApi()

    #
    return render_template('comparison.html',
                           product_a=comparisons[0][0],
                           product_b=comparisons[0][1],
                           todo_number=todo_number,
                           done_number=done_number)


@app.route('/tutorial/comparison/')
@login_required(False)
def tutorial_comparison():
    #
    login_status = get_login_status()
    if login_status == LoginStatus.LOGIN_SUCCESS:
        return redirect(url_for('main'))

    #
    comparisons, todo_number, done_number = ComparisonListApi()

    #
    tutorial = Tutorial()
    tutorial.prev_step = url_for('tutorial_multi')
    tutorial.next_step = url_for('tutorial_follow')
    tutorial.next_step_activated = (done_number > 10)

    #
    return render_template('comparison.html',
                           product_a=comparisons[0][0],
                           product_b=comparisons[0][1],
                           todo_number=todo_number,
                           done_number=done_number,
                           tutorial=tutorial)


@app.route('/tutorial/follow/')
@login_required(False)
def tutorial_follow():
    #
    login_status = get_login_status()
    if login_status == LoginStatus.LOGIN_SUCCESS:
        return redirect(url_for('main'))

    #
    users = UserFacebookListApi()
    users_col = [[] for i in range(4)]
    if users:
        for j, user in enumerate(users):
            users_col[j % 4].append(user)
    else:
        users_col = None

    #
    tutorial = Tutorial()
    tutorial.prev_step = url_for('tutorial_comparison')
    tutorial.next_step = url_for('newsfeed')
    tutorial.next_step_activated = True

    #
    AuthTutorialFinishApi()

    #
    return render_template('users.html',
                           users_col=users_col,
                           tutorial=tutorial)


@app.route('/alarm/')
@login_required()
def alarm():
    #
    alarms = UserMeAlarmListApi()

    #
    return render_template('alarm.html',
                           alarms=alarms)


@app.route('/rating/like/toggle/', methods=['POST'])
@login_required()
def rating_like_toggle():
    #
    rating_id = request.form.get('rating_id', type=int)
    is_liked = RatingLikeToggleApi(rating_id)

    return jsonify(rating_id=rating_id,
                   is_liked=is_liked)


@app.route('/user/following/toggle/', methods=['POST'])
@login_required(False)
def user_following_toggle():
    #
    user_id = request.form.get('user_id', type=int)
    is_following = UserFollowingToggleApi(user_id)

    return jsonify(user_id=user_id,
                   is_following=is_following)


@app.route('/multi/add/', methods=['POST'])
@login_required(False)
def multi_add():
    #
    product_id = request.form.get('product_id', type=int)
    star = request.form.get('star', type=int)
    success = RatingMultiAddApi(product_id, star)

    return jsonify(product_id=product_id,
                   star=star,
                   success=success)


@app.route('/comparison/add/', methods=['POST'])
@login_required(False)
def comparison_add():
    #
    win_product_id = request.form.get('win_product_id', type=int)
    lose_product_id = request.form.get('lose_product_id', type=int)
    success = ComparisonAddApi(win_product_id, lose_product_id)

    return jsonify(success=success)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
