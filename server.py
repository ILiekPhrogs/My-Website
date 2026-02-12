from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib

routes = {
    "/": {"title": "home", "body": "Frug's Homepage"},
    "/about": {"title": "about", "body": "This is what you know about Frug"},
    "/contact": {"title": "contact", "body": "You know nothing about Frug here."},
    "/login": {"title": "Login", "body": open("form.html").read()},
    "/signup": {"title": "Sign Up", "body": open("signup.html").read()},
    "/user": {"title": "User Page", "body": "Welcome, ##username##!"},
}


with open("users.json", "r") as file:
    users = json.load(file)["users"]

def save_users():
    with open("users.json", "w") as file:
        json.dump({"users": users}, file, indent=4)


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
        post_data = self.rfile.read(content_length).decode("UTF-8")
        kvp = urllib.parse.parse_qs(post_data)

        username = kvp.get("username", [""])[0]
        password = kvp.get("password", [""])[0]

        # ---------- LOGIN ----------
        if self.path == "/user":
            for user in users:
                if username == user["username"] and password == user["password"]:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    body = self.load_template("User Page", f"Welcome, {username}!")
                    self.wfile.write(bytes(body, "UTF-8"))
                    return

            # failed login
            self.send_response(301)
            self.send_header("location", "/login?message=Invalid username or password")
            self.end_headers()
            return

        # ---------- SIGNUP ----------
        if self.path == "/signup":

            # Check duplicate username
            for user in users:
                if user["username"] == username:
                    self.send_response(301)
                    self.send_header("location", "/signup?message=Username already exists")
                    self.end_headers()
                    return

            # Create new user
            new_user = {
                "username": username,
                "password": password
            }

            users.append(new_user)
            save_users()   #Persist to JSON file

            # Redirect to login after success
            self.send_response(301)
            self.send_header("location", "/login?message=Signup successful. Please login.")
            self.end_headers()
            return

        
    def load_template(self, title, body):
        with open("template.html", "r") as file:
            template = file.read()
        message = template.replace("##title##", title)
        message = message.replace("##body##", body)
        return message
    
    def save_users():
        with open("users.json", "w") as file:
            json.dump({"users": users}, file, indent=4)

    
if __name__ == "__main__":
    webServer = HTTPServer(("localhost", 8080), MyServer)
    print("Server started at the local host port numer is 8080")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
    