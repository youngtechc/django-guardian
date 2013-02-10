from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.utils.translation import ugettext_lazy as _

from guardian.managers import UserObjectPermissionManager
from guardian.managers import GroupObjectPermissionManager
from guardian.utils import get_anonymous_user
from guardian.utils import ClassProperty


class BaseObjectPermission(models.Model):
    """
    Abstract ObjectPermission class. Actual class should additionally define
    a ``content_object`` field and either ``user`` or ``group`` field.
    """
    permission = models.ForeignKey(Permission)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.content_object),
            unicode(getattr(self, 'user', False) or self.group),
            unicode(self.permission.codename))

    def save(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(self)
        if content_type != self.permission.content_type:
            raise ValidationError("Cannot persist permission not designed for "
                "this class (permission's type is %s and object's type is %s)"
                % (self.permission.content_type, self.content_type))
        return super(BaseObjectPermission, self).save(*args, **kwargs)

    #@ClassProperty
    #@classmethod
    #def _unique_together_attrs(cls):
        #first = 'user' if hasattr(cls, 'user') else 'group'
        #if isinstance(cls.content_object, GenericForeignKey):
            #last = 'object_pk'
        #else:
            #last = 'content_object'
        #return [first, 'permission', last]


class BaseGenericObjectPermission(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_pk = models.CharField(_('object ID'), max_length=255)
    content_object = GenericForeignKey(fk_field='object_pk')

    class Meta:
        abstract = True


class UserObjectPermissionBase(BaseObjectPermission):
    """
    **Manager**: :manager:`UserObjectPermissionManager`
    """
    user = models.ForeignKey(User)

    objects = UserObjectPermissionManager()

    class Meta:
        abstract = True
        # TODO: set properly unique_together
        #unique_together = ['user', 'permission', 'object_pk']


class UserObjectPermission(UserObjectPermissionBase, BaseGenericObjectPermission):
    pass


class GroupObjectPermissionBase(BaseObjectPermission):
    """
    **Manager**: :manager:`GroupObjectPermissionManager`
    """
    group = models.ForeignKey(Group)

    objects = GroupObjectPermissionManager()

    class Meta:
        abstract = True
        # TODO: set properly unique_together
        #unique_together = ['group', 'permission', 'object_pk']


class GroupObjectPermission(GroupObjectPermissionBase, BaseGenericObjectPermission):
    pass


# Prototype User and Group methods
setattr(User, 'get_anonymous', staticmethod(lambda: get_anonymous_user()))
setattr(User, 'add_obj_perm',
    lambda self, perm, obj: UserObjectPermission.objects.assign(perm, self, obj))
setattr(User, 'del_obj_perm',
    lambda self, perm, obj: UserObjectPermission.objects.remove_perm(perm, self, obj))

setattr(Group, 'add_obj_perm',
    lambda self, perm, obj: GroupObjectPermission.objects.assign(perm, self, obj))
setattr(Group, 'del_obj_perm',
    lambda self, perm, obj: GroupObjectPermission.objects.remove_perm(perm, self, obj))

