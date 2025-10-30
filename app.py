from flask import Flask, render_template, request, jsonify
import config
import pymysql

db = config.db1
app = Flask(__name__)

def getAllStudents(cursor):
    sql = "SELECT * FROM student"
    cursor.execute(sql)
    return cursor.fetchall()


@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/schedule', methods = ['GET'])
def schedulePage():
    cursor = db.cursor()
    ID = request.args.get('studentID')

    sql = "SELECT ID, name FROM student WHERE ID = %s"
    cursor.execute(sql, (ID,))
    constData = cursor.fetchall()

    sql = "SELECT DISTINCT CAST(year as unsigned) AS year FROM student JOIN takes ON student.ID = takes.ID WHERE student.ID = %s"
    cursor.execute(sql, (ID,))
    availableYears = [row[0] for row in cursor.fetchall()]

    yearFilter = request.args.get('selectYear')
    print(yearFilter)

    if yearFilter and yearFilter != "0":
        sql = "SELECT course_id, semester, year FROM student JOIN takes ON student.ID = takes.ID WHERE student.ID = %s AND takes.year = %s"
        cursor.execute(sql, (ID, int(yearFilter)))
    else:
        sql = "SELECT course_id, semester, year FROM student JOIN takes ON student.ID = takes.ID WHERE student.ID = %s"
        cursor.execute(sql, (ID,))
    data = cursor.fetchall()


    return render_template('schedule.html', constData = constData, data = data, availableYears=availableYears)


@app.route('/search', methods = ['GET', 'POST'])
def searchPage():
    cursor = db.cursor()
    data = getAllStudents(cursor)

    if request.method == 'GET':
        return render_template('search.html', data=data)
    
    elif request.method == 'POST':
        formAction = request.form.get('action')

        if formAction == 'addStudent':
            try:
                newID = int(request.form.get('submitID'))
            except ValueError:
                return render_template('search.html', data=data)
            
            newName = request.form.get('submitName')
            newDept = request.form.get('submitDept')
            newCred = request.form.get('submitCred')
            values = (newID, newName, newDept, newCred)

            
            checkIDSQL = "SELECT student.ID FROM student WHERE student.ID = %s"
            cursor.execute(checkIDSQL, (newID,))
            if not cursor.fetchone():
                sql = "INSERT INTO student(ID, name, dept_name, tot_cred) VALUES(%s, %s, %s, %s)"
                cursor.execute(sql, values)
            else:
                return "ERROR"
            
            db.commit()
            data = getAllStudents(cursor)
        else:
            
            searchName = request.form.get('name')
            searchID = request.form.get('id')

            if searchName and searchID:
                sql = "SELECT * FROM student WHERE student.name like %s AND student.ID = %s"
                cursor.execute(sql, ('%' + searchName + '%',), (searchID,))
            elif searchName:
                sql = "SELECT * FROM student WHERE student.name like %s"
                cursor.execute(sql, ('%' + searchName + '%',))
            elif searchID:
                sql = "SELECT * FROM student WHERE student.ID = %s"
                cursor.execute(sql, (searchID,))
            else:
                cursor.close()
                return render_template('search.html', data=data)
            data = cursor.fetchall()
        
        cursor.close()
        return render_template('search.html', data=data)

            
    




if __name__ == '__main__':
    cursor = db.cursor()
    app.run()
