from flask import Flask, request # This import the Flask framework and import 2 tools , flask for crearte server and request to read incoming mensages from Meta
import requests # This import the requests library to send HTTP requests to Meta API
from config import ACCESS_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN, MENU, CHEF_NUMBER, DELIVERY_NUMBER , GROQ_API_KEY # Goes to the config file and grab the 6 variables that we  can use here in app.p
from groq import Groq

app = Flask(__name__) # It is an object named "app" from the class "Flask" and it recieves the parameter "__name__" Which is a varible that saves the name of the file. flask gets the name of the file where the code was so it can locate the file and create the web server in it.
user_sessions = {} # this is an empty dictionary for store each customer's conversation state


def send_message(to, message): # this function is for send messages to the customers using Meta API, it takes 2 parameters, the first one is the phone number of the customer and the second one is the message that we want to send, the two parameters can be name whatever you want, but in this case we use "to" and "message" for make it more clear in spanich, "to" means "para" and "message" means "mensaje"
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages" # this is the enpoint of the Meta API for send messages, we use f-string to insert the phone number id that we grab from config.py, this endpoint is the one that we need to call for send messages to the customers using Meta API, the enpont it's form dor 3 parts, the first part is the base url "https://graph.facebook.com/v25.0/", the second part is the phone number id that we grab from config.py and the third part is "/messages" that is the endpoint for send messages to the customers using Meta API
    headers = { # this is the dictionary that we call "headers" because it contains the headers that we need to send in the HTTP request to Meta API, the headers are important because they contain the information that Meta API needs to authenticate our request and know what kind of data we are sending, in this case we need to send 2 headers
        "Authorization": f"Bearer {ACCESS_TOKEN}", # this header is for authenticate our request to Meta API, we use f-string to insert the access token that we grab from config.py, the access token is a long string that Meta API gives us when we create our app in Meta for Developers, this token is like a password that we need to include in our requests to Meta API so they know that we are authorized to use their services 
        "Content-Type": "application/json" # this header is for tell Meta API that the data we are sending in the HTTP request is in JSON format, this is important because Meta API needs to know how to parse the data we are sending and understand it correctly, if we don't include this header or if we put a different value, Meta API might not understand our request and return an error
    }
    data = { # This is a dictionary that we call "data" because it contains the data that we need to send in the body of the HTTP request to Meta API, this data is important because it contains the information that Meta API needs to know in order to send the message to the customer, in this case we need to include 4 key-value pairs in this dictionary
        "messaging_product": "whatsapp",# this key-value pair is for tell Meta API that we are using WhatsApp as our messaging product, this is important because Meta API supports different messaging products like Instagram, Messenger, etc. and they need to know which one we are using so they can route our message correctly
        "to": to, # it's the key-value pair for tell Meta API the phone number of the customer that we want to send the message to, we use the "to" parameter that we receive in the function, this is important because Meta API needs to know where to send the message
        "type": "text",# this is the key-value pair for tell Meta API that the type of message we are sending is a text message, this is important because Meta API supports different types of messages like images, videos, etc. and they need to know which one we are sending so they can handle it correctly
        "text": {"body": message} # this is the key-value pair for tell Meta API the content of the text message that we want to send, we use the "message" parameter that we receive in the function, this is important because Meta API needs to know what is the content of the message so they can send it to the customer
    }
    response = requests.post(url, headers=headers, json=data) # this line is for send the HTTP POST request to Meta API using the requests library, we include the url, headers and data that we defined in the previous lines, this is important because this is the line that actually sends the message to the customer using Meta API, if we don't include this line or if we make a mistake in it, our function won't work and we won't be able to send messages to the customers, post is the method that we use for send data to Meta API, we need to use post because we are sending data in the body of the request, if we use get it won't work because get is for request data from Meta API, not for send data to Meta API
    print(f"Meta status: {response.status_code}")  # ← add this!
    print(f"Meta response: {response.text}")  

