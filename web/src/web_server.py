from flask import Flask, render_template, request, session, redirect, url_for, flash


from core.src import Yaml_Editor, Data_Link
from server.src import Gust_Sources
from web.src.web_helpers import Web_Helpers

app = Flask(__name__, template_folder='templates', static_folder='styles')

#####################
#Globals

success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
if (success == False):
    yaml_file = {}
CONFIG_FILE = yaml_file

SOURCE_LOC = CONFIG_FILE["server_sources_loc"]
test = "HERE"
app.secret_key = "TEST"
#####################

def Start_Web_App():
    app.run(host="0.0.0.0", port=80, debug=True)


########################
# Error Handles

@app.errorhandler(404)
def Page_Not_Found(error):
    return render_template("./404.html")

########################

@app.route("/home")
@app.route("/")
def Home():

    source_ammount = Web_Helpers.Get_Sources_Number()

    return render_template("./home.html", defined_sources_ammount=source_ammount)



@app.route("/sources")
@Web_Helpers.Authentication_Check
def Sources():
    source_ammount, source_headings, data = Web_Helpers.Get_Source_Data()

    return render_template("./sources.html", defined_sources_ammount=source_ammount, headings=source_headings, data=data)

@app.route("/sources/delete", methods=['POST'])
@Web_Helpers.Authentication_Check
def Delete_Source():
    Source_Name=request.form['Source_Name']

    if Source_Name not in Yaml_Editor.List_Headers(SOURCE_LOC):
        print("COULDN'T FIND SOURCE")
        return redirect(url_for('Sources'))
    

    if Source_Name is not None:
        Gust_Sources.Delete_Source(Source_Name)
    
    return redirect(url_for('Sources'))

@app.route('/login_page', methods=['GET', 'POST'])
def Login_Blocker():
    return render_template("./login_block.html")

@app.route('/login_request', methods=['POST'])
def Attempt_Login():

    username=request.form['username']
    password=request.form['password']
    current_url=request.form['current_url']

    success, link = Web_Helpers.Log_In(username,password)

    if success:
        return link
    
    return redirect(current_url)

@app.route('/logout_request', methods=['GET'])
def Attempt_Logout():
    Web_Helpers.Log_Out()
    return redirect(url_for("Home"))

@app.route("/sources/update/<Source>")
@Web_Helpers.Authentication_Check
def Update_Sources(Source):

    data = Web_Helpers.Get_Source_Details()

    source_name = ""
    source_url = ""
    hash_url = ""
    hash_type = "sha256"

    for source in data:
        if (source[0] == Source):
            source_name = source[0]
            source_url = source[1]
            hash_url = source[2]
            hash_type = source[3]

    return render_template("./update_source.html", source_name=source_name, source_url=source_url, hash_url=hash_url, hash_type=hash_type)

@app.route("/sources/triger_update", methods=['POST'])
@Web_Helpers.Authentication_Check
def Trigger_Source_Update():

    source_name=request.form['source_name']
    source_url=request.form['source_url']
    hash_url=request.form['hash_url']
    hash_type=request.form['hash_type']

    Gust_Sources.Update_Source(source_name,source_url,hash_url,hash_type)

    return redirect(url_for('Sources'))