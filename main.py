from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel

app = FastAPI()

connection = psycopg2.connect(
    host="localhost",
    database="postgres",
    port=5432,
    password="Utkarsha@06",
    user="postgres"
)

cursor = connection.cursor()
class Student(BaseModel):
    id: int
    name: str       
    course: str

# GET ALL STUDENTS
@app.get("/students") 


def get_all_students():
    cursor.execute("SELECT * FROM students") #cusor is a key word to execute the query
    rows = cursor.fetchall()
    print(rows)

    # return {'message': 'welcome to the Fast API'}\
    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'name': row[1],
            'course': row[2]
        })
    return result

@app.get('/students/{id}')
def get_single_student(id:int): #pydantic model
   
    try:
        cursor.execute("SELECT * FROM students WHERE id=%s", (id,)) # id = %s" for dynamic query which enter user and give valuse in tuple format
        #and , commas are used to make it a tuple as per sytaxt one value is query and another is 
        #but here it is not tuple ,tuple is created because of comma after id 
        # tuple with single element with comma

        row = cursor.fetchone() #for single row crate a tuple
        return {
            'id': row[0],    
            'name': row[1],
            'course': row[2]
        }
    except:
        raise HTTPException(status_code=404, detail="Student not found")

#create Student Record
@app.post('/students')
def create_student_record(student: Student):
    try:
        cursor.execute("INSERT INTO students (id, name, course) VALUES (%s, %s, %s)", (student.id, student.name, student.course))    
        connection.commit()    
        raise HTTPException(status_code=201, detail="Student record created successfully")
    except psycopg2.IntegrityError as e:
        connection.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=400, detail="Student with this ID already exists")