"""def get_menu_text(): # this function is for generate the text of the menu that we want to send to the customers, this fuunctions is named "get_menu_text" because it returns the text of the menu that we want to send to the customers
    menu_text = "🫓 *Bienvenido a REYPAS!* 🫓\n\nElige tu arepa:\n\n" # This is a variable with the first line of the menu 
    for number, products in MENU.items(): # this is a for loop, key is the number of the menu option and products is the dictionary that contains the name and price of the arepa, we use the items() method to get both the key and the value of each item in the MENU dictionary that we grab from config.py, this is important because we need to loop through all the items in the menu and generate a line of text for each one of them
        menu_text += f"{number}. {products['name']} - ${products['price']:,}\n"# this line function of the next form : menu_text is the variable += (this means that we are adding more text to the variable menu_text) we use [] to access the name and price of the arepa from the products dictionary and in the final of the line we add ":," to format the price with commas for thousands, this is important because we want to generate a nice looking menu text that we can send to the customers
    return menu_text
"""
@app.route("/webhook", methods=["GET"]) # this line is made up for: "@" this is the decorator symbol, it adds extra behavior to the function that we define directly below it, "app.route" "app" is our flask server and ".route" is a method that we use to connects a URL to a function, when that URL receives a request, that function runs "/webhook" is the last part of the URL that we want to connect to the function and "methods=["GET"]" is for reading incoming messages from Meta API, Meta API sends a GET request to this URL when it wants to verify our webhook, this is important because we need to have this route and this method for be able to connect our server with Meta API and receive messages from the Meta API, if we want to receive messages from Meta API we have to take the python app.py  and ngrok run in terminal without it the bot can't receive messages from Meta API. This line is for tell our Flask server that when it receives a GET request to the "/webhook" URL, it should run the function "verify_webhook" that we define below, this is important because this is how we connect our server with Meta API for the verification process, if we don't include this line or if we make a mistake in it, Meta API won't be able to verify our webhook and we won't be able to receive messages from Meta API
def verify_webhook(): # This is the function that runs When meta API sends a GET request, it is made up for: "def" this is the keyword for define a function, "verify_webhook" is the name of the function and "()" means that this function doesn't receive any parameters because this function don't need any information of outside.
    mode = request.args.get("hub.mode") # this line save the hub.mode parameter that Meta API sends in the GET request in a variable named "mode", we use "request.args.get" to get the value of the parameter from the URL query string, this is important because Meta API sends this parameter to tell us what is the purpose of the GET request, if we don't include this line or if we make a mistake in it, we won't be able to verify our webhook correctly, "request" is the object that Flask provides to access the incoming request data, "args" is the dictionary  that contains the query parameters of the URL and "get" is the method that we use to get the value of a specific parameter by its name, in this case we want to get the value of "hub.mode" parameter that Meta API sends for verification, this parameter is important because it tells us if the GET request is for verification or for something else, if we don't check this parameter we might end up accepting requests that are not for verification and that could be a security risk this parameter always is named "suscribe" this is the key word. args.get() it's only used for get the query parameters of the URL.
    token = request.args.get("hub.verify_token") # this line is the sama as the previous one but for it we're going to get the "hub.verify_token" that is the name of the password field because we need verify if it's the same that we set in config.py and we're going to save it in a variable named "token".
    challenge = request.args.get("hub.challenge") # this line is the same as the previous one  but for it we're going to get the "hub.challenge" that is a random string that Meta API sends in the GET request for verification and this is saved in a variable named "challenge". with this variable we'll say to Meta "ok we accept your request" and this code is for meta know that we want to accept this one.
    if mode == "subscribe" and token == VERIFY_TOKEN: # this line verify if the "mode" is "subscribe" and if the "token" is the same that we set in config.py.
         return challenge, 200 # if the previous condition is true, this line return the "challenge" that Meta API sends in the GET request and a status code of 200, "200" is like a green ligth in HTTP that means "OK everything is fine" without this number meta API won't know that we accept the verification request and it won't verify our webhook. the both valuer are important.
    return "Forbidden", 403 # if the previous condition is not true, this line return a message "Forbidden" and a status code of 403,"forbidden" means "you don't have permission to enter!" and "403" is like a red light in HTTP that means "Forbidden" the both values means the dame but forbidden is for human and 403 is for Meta API and for machine.

