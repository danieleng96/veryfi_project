Descriptive document:

Attached I used Veryfi's OCR document read functionality to create a Django project which can preview and perform analysis on all uploaded documents from user.
I embedded a Pyplot Bokeh graphic to show the categories of the documents and the dollar total amount. 
You can sort the file by year.

I locally host and use the default port, which will show in the urls.
I use the built in Sqlite database, and you can see my model to see the fields saved.
There is one app called mainapp, included is a requirements.txt in the veryfi_project folder.



Here is a list of urls and the order their function (I included the default port that the program runs on)


http://127.0.0.1:8000/upload/ -- used to upload new documents from drive on computer. If the form is populated, the page will refresh and display an image of the document.

http://127.0.0.1:8000/display/<slug> -- used slug of document file name. Document images save in project/uploads folder and in the database. json saves as a txt field in database. (*NOTE: if not for limited time, I would have used Postgres to handle the json files better. Choice was Sqlite because of local storage to easily zip to you)

http://127.0.0.1:8000/analysis/<str:scale>  -- will return all documents based on their timescale (args can either be 'all', 'month', or 'year'.)



Thank you
Daniel
10-24-2022
