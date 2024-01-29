import mariadb
import json

def college_setup() -> bool:
    mydb = mariadb.connect(
        host="127.0.0.1",
        user="root",
        password="Bry01202004",
        database="e_voting",
        port=3306
    )
    

    curr = mydb.cursor()
    curr.execute("SELECT * FROM voting_college")
    colleges = {i[1] : {"id" : i[0]} for i in curr}
    
    curr.execute("SELECT course FROM voting_course")
    courses = [j[0] for j in curr]
    
    file_data = open("administrator/course_department.json")
    file_data_json = json.load(file_data)
    for i in file_data_json:
        if i not in colleges.keys():
            curr.execute("INSERT INTO voting_college (college) VALUES(?)", [i])
            colleges[i] = {"id" : curr.lastrowid}
            mydb.commit()
            college_id = curr.lastrowid
        else:
            college_id = colleges[i]["id"]

        for j in file_data_json[i]:
            if j['course'] not in courses:
                curr.execute("INSERT INTO voting_course (course, college_id) VALUES (?, ?)",
                             [j['course'], college_id])
                mydb.commit()
    
    curr.close()
    mydb.close()
        


if __name__ == "__main__":
    college_setup()