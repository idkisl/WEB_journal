from flask import Flask, render_template, request, url_for
import json
import csv
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum'
name_of_user = "зарегистрируйтесь"
current_user = {}


@app.route('/', methods=["POST", "GET"])
@app.route('/index', methods=["POST", "GET"])
def index():
    return render_template("start_page.html",
                           name_of_user=name_of_user,
                           logo=url_for('static', filename='icon.png'),
                           image_1=url_for('static', filename='image1.jpg'),
                           image_2=url_for('static', filename='image2.jpg'),
                           image_3=url_for('static', filename='image3.jpg'))


@app.route('/registration', methods=["POST", "GET"])
def registration():
    with open("data/users.json") as users_file:
        users = json.load(users_file)
    is_good_rigistration = "nothing"
    login = ""

    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        teachers_login = request.form["teachers_login"]
        status = request.form["inlineRadioOptions"]
        avatar = request.form["avatar"]

        is_same_login = False
        for user in users:
            if user["login"] == login:
                is_same_login = True
                is_good_rigistration = "all_bad"
                break
        if is_good_rigistration != "all_bad":
            if not is_same_login and (len(name) == 0 or len(surname) == 0):
                is_good_rigistration = "bad_name"
            elif not is_same_login:
                user = {"login": login,
                        "password": password,
                        "name": name,
                        "surname": surname,
                        "email": email,
                        "status": status,
                        "teachers_login": teachers_login}
                is_good_rigistration = "all_good"
                with open("data/users.json", "w") as users_file:
                    users.append(user)
                    json.dump(users, users_file, ensure_ascii=False, indent=2)
    return render_template("registration.html",
                           name_of_user=name_of_user,
                           title="Регистрация",
                           is_good=is_good_rigistration,
                           login=login,
                           logo=url_for('static', filename='icon.png'))


@app.route('/enter', methods=["POST", "GET"])
def enter():
    global name_of_user
    global current_user

    login = password = ""
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
    if name_of_user == "зарегистрируйтесь":
        user_login_password = "nothing"
    else:
        user_login_password = "all_good"

    is_login_in = False
    with open("data/users.json") as users_file:
        users = json.load(users_file)
        for user in users:
            if login == user["login"] and password == user["password"]:
                is_login_in = True
                user_login_password = "all_good"
                name_of_user = user["status"] + "  &&  " + user["name"] + " " + user["surname"]
                current_user = user
                break

    if request.method == "POST" and not is_login_in:
        user_login_password = "all_bad"
    if login == "" and user == "" and user_login_password != "all_good":
        user_login_password = "nothing"
    else:
        if user_login_password != "all_good":
            user_login_password = "all_bad"
            name_of_user = "зарегистрируйтесь"
            current_user = {}
    if request.method != "POST":
        user_login_password = "nothing"
    return render_template("enter_page.html",
                           name_of_user=name_of_user,
                           title="Вход",
                           user_login_password=user_login_password,
                           logo=url_for('static', filename='icon.png'))


