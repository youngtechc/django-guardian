from datetime import datetime
from django.db import models
from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase


class TaggedProject(TaggedItemBase):
    content_object = models.ForeignKey('Project')


class ProjectUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('Project')


class ProjectGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('Project')


class Project(models.Model):
    name = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(default=datetime.now)

    tags = TaggableManager(through=TaggedProject)

    class Meta:
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.name