@app.route("/webhook", methods=["POST"])# it line does the same as the previous @app.route but this time we use "POST" method because this is for receive the messages that customers send to our WhatsApp bot, we use POST method because it can read the body of the request that Meta API sends, the GET method only can read the query parameters of the URL.
def receive_message():# it is the function for receive messages from customers and get parameter number and message of customer for "handle_message" function runs , this function it's named "receive_message"
    data = request.get_json() # it's a variable named "data" that save the JSON data that Meta API sends and save it in the body of the POST request, request.get_json() it is a method only used for read the JSON data from the body and convert it into a Python dictionary that we can work with.
    # print(data) This line is for print the data that we receive from Meta API in the terminal
    try: # try is use for handle errors, in this case meta API sends diferents types of requests to our webhook, not only the messages that customers send, but also notifications about the status of the messages, delivery reports, etc. and we only want to process the messages that customers send, if we try to access data that doesn't exist in the request we will get an error and our server might crash, so we use try-except block to handle this situation and avoid that our server crashes when we receive a request that doesn't have the expected data.
        message = data["entry"][0]["changes"][0]["value"]["messages"][0] # it's a vatiable named "message" that save the variable data the variable data is a dictionary that contains all the information that Meta API sends in the POST request, this line is for access the specific part of the data that contains the message that the customer sent to our WhatsApp bot,  each step of this line is for access a specific level of the nested dictionary that Meta API sends, "entry" is a list that contains all the entries of the request, we take the first one with [0], "changes" is a list that contains all the changes of the entry, we take the first one with [0], "value" is a dictionary that contains the value of the change, "messages" is a list that contains all the messages that are included in the value, we take the first one with [0] because usually there is only one message per request, only the last part of this code is that we'll use for access the content of the message that the customer sent
        from_number = message["from"] # this line save the phone number of the customer that sent the message in a variable named "from_number", we access this information from the "message" variable tha was defined in the previous line.
        msg_text = message["text"]["body"].strip() # this line works like this: msg_text save the content of the "message" variable, we acces to this content with ["text"]["body"] because is a dictionary nested,  the last part is "strip()" that is a method that we use to remove any extra spaces at the beginning or at the end of the message text
        handle_message(from_number, msg_text) # this line is for call the function "handle_message" that we define below and pass the "from_number" and "msg_text" as parameters for this function can process the message and generate a response for the customer.
        print(msg_text)

    except: # this catches any error in the try block (Meta also sends sent/delivered/read notifications without the "messages" key, which raise KeyError here), but now we log the real error instead of silencing it
        pass
    return "OK", 200 # this always runs, error or not, so Meta always gets a valid HTTP response and doesn't retry/disable the webhook


