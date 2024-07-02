from flask import Flask, render_template, request 
import json
from web3 import Web3, HTTPProvider
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
app = Flask(__name__)

global details
details = ''
global user_id

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:8545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BankContract.json' #bank contract contract code
    deployed_contract_address = '0xd531E07e3C3Cf5d2F096301F3F8558586fe82F48' #hash address to access bank contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'adduser':
        details = contract.functions.getUsers().call()
    if contract_type == 'account':
        details = contract.functions.getBankAccount().call()
    if contract_type == 'history':
        details = contract.functions.gethistory().call()
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]    
    print(details)
   



def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:8545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BankContract.json' #bank contract file
    deployed_contract_address = '0xd531E07e3C3Cf5d2F096301F3F8558586fe82F48' #bank contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'adduser':
        details+=currentData
        msg = contract.functions.addUsers(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'account':
        details+=currentData
        msg = contract.functions.bankAccount(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'history':
        details+=currentData
        msg = contract.functions.addhistory(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)


@app.route('/SendAmountAction', methods=['POST'])
def SendAmountAction():
    global details,otp
    if request.method == 'POST':
        sender = request.form['t1']
        balance = request.form['t2']
        receiver = request.form['t3']
        amount = request.form['t4']
        otp_entered = request.form['t5']
        amount = float(amount)
        balance = float(balance)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        readDetails('adduser')
        arr = details.split("\n")
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == receiver:
                email = array[4]
        if otp_entered == otp:
            if balance > amount:
                data = sender+"#"+str(amount)+"#"+str(timestamp)+"#Sent To "+receiver+"\n"
                saveDataBlockChain(data,"account")
                data = receiver+"#"+str(amount)+"#"+str(timestamp)+"#Received From "+sender+"\n"
                saveDataBlockChain(data,"account")
                context= 'Money sent to '+receiver
                sendotp1(email,sender,amount)
                return render_template('UserScreen.html', msg=context)
            else:
                context= 'Insufficient balance'
                return render_template('UserScreen.html', msg=context)
        else:
            context = 'Invalid OTP, Please Try Again'
            return render_template('UserScreen.html', msg=context)



@app.route('/SendAmount', methods=['GET','POST'])
def SendAmount():
    if request.method == 'GET':
        global user_id
        readDetails("account")
        deposit = 0
        wd = 0
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == user_id:
                if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
                    deposit = deposit + float(arr[1])
                else:
                    wd = wd + float(arr[1])
        deposit = deposit - wd            
        output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Available&nbsp;Balance</td><td><input type="text" name="t2" size="20" value='+str(deposit)+' readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Choose&nbsp;Receiver&nbsp;Name</td><td><select name="t3">'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "adduser":
                if arr[1] != user_id:
                    output += '<option value="'+arr[1]+'">'+arr[1]+'</option>'
        output += "</select></td></tr>"
             
        return render_template('SendAmount.html', msg1=output)


    
@app.route('/ViewBalance', methods=['GET','POST'])
def ViewBalance():
    if request.method == 'GET':
        global user_id
        output = '<table border=1 align=center width=100%>'
        font = '<font size="3" color="black">'
        arr = ['Username','Amount','Transaction Date',"Transaction Status"]
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        readDetails("account")
        rows = details.split("\n")
        deposit = 0
        wd = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == user_id:
                output += "<tr><td>"+font+arr[0]+"</td>"
                output += "<td>"+font+arr[1]+"</td>"
                output += "<td>"+font+arr[2]+"</td>"
                output += "<td>"+font+arr[3]+"</td>"
                if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
                    deposit = deposit + float(arr[1])
                else:
                    wd = wd + float(arr[1])
        deposit = deposit - wd
        output += "<tr><td>"+font+"Current Balance : "+str(deposit)+"</td>"
              
        return render_template('ViewBalance.html', msg=output) 

            

@app.route('/LoginAction', methods=['POST'])
def LoginAction():
    global details
    global user_id
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        status = 'none'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "adduser":
                if arr[1] == username and arr[2] == password:
                    status = 'success'
                    user_id = username
                    break
        if status == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= "Welcome "+username
            return render_template('UserScreen.html', msg=context)
        else:
            context= 'Invalid login details'
            return render_template('Login.html', msg=context) 

@app.route('/AdminLoginAction', methods=['POST'])
def AdminLoginAction():
    global details
    global user_id
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        if username == 'admin' and password == 'admin':
            context = 'Welcome admin'
            return render_template('AdminScreen.html', msg=context)
        else:
            context= 'Invalid login details'
            return render_template('AdminLogin.html', msg=context) 


@app.route('/DepositAction', methods=['POST'])
def DepositAction():
    global details
    if request.method == 'POST':
        username = request.form['t1']
        amount = request.form['t2']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = username+"#"+amount+"#"+str(timestamp)+"#Self Deposit"+"\n"
        saveDataBlockChain(data,"account")
        context= 'Money added to user account '+username
        return render_template('Deposit.html', msg=context)


@app.route('/SignupAction', methods=['POST'])
def SignupAction():
    global details
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        contact = request.form['t3']
        email = request.form['t4']
        address = request.form['t5']
        gender = request.form['t6']
        record = 'none'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "adduser":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "adduser#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+gender+"\n"
            saveDataBlockChain(data,"adduser")
            context= 'Signup process completd and record saved in Blockchain'
            return render_template('Signup.html', msg=context)
        else:
            context= username+' Username already exists'
            return render_template('Signup.html', msg=context) 


@app.route('/Deposit', methods=['GET'])
def Deposit():
    if request.method == 'GET':
        global user_id
        output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
        
        return render_template('Deposit.html', msg1=output) 


@app.route('/SendRequest', methods=['GET', 'POST'])
def SendRequest():
    if request.method == 'GET':
        global user_id
        output = '<tr><td><font size="3" color="black">Choose Receiver Name</font></td><td><form method="post"><select name="selected_user">'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows) - 1):
            arr = rows[i].split("#")
            if arr[0] == "adduser" and arr[1] != user_id:
                output += '<option value="' + arr[1] + '">' + arr[1] + '</option>'
        output += '</select></td></tr><br><br>'
        output += '<tr><td><input type="submit" value="Send Request"></td></tr></form>'
        return render_template('SendRequest.html', msg=output)
    elif request.method == 'POST':
        selected_user = request.form['selected_user']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = user_id+"#"+selected_user+"#"+str(timestamp)+"#SendRequest"+"\n"
        saveDataBlockChain(data, "history")
        context = 'Request sent successfully'
        return render_template('SendRequest.html', msg1=context)
 

