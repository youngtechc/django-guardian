from django.test import TestCase

from guardian.compat import get_user_model
from guardian.models import Group
from guardian.shortcuts import get_objects_for_user, assign_perm

from guardian.testapp.models import Post


class BugTestCase(TestCase):

    def test_bug_report(self):
        """Tests to inspect bug report #415

            # I have an object type, we'll call it MyModel.
            There are two objects of this type: summer and winter.
            # I have a permission called read that is used by MyModel.
            # I have a group called Summer Group. Using the admin panel,
            I assigned this group the read permission on summer, but not winter.
            # I have a user, called Johnny. He does not have any permissions,
            but he does belong to Summer Group.
            # objs = get_objects_for_user(request.user, 'my app.read')
            # Given that request.user is Johnny, I would expect this to return
            only summer, but it returns both summer and winter.
        """
        perm = 'change_post'
        summer, _ = Post.objects.get_or_create(title='summer')
        winter, _ = Post.objects.get_or_create(title='winter')
        summer_group, _ = Group.objects.get_or_create(name='Summer Group')
        assign_perm(perm, summer_group, summer)
        johnny, _ = get_user_model().objects.get_or_create(username='johnny')
        johnny.groups = [summer_group]
        johnny.save()

        # Only for copy-paste, doesn't work in test runner
        # import logging
        # l = logging.getLogger('django.db.backends')
        # l.setLevel(logging.DEBUG)
        # l.addHandler(logging.StreamHandler())

        objs = get_objects_for_user(johnny, perms=perm, klass=Post)
        self.assertTrue(objs.filter(pk=summer.pk).exists())
        self.assertFalse(objs.filter(pk=winter.pk).exists())