""" def handle_message(from_number, msg_text):
    session = user_sessions.get(from_number, {"step": "menu"}) # This line breaks down as follows: We create a variable named "session", this variable will save the state of the conversation with the customer, "user_sessions"is the dictionary that we defined for save the conversation state of each customer ".get()" is a method that we created for get the conversation state of a specific customer by their phone number , this works of the folloing way: get method is for search a key value in a dictionary (this method is especific only for dictionarys), if the key doesn't exist in the dictionary, it returns a default value named none or we can specify a custom default value, in this case we specify a custom default value that is a dictionary with the key "step" and the value "menu", this means that if the customer's phone number is not in the user_sessions dictionary, we will start a new conversation with that customer and we will set the initial step of the conversation to "menu", some important things is that the get method doesn't save nothing in the user_sessions dictionary, it only returns the value of the key if it exists or the default value if it doesn't exist, if the number does exist the get methond returs the value that have the number in this moment and return us the step that have the key in this moment 
    # This is a example for the each peticion that make the customer and what step and order etc, the dictionary save

    # {'573116359685': {'step': 'waiting_order'}}
    # {'573116359685': {'step': 'waiting_address', 'order': {'name': 'Arepa de Choclo', 'price': 3500}}}
    # {'573116359685': {'step': 'menu', 'order': {'name': 'Arepa de Choclo', 'price': 3500}, 'address': 'Sgsxzcs'}}
    
    # for each message that the customer sends to the bot, the step will change too , the step will be overwritten, the dictinary will only save the content of the customer want, for example oder, addres, name of the product etc, but the step will be always overwritten this one won't be saved only it'll be save the last step the customer was left.

    if session["step"] == "menu": # this is a conditional statement if-else, this line wokrs of the next way: "session["step"]" "session" is an dictionary and it are going to search the key "step" in to the diccionaty and it'll valid if the key step have a value named "menu", if the value is the step is menu the block bellow will be executed if the value is not found, it will follow the else statement of the condicional.
        send_message(from_number, get_menu_text()) # This is the next part of the code if the validation is true we call the function "send_message" that we defined previuslly this function asks us 2 parameters, the first parameter is the phone number of the customer and the second one is other function named "get_menu_text()" it was defined previuslly too, this one is for get the menu to arepas 
        user_sessions[from_number] = {"step": "waiting_order"} # Ok this line will take the dictionary crated for save states of the customer and could happend two posibilitys things, if the number to cutomer exist it will overwriting the step for the new one ({"step": "waiting_order"} if on the contrary the number doesn't exists this will add the number of the custumer and it will add the step in this case it is the thing that happened.
    elif session["step"] == "waiting_order": # it is an else if condicional it line does the same thing to previus validation but in this case we'll valid if the value saved in the key to the dictinary "session" is "waiting_order", if the key is equal it will be run the code bellow
        if msg_text in MENU: # this is a if condicion that valid if the message that customer sent is in the MENU key that we created in our MENU, if message is in the MENU it'll execute the code bellow
            item = MENU[msg_text] # it works the next way: "MENU" is the menu that we created previuslly, "[msg_text]" it is the number to product that the customer sent to bot and it will search the number to product and finally the name and price to the customer will be saved in a variable named "item"
            session["order"] = item # it will create the key named "order" to customer in the dictionary that we created previuslly and it will save the variable item in it
            session["step"] = "waiting_address" # it will overwrites the step that there was for "waiting_address" for next step of the bot
            user_sessions[from_number] = session # finally it will overwrites all user_session for the customer's number with all variables saved previuslly in the variable "session"
            send_message(from_number, f"✅ Elegiste: {item['name']} - ${item['price']:,}\n\nAhora envíame tu dirección de entrega:") # It is he messagee that will be send to customer if all previuslly thing were correct executed the message contain the vaiable item['name'] and item['price'] that they are the values of MENU creaated and we are going to say to customer that he haave to text the home addres
        else: # it is the else conditional and it will be execute if the message that custumer sent is diferent to the keys of the MENU 
            send_message(from_number, "❌ Opción no válida. Elige un número del menú.") # it will send a message using the  send_message fuction the mesagge in for say to the customer that chose the valid option of Menu
            send_message(from_number, get_menu_text()) # then it will send the menu again

    elif session["step"] == "waiting_address": # if the step is waiting_addres it will exeute the code bellow
        session["address"] = msg_text # this automatucallly the customer send message it will save the messaage in a new key named "adress"
        session["step"] = "menu" # It will update the step to "menu" for procces a new request to customer
        user_sessions[from_number] = session # and finally we will update the user_session of number to customer 
        order_summary = f"🛒 *NUEVO PEDIDO REYPAS*\n\n📱 Cliente: {from_number}\n🫓 Pedido: {session['order']['name']}\n💰 Precio: ${session['order']['price']:,}\n📍 Dirección: {msg_text}" # it is a variable named "oder_summary" it will save the finall message ti sent to cheff number and delivery number 
        send_message(CHEF_NUMBER, order_summary) # here we are goint to use the variable to cheff
        send_message(DELIVERY_NUMBER, order_summary) # here to delivery 
        send_message(from_number, "✅ *Pedido confirmado!* Tu arepa está en camino 🛵\n\n¡Gracias por elegir REYPAS!") # and finally we are going to send the finally message to customer to tell them that oder is in way.

    # print(user_sessions) 
"""

