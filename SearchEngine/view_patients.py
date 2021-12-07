import sys
import traceback
import logging
import python_db

mysql_username = 'scanales'
mysql_password = 'iepha3Oo'

try:
    python_db.open_database('localhost', mysql_username, mysql_password, mysql_username)
    res = python_db.executeSelect('SELECT * FROM Patient;')
    res = res.split('\n')
    col_names = res[0].split(' ')
    print("<div class=\"container-fluid\"> <section class=\"patient\" id=\"patient\"> <br/> <h2>" + "Patient Table" + "</h2><br/>")
    print("<table class=\"table table-bordered\">")
    print("<tr>")
    for i in range(len(col_names)):
        if len(col_names[i]) > 1:
            print("   <th scope=\"col\">" + col_names[i] + "</th>")
    print("</tr>")

    for i in range(len(res)-2):
        col_data = res[i+2].split(' ')
        print(" <tr>")
        for i in range(len(col_data)):
            if len(col_data[i]) > 0:
                print("   <td>" + col_data[i] + "</td>")
        print("</tr>")

    print("</table></section></div></div>")
    python_db.close()
except Exception as e:
    logging.error(traceback.format_exc())