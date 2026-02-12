from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib

routes = {
    "index.html": {"title": "home", "body": "Welcome to Frug's Homepage"},
    "about.html": {"title": "about", "body": "I Like Frogs"},
    "contact.html": {"title": "contact", "body": "1234 Freddy Fazbear ln., OH 1234"},
    "login.html": {"title": "Form Post Example", "body": open("login.html", "r").read()},
    "signup.html":{"title": "Sign Up", "body":"Join me in the pond"},
    "/user": {"title": "User Page", "body": "Welcome, ##username##!"},
    "/api/response": "{\"message\": \"api response\"}",
    "/api/getAllUsers": "{\"users\": [{\"username\": \"admin\", \"password\": \"admin\"}, {\"username\": \"frug\", \"password\": \"frug\"}]}"
}

users = json.load(open("users.json", "r"))["users"]

class MyServer(BaseHTTPRequestHandler):
    # this method handdles all the GET requests
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in routes:
            # set up the restulf api response
            if self.path.startswith("/api/"):
                self.send_response(200) # 200 means OK
                self.send_header("Content-type", "application/json")
                self.end_headers()
                body = json.dumps(routes[path])
                self.wfile.write(bytes(body, "UTF-16"))
                return
            else:
                # we will send a response to the client
                self.send_response(200) # 200 means OK
                self.send_header("Content-type", "text/html")
                self.end_headers()
                body = self.load_template(routes[path]["title"], routes[path]["body"])
                split_path = self.path.split("?")
                if len(split_path) > 1:
                    message = urllib.parse.parse_qs(split_path[1])["message"][0]
                else:
                    message = ""
                body = body.replace("##message##", message)
                self.wfile.write(bytes(body, "UTF-16"))
                return
        else:
            # we will send a response to the client
            self.send_response(404) # 200 means OK
            self.send_header("Content-type", "text/html")
            self.end_headers()
            message = self.load_template("404", "404 Not Found")
            self.wfile.write(bytes(message, "UTF-16"))
            return
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)    
        kvp = post_data.decode("UTF-8").split("&")
        for kv in kvp:
            key, value = kv.split("=")
            if key == "username":
                username = value
            if key == "password":
                password = value
        found = False
        message = ""
        for user in users:
            if username == user["username"]:
                print(username)
                if password == user["password"]:
                    found = True
                    break
                else:
                    found = False
                    message = "Invalid username or password"
                    break
            else:
                found = False
                message = "Invalid username or password"
        if found:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            message = self.load_template("User Page", f"Welcome, {username}!")
            self.wfile.write(bytes(message, "UTF-8"))
            return
        else:
            self.send_response(301)
            self.send_header("location", "/login?message=" + message)
            self.end_headers()
            # message = self.load_template("Login Page", message)
            #self.wfile.write(bytes(message, "UTF-8"))
            return
        
    def load_template(self, title, body):
        with open("template.html", "r") as file:
            template = file.read()
        message = template.replace("##title##", title)
        message = message.replace("##body##", body)
        return message
    
if __name__ == "__main__":
    webServer = HTTPServer(("localhost", 8080), MyServer)
    print("Server started at the local host port numer is 8080")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
    