def handle_message(from_number, msg_text): # It is a function named "handle_message" that receives two parameters, the firt one is from_number that is the phone number of the cutomer and the second one is msg_text that is the message that the customer sent to our whatsapp bot
    if from_number not in user_sessions: # It is a condicional that valid if the number of the customer is not in the dictionary that we created for save the state of the conversation.
    
        user_sessions[from_number] = [] # If the conditional is true it line will create a new key in the dicttionary with the number of the customer and it will save an empty list in it (It have to be a list for it can save the dicts with each rol and message), if the codicinal is false the it line won't run.
    
    user_sessions[from_number].append({ # Then the saved customer's number and creare a empty List We will save in a dict with 2 keys, values
    "role": "user", # It key-value is for know that is a customer 
    "content": msg_text # It is for save the msg of the customer
    })
    try:
        client = Groq(api_key=GROQ_API_KEY) # This is an object of the class Groq, and I put the key as a parameter and it will initialize the connection with Groq using all the functions and methods of its class
        response = client.chat.completions.create( # This line break down in the following way: "response" It is a variable that will save the AI's response, "client"is our current connection with Groq, "chat" is a subclass of Groq for sending text messages,there are more subclases like audio and image, "completions" is a subclas of chat, and "create" is a method from completions that creates the request to Groq.
            model="openai/gpt-oss-20b", # It is the AI model  that we will use, it is the most capable free model from Groq. 
            messages=[ # It is a variable named "messages" that save the instructions for Groq and the conversacion history
                { # These are the instructions for the bot to work of correctly with the customers
                    "role": "system", # It is a key-value pair that indentifies the message as instruccions for the IA
                    # It is the content of the instruccions for the bot can talk with customers
                    "content": """ Eres el asistente de REYPAS, 
                    una arepería en Bogotá Colombia.

                    Responde naturalmente al cliente.
                    Solo muestra el menú cuando el cliente
                    lo pida o quiera ordenar.

                    Menú:
                    Arepas
                    Arepa BURGER $14900
                    Arepa TIPICA $12900
                    Arepa POWER $7900
                    Arepa ReQuesuda $4500
                    Arepa JQ $2900
                    Arepa Sencilla $1400
                    Bebidas
                    Gaseosa $3500
                    Agua $2500
                    Hit $3500
                    Tinto $2500
                    Perico $3500
                    milo $3500

                    REGLAS ESTRICTAS:

                    1. SOLO responde a lo que el cliente escribió
                    2. NUNCA envíes mensajes adicionales después de responder
                    3. NUNCA digas "¿En qué más puedo ayudarte?"
                    4. NUNCA digas "¡Hola de nuevo!"
                    5. NUNCA hagas seguimiento si el cliente no escribe
                    6. Una sola respuesta por mensaje del cliente
                    7. Respuestas CORTAS y directas
                    8. Arepa burguer lleva carne, jamon, queso, lechuga, salsas al gusto, arepa tipica lleva carne, arepa power lleva Huevos, arepa requesuda lleva queso, arepa jq lleva jamon y queso, arepa sencilla lleva solo arepa.
                    9. Si el cliente pide el menu mandale este link https://reypas-menu.netlify.app/ y ponle un mensaje bonito mas el link
                    10. Solo responde preguntas sobre el pedidos si pregunta cualquier otra cosa dile que solo respondes mensajes de el pedido
                    11. Sugierele productos especificos con nombre y precio  al cleinte para subir el tiket por pedido, hablale de forma que el client acpte hablale muy convncente 

                    - Responde siempre en español!
                    
                    - Si alguien te pregunta sobre quien te creo di, soy una empresa de inteligencia Aretificial llamada DiCsAI que automatiza los mesajes por whatsapp.

                    - Recuerda esto siempre: Si el cliente no responde, no mandes mas mensajes espera a que el cliente vuelva a escribir para volver a enviar mensajes.

                    - El valor de el envio es de 2000 siempre, no muestres ni digas cuanto es el valor de el domicilio solo sumalo al precio final. 
                    
                    - Solo di el precio de el domicilio si el cliente lo pregunta y da una explicacion clara y concisa de porque se cobra

                    - No se te olvide siempre que si el pedido es para llevar, preguntar por la direccion
                    
                    """
                }
            ] + user_sessions[from_number], # This adds the full conversation history of the customer
                                            # So the AI can remember everithing that was said before 
                                            # and respond accordingly in context 
            max_tokens=1000 # It is the limit that the IA can spend for each response
        )                  # for each response, 1 token ≈ 4 characters,
                        # 500 tokens ≈ ~375 words maximum,
                        # this keeps responses SHORT and FAST!
        
        ai_response = response.choices[0].message.content
        print(f"DEBUG - ai_response: '{ai_response}'", flush=True)

    except Exception as e:
        print(f"GROQ ERROR: {e}", flush=True)
        ai_response = "Lo siento, tuve un problema. Intenta de nuevo en un momento."

    user_sessions[from_number].append({
        "role": "assistant",
        "content": ai_response
    })
    send_message(from_number, ai_response)
    

if __name__ == "__main__": # How __name__ and "__main__" works: When You run the code,Python automatically assigns "__main__" to "__name__" in the file you  ran directly. If that file imports another file,the imported file gets its file name as __name__ instead.Python only assigns "__main__" to one file --the one you executed directly
    app.run(debug=True, port=5000) # If the previuslly conditional is true, it line will be executed, this line works to the next way: "app" is the object where be the web service, ".run"  it is a method that runs all web service and all code above, begins listening for incoming http requests, it keeps running until you press ctrl+c, "debug=True" it is to show detailed error messages in terminal, Auto-restars when you save code changes (you don't have to run the code again for it),it never have to be used in production and finally "port=5000" it is a "TPC socket" (enpoind for trasmit information trougth http requists ), this is the door where the requsts can conect with our bot

