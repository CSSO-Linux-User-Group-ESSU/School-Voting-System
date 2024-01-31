import json
from os import path
from typing import Union

def course_checker(course : str) -> Union[str, None]:
    """
    Handles the validation of a course code based on the data in the file uploaded.

    Parameters:
        course (str): The course acronym to be validated.

    Returns:
        Union[str, None]: 
        Returns a full course name if the course acronym is registered in the database.
        If the course code is invalid, returns None.

    Raises:
        None

    Usage:
        This function is designed to validate a course acronym provided from the file.
        If the course code is valid, the function returns the full course name.
        If the course code is invalid, it returns None, and the calling code is expected to handle the error accordingly.
    """

    #Backend folder directory
    backend_directory = path.dirname(path.abspath(__file__))

    #course_department,json file location
    course_json = path.join(backend_directory, "../course_department.json")
    
    #Open the course_department,json file 
    with open(course_json) as file:

        #Read the json file as a dictionary
        data = json.load(file)

        #Itterate over the department
        for i in data.values():

            #Itterate over the department courses
            for j in i:

                #Check if the course acronym is the same as the current course and return if it is
                if course in j.values():
                    return j["course"]
        
        #return None if the course is not found
        return None
            

#Testing purposes
if __name__ == "__main__":
    print(course_checker("BSCS"))
