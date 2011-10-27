from django.db import models

class Manager(models.Manager):
    ''' Query only objects which have not been trashed. '''
    def get_query_set(self):
        query_set = super(Manager, self).get_query_set()
        return query_set.filter(trashed=False)