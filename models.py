# -*- coding: utf-8 -*-
import datetime, json

def get_left_time_str(created_datetime):
    left_timestamp = datetime.datetime.now().timestamp() - (created_datetime/1000)
    if left_timestamp < 60:
        return "Just now"
    elif left_timestamp < 60*60:
        return "%d minute before" % int(left_timestamp / 60)
    elif left_timestamp < 60*60*24:
        return "%d hour before" % int(left_timestamp / (60*60))
    elif left_timestamp < 60*60*24*30:
        return "%d day before" % int(left_timestamp / (60*60*24))
    elif left_timestamp < 60*60*24*367:
        return "%d month before" % int(left_timestamp / (60*60*24*30))
    else :
        return "%d year before" % int(left_timestamp / (60*60*24*365))

class Rating:
    def __init__(self, rating_obj):
        
        self.id = rating_obj['id']
        self.time = get_left_time_str(rating_obj['created_datetime'])
        self.message = rating_obj['message']        

        if rating_obj.get('is_liked'):
            self.is_liked = rating_obj['is_liked']
        if rating_obj.get('star'):
            self.star = rating_obj['star']
        if rating_obj.get('image'):
            self.image_url = rating_obj['image']['small']['url']

        #######        
        if rating_obj.get('like_number') != None:
            self.like_number = rating_obj['like_number']
        elif rating_obj.get('like_users') != None:            
            users = []
            for user_obj in rating_obj.get('like_users'):
                users.append(User(user_obj))
            self.like_users = users
            self.like_number = len(users)

        #######
        if rating_obj.get('comment_number') != None:
            self.comment_number = rating_obj['comment_number']
        elif rating_obj.get('comments') != None:            
            comments = []
            for comment_obj in rating_obj.get('comments'):
                comments.append(Comment(comment_obj))
            self.comments = comments
            self.comment_number = len(comments)

        #######
        if rating_obj.get('user'):
            self.user = User(rating_obj['user'])
        if rating_obj.get('product'):
            self.product = Product(rating_obj['product'])


class User:
    def __init__(self, user_obj):
        self.id = user_obj['id']
        self.name = user_obj['name']
        if user_obj.get('image') != None:
            self.image_url = user_obj['image']['small']['url']
        elif user_obj.get('image_url') != None:
            self.image_url = user_obj['image_url']
        if user_obj.get('is_blocking') != None:
            self.is_blocking = user_obj.get('is_blocking')
        if user_obj.get('about') != None:
            self.about = user_obj.get('about')
        if user_obj.get(u'following_number') != None:
            self.following_number = user_obj.get(u'following_number')
        if user_obj.get(u'follower_number') != None:
            self.follower_number = user_obj.get(u'follower_number')
        if user_obj.get('is_me') != None:
            self.is_me = user_obj.get('is_me')
        if user_obj.get('is_following') != None:
            self.is_following = user_obj.get('is_following')
        if user_obj.get('matching') != None:
            self.matching = user_obj.get('matching')

class Product:
    def __init__(self, product_obj):

        self.id = product_obj['id']
        self.name = product_obj['name']
        if product_obj.get('brand') != None:
            self.brand = product_obj.get('brand')
        if product_obj.get('chosen_image') != None:
            self.chosen_image_url = product_obj.get('chosen_image')['small']['url']
        if product_obj.get('like_users') != None:
            users = []
            for user_obj in product_obj.get('like_users'):
                users.append(User(user_obj))
            self.like_users = users
        if product_obj.get('manager') != None:
            self.manager = Manager(product_obj.get('manager'))
        if product_obj.get('image') != None:
            self.image_url = product_obj.get('image')['small']['url']
        if product_obj.get('star') != None:
            self.star = product_obj['star']
        if product_obj.get('last_rating') != None:
            self.last_rating = Rating(product_obj['last_rating'])
        if product_obj.get('top_percent') != None:
            self.top_percent = product_obj.get('top_percent')

class Comment:
    def __init__(self, comment_obj):
        self.time = get_left_time_str(comment_obj['created_datetime'])
        self.message = comment_obj['message']    
        self.user = User(comment_obj['user'])


class Manager:
    def __init__(self, manager_obj):
        self.id = manager_obj['id']
        self.user = User(manager_obj)
        self.message = manager_obj['message']


class Alarm:
    def __init__(self, alarm_obj):
        self.id = alarm_obj['id']        
        if alarm_obj.get('image_url') != None :
            self.image_url = alarm_obj['image_url']
        self.time = get_left_time_str(alarm_obj['created_datetime'])
        self.type = alarm_obj['type']
        self.data = alarm_obj['data']
        
        if self.type == 1:
            self.user_name = self.data['user_name']
            self.rating_id = self.data['rating_id']
        elif self.type == 2:
            self.user_name = self.data['user_name']
            self.user_id = self.data['user_id']
        elif self.type == 3:
            self.user_name = self.data['user_name']
            self.user_id = self.data['user_id']
        elif self.type == 4:
            self.user_name = self.data['user_name']
            self.rating_id = self.data['rating_id']
        elif self.type == 5:
            self.user_name = self.data['user_name']
            self.rating_id = self.data['rating_id']
            self.rating_user_name = self.data['rating_user_name']
        elif self.type == 6:
            self.msg = self.data['msg']
            self.url = self.data['url']


class Tutorial:
    def __init__(self):
        pass

class LoginStatus:
    LOGIN_FAIL, LOGIN_TUTORIAL_UNFINISHED, LOGIN_SUCCESS = range(3)

