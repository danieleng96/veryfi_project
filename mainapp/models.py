from datetime import datetime
from unittest.util import _MAX_LENGTH
from django.db import models
from .config import states, expense_type
from .taxes import tax_bracket




#Next steps, add personal finance information

class PersonalFinance(models.Model):

    first_name = models.CharField(null = False, max_length = 30)
    last_name = models.CharField(null = False, max_length = 30)
    monthly_expenses = models.FloatField(null = True)
    monthly_budget = models.FloatField(null = True)
    annual_salary = models.FloatField(null = True)
    state = models.CharField(null = True, max_length = 2, choices = states)
    tax_bracket = models.IntegerField(null = True)
    create_time = models.DateTimeField(auto_now_add = True)
    update_time = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.first_name
    
    def save(self, *args, **kwargs):
        if not self.id:
            return super(PersonalFinance, self).save()
        return super(PersonalFinance, self).save()



#can add new expenses not in upload tag
class Expenses(models.Model):

    finances = models.OneToOneField(PersonalFinance, on_delete = models.CASCADE)
    category = models.CharField(null = False, max_length = 100)
    amount = models.FloatField(null = False)
    expense_type = models.CharField(null = False, max_length = 1)
    #create and effective time
    create_time = models.DateTimeField(auto_now_add = True)
    effective_time = models.DateTimeField(auto_now_add = True)

class Upload(models.Model):

    # first_name = models.OneToOneField(PersonalFinance.first_name)
    # last_name = models.OneToOneField(PersonalFinance.last_name, default = )

    image = models.ImageField(upload_to = 'images')
    ocr_json = models.TextField(default = '')
    input_time = models.DateTimeField(auto_now_add = True)
    slug = models.SlugField(unique = True, max_length = 200, null = True)
    total = models.FloatField(null = True)
    transaction_date = models.DateTimeField(null = True)
    category = models.CharField(null = True, max_length = 100)

    def save(self, *args, **kwargs):
        if not self.id:
            # self.slug = slugify(self.image)
            return super(Upload, self).save()
        return super(Upload, self).save()

    def __str__(self):
        return self.image