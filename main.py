from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # Load environment variables from .env file

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allows specific origins
    allow_credentials=False,           # Allows cookies or headers to be sent
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],              # Allows all HTTP headers
)

# connection = psycopg2.connect(
#     host=os.getenv("DB_HOST"),
#     database=os.getenv("DB_DATABASE"),
#     port=os.getenv("DB_PORT"),
#     password=os.getenv("DB_PASSWORD"),
#     user=os.getenv("DB_USER")
# )

connection = psycopg2.connect('postgresql://neondb_owner:npg_p9doKOGHy4eu@ep-restless-leaf-b3lflrcm-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

class Student(BaseModel):
    id: int = None
    name: str = None       
    course: str = None

# GET ALL STUDENTS
@app.get("/students") 
  # Create a cursor for executing queries
def get_all_students():
    cursor = connection.cursor()  # Create a cursor for executing queries
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
    cursor.close()  # Close the cursor after use    
    return result

@app.get('/students/{id}')              #{id}' path parameter
def get_single_student(id:int): #pydantic model
    cursor = connection.cursor()  # Create a new cursor for this request
    try: 
        cursor = connection.cursor()  # Create a new cursor for this request
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
        cursor.close()  # Close the cursor in case of an exception
        raise HTTPException(status_code=404, detail="Student not found")

#create Student Record
@app.post('/students')
def create_student_record(student: Student):
    try:
        cursor = connection.cursor()  # Create a new cursor for this request
        cursor.execute("INSERT INTO students (id, name, course) VALUES (%s, %s, %s)", (student.id, student.name, student.course))    
        connection.commit()    
        raise HTTPException(status_code=201, detail="Student record created successfully")
    except psycopg2.IntegrityError as e:
        connection.rollback()  # Rollback the transaction in case of an error
        cursor.close()  # Close the cursor after use
        raise HTTPException(status_code=400, detail="Student with this ID already exists")
        

@app.put('/students/{id}')
def update_student_record(id: int, student: Student):  #student is object and Student is class name
    cursor = connection.cursor()  # Create a new cursor for this request
    cursor.execute("UPDATE students SET id=%s, name=%s, course=%s WHERE id=%s", (student.id, student.name, student.course, id))
    if (cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail="Student not found")
    connection.commit()
    cursor.close()  # Close the cursor after use
    raise HTTPException(status_code=200, detail="Student record updated successfully")

#partial Update of Student Record
@app.patch('/students/{id}')
def update_student_partial_record(id: int, student: Student):
    cursor = connection.cursor()  # Create a new cursor for this request
    if (student.id != None):
        cursor.execute("UPDATE students SET id=%s WHERE id=%s", (student.id, id))
    if (student.name != None):
        cursor.execute("UPDATE students SET name=%s WHERE id=%s", (student.name, id))
    if (student.course != None):
        cursor.execute("UPDATE students SET course=%s WHERE id=%s", (student.course, id))
    if (cursor.rowcount == 0):

        raise HTTPException(status_code=404, detail="Student not found")
    connection.commit()
    cursor.close()  # Close the cursor after use
    raise HTTPException(status_code=200, detail="Partial Student record updated successfully")


#delete Student Record
@app.delete('/students/{id}')
def delete_student_record(id: int):
    cursor = connection.cursor()  # Create a new cursor for this request
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    if (cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail="Student not found")
    connection.commit()
    cursor.close()  # Close the cursor after use
    raise HTTPException(status_code=200, detail="Student record deleted successfully") 

