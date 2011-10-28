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

	@classmethod
	def get_for_model(cls, model):
		content_type = ContentType.objects.get_for_model(model)
		try:
			return cls.objects.filter(content_type__pk=content_type.id, object_id=model.id).all()[0]
		except IndexError:
			raise model.__class__.DoesNotExist("No trashed item found for model")

	def __unicode__(self):
		return self.content_object	
	    

class TrashableModel(models.Model):

	objects = Manager()
	trashed = models.BooleanField(_("Trashed"), default=False, db_index=True)

	def delete(self, *args, **kwargs):
		trash = False

		if kwargs.has_key("trash"):
			trash = kwargs["trash"]
			del kwargs["trash"]
		


		if not self.trashed and trash:
			trashed_item = TrashedItem(content_object=self, trashed_at=datetime.now())
			trashed_item.save()
			self.trashed = True
			self.save()		
		else:
			super(TrashableModel, self).delete(*args, **kwargs)


	def restore(self):

		trashed_item = TrashedItem.get_for_model(model=self)
		trashed_item.delete()
		
		self.trashed = False
		self.save()

	class Meta:
		abstract = True



