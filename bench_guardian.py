#!/usr/bin/env python
import datetime
import os
import random
import string

os.environ["DJANGO_SETTINGS_MODULE"] = 'guardian.testsettings'
from guardian import testsettings as settings
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

from utils import show_db_config
from django.contrib.auth.models import User, Group

NUM_OBJECTS=1000000
NUM_USERS=10000
NUM_PERMS_PER_USER=1000


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
        
        self.Model = Group
        self.perm = 'auth.change_group'

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
    show_db_config(settings, 'benchmarks')
    benchmark = Benchmark(10, 100, 100)
    benchmark.main()


if __name__ == '__main__':
    main()



