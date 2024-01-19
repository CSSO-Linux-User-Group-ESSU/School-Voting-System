from django.contrib import messages
from django.shortcuts import redirect, reverse
import os
from voting.forms import FileUploadForm
from voting.models import UploadFile
from administrator.backend.voter_upload import upload_voters
from django.http import HttpRequest, HttpResponseRedirect


def uploadUser(request : HttpRequest) -> HttpResponseRedirect:
    """
    Handles the upload of voter data from a file.

    Parameters:
        request (object): The HTTP request object.

    Returns:
    
        HttpResponseRedirect: Redirects to the 'adminViewVoters' page after processing the request.

    Raises:
        None

    Usage:
        This view handles the upload of voter data from a file. It expects a POST request with
        a file uploaded through a form. The uploaded file is processed, and voter data is added
        to the database. If successful, a success message is displayed. If the file format is
        invalid or an error occurs during processing, appropriate error messages are displayed.
        The view redirects to the 'adminViewVoters' page after processing.
    """

    #Check for request method
    if request.method == "POST":

        #Retrieve the file if the request method is POST
        form : FileUploadForm = FileUploadForm(request.POST, request.FILES)


        if form.is_valid():
            #Save the file the file validate the form validation
            save_file = form.save()

            #Get the file name of the file uploaded
            filepath = UploadFile.objects.get(id=save_file.pk)

            try:
                #Create an account each voter
                error_student = upload_voters(filepath.voters_file)

            except Exception:
                #Delete the file in the system if an error has occured while creating an account each voter
                os.remove(f"./media/{str(filepath.voters_file)}")
                messages.error(request, "Invalid File Format! Did you ask for a form from CCS?")
            
            else:
                if error_student:
                    
                    if type(error_student) == list:
                            #Show all the student who have an error creating an account
                            error = ",".join(error_student)
                            messages.error(request, f"Invalid Students Number: {error}")
                    else:
                        messages.error(request, error_student)

                else:
                    #Show a message that it is uploading if there's no error
                    messages.success(request, "Voters Uploaded Now")
        else:
            #Show an error message if the file type is not a csv file
            messages.error(request, "File mismatch")
    
    else:
        #Show an error message if the method is GET
        messages.error(request, "Access To This Resource Denied")
    
    #Redirect the userr to 'adminViewVoters' route after each rerquest
    return redirect(reverse("adminViewVoters"))