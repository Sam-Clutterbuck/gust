from flask import Flask, render_template, request, redirect, url_for, jsonify
from psutil import cpu_percent 

from server.src import Gust_Sources, File_Download
from server.web.src.web_helpers import Web_Helpers

app = Flask(__name__, template_folder='templates', static_folder='styles')

#####################
#Globals

app.secret_key = "TEST"
#####################

def Start_Web_App():
    app.run(host="0.0.0.0", port=80, debug=True)


########################################################################
# Error Handles

@app.errorhandler(404)
def Page_Not_Found(error):
    return render_template("./404.html")

########################################################################

########################################################################
#Login logic

@app.route('/login_page', methods=['GET', 'POST'])
@Web_Helpers.Url_Log
def Login_Blocker():
    return render_template("./login_block.html")

@app.route('/login_request', methods=['POST'])
def Attempt_Login():

    username=request.form['username']
    password=request.form['password']
    current_url=Web_Helpers.Get_Previous_Url()

    success, link = Web_Helpers.Log_In(username,password)

    if success:
        return link
    
    return redirect(current_url)

@app.route('/logout_request', methods=['GET'])
def Attempt_Logout():
    Web_Helpers.Log_Out()
    return redirect(url_for("Home"))

########################################################################
# Home page

@app.route("/home")
@app.route("/")
@Web_Helpers.Url_Log
def Home():

    source_ammount = Web_Helpers.Get_Header_Number(Web_Helpers.SOURCE_LOC)

    return render_template("./home.html", defined_sources_ammount=source_ammount)


########################################################################
# Sources pages

@app.route("/sources")
@Web_Helpers.Authentication_Check
@Web_Helpers.Url_Log
def Sources():
    source_ammount, source_headings, data = Web_Helpers.Get_Source_Data()

    return render_template("./sources.html", defined_sources_ammount=source_ammount, headings=source_headings, data=data)

@app.route("/sources/delete", methods=['POST'])
@Web_Helpers.Authentication_Check
def Delete_Source():
    Source_Name=request.form['Source_Name']

    if Source_Name is not None:
        Gust_Sources.Delete_Source(Source_Name)
    
    return redirect(url_for('Sources'))


@app.route("/sources/update/<Source>")
@Web_Helpers.Authentication_Check
@Web_Helpers.Url_Log
def Update_Sources(Source):

    data = Web_Helpers.Get_Details(Web_Helpers.SOURCE_LOC)

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


########################################################################
# Downloads pages


@app.route("/downloads")
@Web_Helpers.Url_Log
def Downloads():
    ammount, headings, data = Web_Helpers.Get_Downloads_Data()

    if (len(File_Download.DOWNLOADING_STATUS) > 0):
        downloading_files = True
        print("TRUYE")
    else:
        downloading_files = False


    test = request.args.get('text')
    print(test)

    return render_template("./downloads.html", download_ammount=ammount, headings=headings, data=data, downloading_files=downloading_files)

@app.route("/downloads/begin", methods=['POST'])
@Web_Helpers.Authentication_Check
def Download_Source():
    Source_Name=request.form['Source_Name']

    if Source_Name is not None:
        Gust_Sources.Download_Source(Source_Name)
    
    return redirect(url_for('Downloads'))


@app.route("/downloads/begin/all", methods=['GET'])
@Web_Helpers.Authentication_Check
def Download_All_Sources():
    
    Gust_Sources.Download_Sources()
    
    return redirect(url_for('Downloads'))


@app.route('/_download_Progress', methods= ['GET'])
def Download_Progress():

    data = Web_Helpers.Download_Info()
    return jsonify(data)