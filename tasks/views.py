from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import openpyxl
from django.http import HttpResponse, FileResponse, JsonResponse
from django.utils.encoding import smart_str
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from zipfile import ZipFile
import os
import shutil



@login_required(login_url="/users/login/")
def remupc_view(request):
    if request.method == "POST":
        first_file = request.FILES.get('first_file')  # Get uploaded file
        second_files = request.FILES.getlist('second_file[]')

        if not first_file or not second_files:
            return render(request, 'remupc.html', {"error": "Please select both UPC Excel data  and Tag files."})

        # Create a temporary dump folder in the project base directory
        dump_folder = os.path.join(settings.MEDIA_ROOT, 'dump')
        if not os.path.exists(dump_folder):
            os.makedirs(dump_folder)

        fs = FileSystemStorage(location=dump_folder)  # Save to a folder named 'dump'

        firstfilename = fs.save(first_file.name, first_file)  # Save the file
        firstfile_url = os.path.join(dump_folder, firstfilename)# Get the file URL
 
        # Process Excel file
        arrUPC_data = getUPCFromExcel(firstfile_url) 




        # Process and update each flat file
        tag_files = []
        for second_file in second_files:

            second_filename = fs.save(second_file.name, second_file)  # Save the file
            secondfile_url = os.path.join(dump_folder, second_filename)

            # Process each file
            deleteMatchingUPCRow(arrUPC_data, secondfile_url)
            tag_files.append(second_filename)

        # Store the file names in session to pass to the next page
        request.session['uploaded_files'] = tag_files 
        request.session['uploaded_status'] = 'True' 
        return redirect('tasks:download')  # Redirect to download page
    else:
        return render(request, "tasks/remupc.html", {'disable_menu' : True})



# Helper functions for Excel and flat file processing (to be implemented)
def getUPCFromExcel(excel_file):
    arrUPC = []
    workbook = openpyxl.load_workbook(excel_file, data_only=True)  # Read data only for efficiency
    # Extract data from Excel sheet 
    for eachSheet in workbook.worksheets:
        if eachSheet.sheet_state == "visible":
            # sheet = workbook.worksheets[i]
            for column in eachSheet.iter_cols():
                column_name = column[0].value
                if column_name == "UPC":
                    for i, cell in enumerate(column):
                        if i != 0:
                            upcstr = str(cell.value)
                            upcstr = upcstr.replace("-", "")
                            if upcstr != None:
                                arrUPC.append(upcstr)

    return arrUPC  # This will be a list, dictionary, or other structure

def deleteMatchingUPCRow(arrUPC_data, flat_file):
    tagFilePath = flat_file

    with open(tagFilePath, 'r+') as sfile:
        data = sfile.readlines()
        sfile.seek(0)
        sfile.truncate()

    sfile = open(tagFilePath, 'w')
    for line in data:
        start = 45  # upc 45 - 57 (13 digits)
        end = 58  
            
        for exlUPC in arrUPC_data:
            index = line.find(exlUPC, start, end)
            if index > 0:
                break

        if index == -1:
            sfile.write(line)

    


##-------------- After process the file which recieved through browser will send back to browser for user to download srart here -------------##########

def download_files(request):
    if request.method == "POST":

        if request.session.get('uploaded_status') == 'True':
            uploaded_files = request.session.get('uploaded_files', [])
            dump_folder = os.path.join(settings.MEDIA_ROOT, 'dump')

            if not uploaded_files or not os.path.exists(dump_folder):
                return HttpResponse("No files found to download.", status=404)

            file_paths = [os.path.join(dump_folder, file_name) for file_name in uploaded_files]

            # Check how many files the user selected
            if len(file_paths) == 1:
                # Single file: Return the file directly
                file_to_download = file_paths[0]
                response = FileResponse(open(file_to_download, 'rb'), as_attachment=True)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_to_download)}"'
            else:
                # Multiple files: Zip them together
                zip_file_path = os.path.join(dump_folder, 'tag_files.zip')
                with ZipFile(zip_file_path, 'w') as zipf:
                    for file_path in file_paths:
                        zipf.write(file_path, arcname=os.path.basename(file_path))

                response = FileResponse(open(zip_file_path, 'rb'), as_attachment=True)
                response['Content-Disposition'] = f'attachment; filename="processed_Tag_files.zip"'

            # Cleanup: Delete all files in the dump folder after download
            shutil.rmtree(dump_folder, ignore_errors=True)
            request.session['uploaded_status'] = 'False' 
            return response
        else:
            return redirect("home")
    else:
        return render(request, "tasks/download.html", {'disable_menu' : True})

  