def request_status(name, user, date):
    readDetails('history')
    arr = details.split("\n")

    for i in range(len(arr)-1):
        array = arr[i].split("#")

        if array[0] == name and array[1] == user and array[2] == date and array[3] == 'StatusAccepted':
            return True
            break

    return False



@app.route('/RequestAction', methods=['GET', 'POST'])
def RequestAction():
    if request.method == 'GET':
        global user_id, name
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Request Sent By', 'Date and time', 'Action']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('history')
        arr = details.split("\n")

        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == user_id and array[3] == 'SendRequest':
                output += "<tr><td>" + font + array[0] + "</td>"
                output += "<td>" + font + array[2] + "</td>"
                output += f'<td><a href="/acceptrequest?name={array[0]}&date={array[2]}">{font}Click Here to Accept{font}</a></td>' if not request_status(array[0], user_id, array[2]) else f'<td>{font}Already Accepted{font}</td>'


        output += "</table><br/><br/><br/>"

        return render_template('RequestAction.html', msg=output)


def generate_otp():
    return str(random.randint(1000, 9999))

def sendotp(email):
    global otp
    otp_code = generate_otp()  
    otp = otp_code
    print(otp)
    email_address = 'truprojects02@gmail.com'
    email_password = 'lncqoxdnuifrauve'

    message = f'Subject: OTP for the transaction\n\nYour OTP is: {otp_code}'

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(email_address, email_password)
        connection.sendmail(from_addr=email_address, to_addrs=email, msg=message)

def sendotp1(email,sender,amount):
    email_address = 'truprojects02@gmail.com'
    email_password = 'lncqoxdnuifrauve'

    message = f'Your transaction is successful\n\n {amount} received from {sender}'

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(email_address, email_password)
        connection.sendmail(from_addr=email_address, to_addrs=email, msg=message)


@app.route('/acceptrequest', methods=['GET', 'POST'])
def acceptrequest():
    global user_id, name

    if request.method == 'GET':
        name = request.args.get('name')
        date = request.args.get('date')
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "adduser":
                if arr[1] == name:
                    email = arr[4]

        sendotp(email)
        
        data = name+"#"+user_id+"#"+date+"#"+"StatusAccepted"+"\n"
        saveDataBlockChain(data,"history")
        context = 'Otp send successfully'
        return render_template('RequestAction.html', msg1=context)

@app.route('/ViewTransaction', methods=['GET','POST'])
def ViewTransaction():
    if request.method == 'GET':
        global user_id
        output = '<table border=1 align=center width=100%>'
        font = '<font size="3" color="black">'
        arr = ['Username','Amount','Transaction Date',"Transaction Status"]
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        readDetails("account")
        rows = details.split("\n")
        deposit = 0
        wd = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            output += "<tr><td>"+font+arr[0]+"</td>"
            output += "<td>"+font+arr[1]+"</td>"
            output += "<td>"+font+arr[2]+"</td>"
            output += "<td>"+font+arr[3]+"</td></tr>"
              
        return render_template('ViewTransaction.html', msg=output) 





@app.route('/SendRequest', methods=['GET', 'POST'])
def SendRequests():
    if request.method == 'GET':
       return render_template('SendRequest.html', msg='')


@app.route('/Deposit', methods=['GET', 'POST'])
def Deposits():
    if request.method == 'GET':
       return render_template('Deposit.html', msg='')


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
       return render_template('Login.html', msg='')

@app.route('/RequestAction', methods=['GET', 'POST'])
def RequestActions():
    if request.method == 'GET':
       return render_template('RequestAction.html', msg='')

@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
    if request.method == 'GET':
       return render_template('AdminLogin.html', msg='')

@app.route('/AdminScreen', methods=['GET', 'POST'])
def AdminScreen():
    if request.method == 'GET':
       return render_template('AdminScreen.html', msg='')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/ViewTransaction', methods=['GET', 'POST'])
def ViewTransactions():
    if request.method == 'GET':
       return render_template('ViewTransaction.html', msg='')

@app.route('/SendAmount', methods=['GET', 'POST'])
def SendAmounts():
    if request.method == 'GET':
       return render_template('SendAmount.html', msg='')

@app.route('/Signup', methods=['GET', 'POST'])
def Signup():
    if request.method == 'GET':
       return render_template('Signup.html', msg='')

@app.route('/UserScreen', methods=['GET', 'POST'])
def UserScreen():
    if request.method == 'GET':
       return render_template('UserScreen.html', msg='')

@app.route('/ViewBalance', methods=['GET', 'POST'])
def ViewBalances():
    if request.method == 'GET':
       return render_template('ViewBalance.html', msg='')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
       return render_template('index.html', msg='')


if __name__ == '__main__':
    app.run()       
