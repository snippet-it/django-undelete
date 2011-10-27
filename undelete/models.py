from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from undelete.managers import Manager


class TrashedItem(models.Model):
	trashed_at = models.DateTimeField(_('Trashed at'), editable=False, blank=True, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
    	return self.content_object	
	    

class TrashableModel(models.Model):

	objects = Manager()
	trashed = models.BooleanField(_("Trashed"), default=False, db_index=True)

	def delete(self, *args, **kwargs, trash=True):
	    if not self.trashed and trash:
	    	trashed_item = TrashedItem(content_object=self, trashed_at=datetime.now())
	    	trashed_item.save()
	    	self.trashed = True
	    	self.save()
	    else:
			super(TrashableModel, self).delete(*args, **kwargs)


	def restore(self):

		trashed_items = TrashedItem.objects.filter(content_object=self)

		for item in trashed_items:
			item.delete()
		
		self.trashed = False
		self.save()

	class Meta:
		abstract = True



