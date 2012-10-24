#!/usr/bin/env python
import datetime
import os
import random
import string
import sys

abspath = lambda *p: os.path.abspath(os.path.join(*p))

THIS_DIR = abspath(os.path.dirname(__file__))
ROOT_DIR = abspath(THIS_DIR, '..')

# so the preferred guardian module is one within this repo and
# not system-wide
sys.path.insert(0, ROOT_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = 'benchmarks.settings'
from benchmarks import settings
from guardian.shortcuts import assign

settings.DJALOG_LEVEL = 40
settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sites',
    'guardian',
)

from utils import show_settings
from django.contrib.auth.models import User
from benchmarks.models import TestModel

USERS_COUNT = 20
OBJECTS_COUNT = 100
OBJECTS_WIHT_PERMS_COUNT = 100

def random_string(length=25, chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for i in range(length))


class Call(object):
    def __init__(self, args, kwargs, start=None, finish=None):
        self.args = args
        self.kwargs = kwargs
        self.start = start
        self.finish = finish

    def delta(self):
        return self.finish - self.start


class Timed(object):

    def __init__(self, action=None):
        self.action = action

    def __call__(self, func):

        if not hasattr(func, 'calls'):
            func.calls = []

        def wrapper(*args, **kwargs):
            if self.action:
                print(" -> [%s]" % self.action)
            start = datetime.datetime.now()
            call = Call(list(args), dict(kwargs), start)
            try:
                return func(*args, **kwargs)
            finally:
                call.finish = datetime.datetime.now()
                func.calls.append(call)
                if self.action:
                    print(" -> [%s] Done (Total time: %s)" % (self.action, 
                        call.delta()))
        return wrapper


class Benchmark(object):

    def __init__(self, users_count, objects_count, objects_with_perms_count):
        self.users_count = users_count
        self.objects_count = objects_count
        self.objects_with_perms_count = objects_with_perms_count
        
        self.Model = TestModel
        self.perm = 'auth.change_testmodel'

    def prepare_db(self):
        from django.core.management import call_command
        call_command('syncdb', interactive=False)

    @Timed("Creating users")
    def create_users(self):
        User.objects.bulk_create(User(username=random_string().capitalize())
            for x in range(self.users_count))

    @Timed("Creating objects")
    def create_objects(self):
        Model = self.Model
        Model.objects.bulk_create(Model(name=random_string(20))
            for x in range(self.objects_count))

    @Timed("Grant permissions")
    def grant_perms(self):
        ids = range(1, self.objects_count)
        for user in User.objects.iterator():
            for x in xrange(self.objects_with_perms_count):
                obj = self.Model.objects.get(id=random.choice(ids))
                self.grant_perm(user, obj, self.perm)

    def grant_perm(self, user, obj, perm):
        assign(perm, user, obj)

    @Timed("Check permissions")
    def check_perms(self):
        ids = range(1, self.objects_count)
        for user in User.objects.iterator():
            for x in xrange(self.objects_with_perms_count):
                obj = self.Model.objects.get(id=random.choice(ids))
                self.check_perm(user, obj, self.perm)

    def check_perm(self, user, obj, perm):
        user.has_perm(perm, obj)

    @Timed("Benchmark")
    def main(self):
        self.prepare_db()
        self.create_users()
        self.create_objects()
        self.grant_perms()
        self.check_perms()


def main():
    show_settings(settings, 'benchmarks')
    benchmark = Benchmark(USERS_COUNT, OBJECTS_COUNT, OBJECTS_WIHT_PERMS_COUNT)
    benchmark.main()


if __name__ == '__main__':
    main()