@app.route('/diary', methods=["POST", "GET"])
def diary():
    # если пользователь не авторизован или если он учитель -- не пускать
    if len(current_user) == 0 or current_user["status"] == "teacher":
        return render_template("no_acess.html",
                               name_of_user=name_of_user,
                               title="Дневник",
                               parametr="ученика",
                               role=True,
                               logo=url_for('static', filename='icon.png'))

    with open('data/students.csv', encoding="utf8", errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"', )
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        base_info = {}
        student_info = {}
        for person in reader:
            if person["name"] == 'theme_of_lesson' and len(person["surname"]) == 0:
                base_info = person
            elif person["name"] == current_user["name"] and person["surname"] == current_user["surname"]:
                student_info = person
        # print(person["name"], person["surname"], current_user["name"], current_user["surname"])
        if len(student_info) == 0:
            return render_template("no_acess.html",
                                   name_of_user=name_of_user,
                                   title="Дневник",
                                   parametr="ученика",
                                   role=False,
                                   text="Данный ученик не зарегистрирован в системе",
                                   logo=url_for('static', filename='icon.png'))
        teacher_info = {}

        for person in reader:
            if person["login"] == student_info["teachers_login"]:
                teacher_info = person
        if len(teacher_info) == 0:
            teacher_info["name"] = "преподаватель"
            teacher_info["surname"] = "не зарегистрирован"

        keys = list(base_info.keys())
        keys.remove("name")
        keys.remove("surname")
        keys.remove("teacher")
        keys = sorted(keys)
        html_str = ""
        html_str += '''<table class="table" style="text-align: center; vertical-align: middle;">
              <thead class="thead-light">
                <tr class="align-bottom">
                  <th width="10%" scope="row">Номер урока</th>
                  <th  width="40%" scope="row">Тема урока</th>
                  <th scope="row">Оценка</th>
                </tr>
              </thead>
            
              <tbody>'''
        for i in range(len(keys)):
            html_str += f'''<tr class="align-bottom">
                          <th  width="10%" scope="row">{i + 1}</th>
                          <td width="40%" scope="row">{base_info[keys[i]]}</td>
                          <td scope="row">{student_info[keys[i]]}</td>
                        </tr>'''
        html_str += '''
                  </tbody>
                </table>'''
        all_html = ""
        with open("data/student_part1.txt", "r") as str_1:
            all_html += str_1.read()
        all_html += html_str
        with open("data/student_part3.txt", "r") as str_3:
            all_html += str_3.read()
        with open("templates/diary_generated.html", "w") as file:
            file.write(all_html)

    return render_template("diary_generated.html",
                           name_of_user=name_of_user,
                           title="Дневник",
                           text_of_hello=f"Оценки ученика {current_user['name']} {current_user['surname']}",
                           logo=url_for('static', filename='icon.png'))


@app.route('/journal', methods=["POST", "GET"])
def journal():
    # если пользователь не авторизован или если он ученик -- не пускать
    if len(current_user) == 0 or current_user["status"] == "student":
        return render_template("no_acess.html",
                               name_of_user=name_of_user,
                               title="Журнал",
                               parametr="учителя",
                               role=True,
                               logo=url_for('static', filename='icon.png'))
    with open('data/students.csv', encoding="utf8", errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"', )
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        base_info = {}
        my_students = []
        for person in reader:
            if person["name"] == 'theme_of_lesson' and len(person["surname"]) == 0:
                base_info = person
            elif person["teacher"] == current_user["login"]:
                my_students.append(person)
        keys = list(base_info.keys())
        keys.remove("name")
        keys.remove("surname")
        keys.remove("teacher")
        keys = sorted(keys)
    table_html = '''<div class="table-responsive">
                    <table class="table">
                  <caption>Журнал учителя {{name_teacher}}</caption>
                  <thead>'''

    # линия - заголовок таблицы
    line = '''<tr>
                      <th scope="col">#</th>
                      <th scope="col">Имя</th>
                      <th scope="col">Фамилия</th>'''
    for key in keys:
        line += f'''\n<th scope="col">{key}</th>\n'''
    line += '''</tr>'''

    table_html += line

    line = '''<tr>
              <th scope="row"></th>
              <th scope="row">темы</th>
              <th scope="row">уроков:</th>'''
    for key in keys:
        line += f'''\n<th>{base_info[key]}</th>\n'''
    line += '''</tr>'''
    table_html += line
    table_html += '''</thead>
                        <tbody>'''
    # print(my_students)
    # тело таблицы
    for i in range(len(my_students)):
        student = my_students[i]
        line = "<tr>"
        line += f'''<th scope="row">{i + 1}</th>'''
        line += f'''<td>{student["name"]}</td>'''
        line += f'''<td>{student["surname"]}</td>'''
        for key in keys:
            line += f'''<td>{student[key]}</td>'''
        line += "</tr>"
        # print(line)
        table_html += line

    table_html += '''  </tbody>
                    </table>
                    </div>'''


    all_html = ""
    with open("data/student_part1.txt", "r") as str_1:
        all_html += str_1.read()
    all_html += table_html
    with open("data/student_part3.txt", "r") as str_3:
        all_html += str_3.read()

    with open("templates/journal_generated.html", "w") as file:
        file.write(all_html)

    return render_template("journal_generated.html",
                           name_of_user=name_of_user,
                           title="Журнал",
                           text_of_hello=f"Журнал учителя {current_user['name']} {current_user['surname']}",
                           name_teacher=f"{current_user['name']} {current_user['surname']}",
                           logo=url_for('static', filename='icon.png'))


@app.route('/dnevnik', methods=["POST", "GET"])
def dnevnik():
    # если пользователь не авторизован или если он учитель -- не пускать
    if len(current_user) == 0 or current_user["status"] == "teacher":
        return render_template("no_acess.html",
                               name_of_user=name_of_user,
                               title="Дневник",
                               parametr="ученика",
                               role=True,
                               logo=url_for('static', filename='icon.png'))

    with open('data/students.csv', encoding="utf8", errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"', )
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        base_info = {}
        student_info = {}
        for person in reader:
            if person["name"] == 'theme_of_lesson' and len(person["surname"]) == 0:
                base_info = person
            elif person["name"] == current_user["name"] and person["surname"] == current_user["surname"]:
                student_info = person
        # print(person["name"], person["surname"], current_user["name"], current_user["surname"])
        if len(student_info) == 0:
            return render_template("no_acess.html",
                                   name_of_user=name_of_user,
                                   title="Дневник",
                                   parametr="ученика",
                                   role=False,
                                   text="Данный ученик не зарегистрирован в системе",
                                   logo=url_for('static', filename='icon.png'))
        teacher_info = {}

        for person in reader:
            if person["login"] == student_info["teachers_login"]:
                teacher_info = person
        if len(teacher_info) == 0:
            teacher_info["name"] = "преподаватель"
            teacher_info["surname"] = "не зарегистрирован"

        keys = list(base_info.keys())
        keys.remove("name")
        keys.remove("surname")
        keys.remove("teacher")
        keys = sorted(keys)
        html_str = ""
        html_str += '''<table class="table" style="text-align: center; vertical-align: middle;">
              <thead class="thead-light">
                <tr class="align-bottom">
                  <th width="10%" scope="row">Номер урока</th>
                  <th  width="40%" scope="row">Тема урока</th>
                  <th scope="row">Оценка</th>
                </tr>
              </thead>

              <tbody>'''
        for i in range(len(keys)):
            html_str += f'''<tr class="align-bottom">
                          <th  width="10%" scope="row">{i + 1}</th>
                          <td width="40%" scope="row">{base_info[keys[i]]}</td>
                          <td scope="row">{student_info[keys[i]]}</td>
                        </tr>'''
        html_str += '''
                  </tbody>
                </table>'''
        all_html = ""
        with open("data/student_part1.txt", "r") as str_1:
            all_html += str_1.read()
        all_html += html_str
        with open("data/student_part3.txt", "r") as str_3:
            all_html += str_3.read()
        with open("templates/diary_generated.html", "w") as file:
            file.write(all_html)

    return render_template("diary_generated.html",
                           name_of_user=name_of_user,
                           title="Дневник",
                           text_of_hello=f"Оценки ученика {current_user['name']} {current_user['surname']}",
                           logo=url_for('static', filename='icon.png'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')