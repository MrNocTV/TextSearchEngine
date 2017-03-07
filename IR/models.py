from django.db import models

# Create your models here.
class Doc(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    content = models.TextField()                   # content of the doc
    length = models.IntegerField(default=1)

    def __str__(self):
        return '%d' % self.id

class Term(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    content = models.CharField(max_length=250)     # content of a term, ex: shit, asshole, ...
    how_many = models.IntegerField()               # how many docs containing this term 
    idf = models.FloatField()                      # inverse document frequency

    def __str__(self):
        return '%s %d %f' % (self.content, self.how_many, self.idf)

class Entry(models.Model):
    term = models.ForeignKey(
        Term,                                       # set a many-to-one relationship with Term
        on_delete = models.CASCADE                  
    )
    tf = models.FloatField()                        # term frequency (in doc)
    doc = models.IntegerField()                     # id of doc contains term

    def __str__(self):
        return '[doc: %s, tf: %f]' % (self.doc, self.tf)


