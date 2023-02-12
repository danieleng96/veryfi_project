from tabnanny import check
from  django.urls import reverse
from django.shortcuts import render,redirect,get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from .forms import InputBudget, UploadForm
from .models import Upload, PersonalFinance
from veryfi import *
from .taxes import tax_bracket as tb
from django.db.models import Sum, Count
from . import config
import json
from . import analysis_commands
from django.utils.text import slugify   
from datetime import date
from .taxes import tax_bracket

def buttons(request):
    return render(request, 'mainapp/button_load.html')

#select OCR document from files to read. Needs to have a "total" section to calculate correctly
def upload_doc(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            saved_object = form.instance
            image_name = saved_object.image
            image_object = Upload.objects.get(image=image_name)
            image_object.slug = slugify(image_name)
            image_object.save()

            # slug = saved_object.slug
            slug = image_object.slug
            return render(request, 'mainapp/upload.html', {'slug':slug, "saved_object":saved_object})
    else:
        form = UploadForm
    return render(request, 'mainapp/upload.html', {'form':form})

#uses a few simple fields from OCR Read to be displayed in analysis page

def display_output(request, slug):
    #get data with slug value
    result = Upload.objects.get(slug = slug)
    file = result.image
    
    #run veryfi ocr on invoices, save entire json in category. Did not use Postgres for time and local saving purposes, but would scale using Postgres.
    veryfi_client = Client(config.client_id, config.client_secret, config.username, config.api_key)
    ocr_json = veryfi_client.process_document(file_path = f"./uploads/{file}")
    
    #parse key values for analysis from json
    if ocr_json['category']:
        result.total = ocr_json['total']
    else:
        result.total = 0
    result.category = ocr_json['category']
    result.transaction_date = ocr_json['date']
    result.ocr_json = str(json.dumps(ocr_json))
    
    result.save()
    
    return render(request, 'mainapp/display_result.html', {'total':int(ocr_json['total']),'category':str(ocr_json['category']),'date':str(ocr_json['date'])})

#needs to add option to remove specific documents
def clear_all(request):
    Upload.objects.all().delete()

#analysis based on timescale (month, year or all time as url arguments)
def analysis(request, scale = 'all'):
    
    try:
        #too hardcoded
        Upload.objects.all()
        if scale == 'month':
            totals = Upload.objects.exclude(total__isnull=True).filter(transaction_date__month = date.today().month).values('category').order_by('category').annotate(total_cost=Sum('total'))
            numbers = Upload.objects.exclude(total__isnull=True).filter(transaction_date__month = date.today().month).values('category').order_by('category').annotate(count=Count('total'))

        elif scale == 'year':
            totals = Upload.objects.exclude(total__isnull=True).filter(transaction_date__year = date.today().year).values('category').order_by('category').annotate(total_cost=Sum('total'))
            numbers = Upload.objects.exclude(total__isnull=True).filter(transaction_date__year = date.today().year).values('category').order_by('category').annotate(count=Count('total'))

        elif scale == 'all':
            totals = Upload.objects.exclude(total__isnull=True).values('category').order_by('category').annotate(total_cost=Sum('total'))
            numbers = Upload.objects.exclude(total__isnull=True).values('category').order_by('category').annotate(count=Count('total'))

        values = [round(y['total_cost'],2) for y in totals]
        keys = [x['category'] for x in totals]
        num_values = [y['count'] for y in numbers]
        num_cat = [x['category'] for x in totals]
        data = dict(zip(keys, values)) 
        script,div = analysis_commands.bokeh_pie_chart(data)
        return render(request, 'mainapp/analysis_sidebar.html', {'script':script, 'div':div, 'number_values':{'cats': num_cat, 'val':num_values, 'tot':values}, 'scale':scale})
    except:
        return redirect(reverse('upload'))

#redirects default page to analysis. if no data for analysis, returns to document input page
def redirect_analysis(request):
    return redirect(reverse('analysis',kwargs={'scale':'all'}))



#Next steps, include input finanaces

def enter_finances(request):
    if request.method == 'POST':    
        form = InputBudget(request.POST)
        if form.is_valid():
            queryset = PersonalFinance.objects.all()
            columns = [str(field.name.capitalize()).replace('_',' ') for field in PersonalFinance._meta.get_fields()]
            saved_object = form.instance
            saved_object.tax_bracket = tax_bracket(saved_object.annual_salary)
            check_entry = queryset.filter(first_name=saved_object.first_name, last_name = saved_object.last_name)
            if check_entry.exists(): # return True/False
                c = check_entry[0]
                c.first_name=saved_object.first_name
                c.last_name = saved_object.last_name
                c.monthly_expenses = saved_object.monthly_expenses
                #calculate monthly budget by annual budget - taxes
                c.monthly_budget = round(((float(saved_object.annual_salary)*(100.0-float(saved_object.tax_bracket)))/1200.0),2)
                c.annual_salary = saved_object.annual_salary
                c.state = saved_object.state
                c.tax_bracket = saved_object.tax_bracket
                name = str(saved_object.first_name)+' '+str(saved_object.last_name)
                action = f'Updated user {name}'
                c.save()
            else:
                action = 'Inserted new user!'
                saved_object.save()
            # return redirect(reverse('view_finances'))
            return render(request, 'mainapp/show_table.html',  {'queryset' : queryset, 'columns':columns, 'action':action})
    else:
        form = InputBudget
    return render(request, 'mainapp/finances_upload.html', {'form':form})

def view_finances(request):
    queryset = PersonalFinance.objects.all()
    columns = [str(field.name.capitalize()).replace('_',' ') for field in PersonalFinance._meta.get_fields()]
    action = 'Welcome to Finance viewer'
    return render(request, 'mainapp/show_table.html', {'queryset' : queryset, 'columns':columns, 'action':action})


def show_items(request):
    title = "Show all documents"
    queryset = Upload.objects.values('id','category','input_time','transaction_date','total')
    context = {
        'title':title,
        'queryset': queryset,

    }
    return render(request, "mainapp/show_table.html")

def delete_invoice(request, pk):
    queryset = Upload.objects.get(id = pk)
    if request.method == 'POST':
        queryset.delete()
        return redirect(reverse('analysis',kwargs={'scale':'all'}))
    return render(request, 'mainapp/delete_entry.html')


# def items_delete(request, id = None):
#     instance = getobject_or_404(Upload, id=id)
#     instance.delete()
#     return redirect("item_delete")s