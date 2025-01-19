from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Database configuration
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=nikhil128.database.windows.net;'
        'DATABASE=StudentDB;'
        'UID=testuser;'
        'PWD=Knikhilkumar@7585'
    )

@app.route('/')
def index():
    return '''
    <h1>Student Management System</h1>
    <p>Available endpoints:</p>
    <ul>
        <li>GET /students - List all students</li>
        <li>GET /student/<id> - Get a specific student</li>
        <li>POST /student - Create a new student</li>
        <li>PUT /student/<id> - Update a student</li>
        <li>DELETE /student/<id> - Delete a student</li>
    </ul>
    '''

@app.route('/students')
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students')
        students = []
        for row in cursor.fetchall():
            students.append({
                'ID': row.ID,
                'Name': row.Name,
                'Age': row.Age
            })
        return jsonify(students)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/<int:id>')
def get_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students WHERE ID = ?', (id,))
        row = cursor.fetchone()
        if row:
            student = {
                'ID': row.ID,
                'Name': row.Name,
                'Age': row.Age
            }
            return jsonify(student)
        return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        if not all(key in data for key in ['ID', 'Name', 'Age']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Students (ID, Name, Age) 
            VALUES (?, ?, ?)
        ''', (data['ID'], data['Name'], data['Age']))
        
        conn.commit()
        return jsonify({'message': 'Student created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        data = request.get_json()
        if not any(key in data for key in ['Name', 'Age']):
            return jsonify({'error': 'No fields to update'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        if 'Name' in data:
            update_fields.append('Name = ?')
            params.append(data['Name'])
        if 'Age' in data:
            update_fields.append('Age = ?')
            params.append(data['Age'])
        params.append(id)
        
        query = f"UPDATE Students SET {', '.join(update_fields)} WHERE ID = ?"
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Student not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Student updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM Students WHERE ID = ?', (id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Student not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)