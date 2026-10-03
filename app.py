from flask import Flask, request # This import the Flask framework and import 2 tools , flask for crearte server and request to read incoming mensages from Meta
import sqlite3
import requests # This import the requests library to send HTTP requests to Meta API
import json 
from config import ACCESS_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN, CHEF_NUMBER, DELIVERY_NUMBER , GROQ_API_KEY # Goes to the config file and grab the 6 variables that we  can use here in app.p
from groq import Groq

app = Flask(__name__) # It is an object named "app" from the class "Flask" and it recieves the parameter "__name__" Which is a varible that saves the name of the file. flask gets the name of the file where the code was so it can locate the file and create the web server in it.
user_sessions = {} # this is an empty dictionary for store each customer's conversation state
last_saved_order = {}
order_status = {}

def send_message(to, message): # this function is for send messages to the customers using Meta API, it takes 2 parameters, the first one is the phone number of the customer and the second one is the message that we want to send, the two parameters can be name whatever you want, but in this case we use "to" and "message" for make it more clear in spanich, "to" means "para" and "message" means "mensaje"
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages" # this is the enpoint of the Meta API for send messages, we use f-string to insert the phone number id that we grab from config.py, this endpoint is the one that we need to call for send messages to the customers using Meta API, the enpont it's form dor 3 parts, the first part is the base url "https://graph.facebook.com/v25.0/", the second part is the phone number id that we grab from config.py and the third part is "/messages" that is the endpoint for send messages to the customers using Meta API
    headers = { # this is the dictionary that we call "headers" because it contains the headers that we need to send in the HTTP request to Meta API, the headers are important because they contain the information that Meta API needs to authenticate our request and know what kind of data we are sending, in this case we need to send 2 headers
        "Authorization": f"Bearer {ACCESS_TOKEN}", # this header is for authenticate our request to Meta API, we use f-string to insert the access token that we grab from config.py, the access token is a long string that Meta API gives us when we create our app in Meta for Developers, this token is like a password that we need to include in our requests to Meta API so they know that we are authorized to use their services 
        "Content-Type": "application/json" # this header is for tell Meta API that the data we are sending in the HTTP request is in JSON format, this is important because Meta API needs to know how to parse the data we are sending and understand it correctly, if we don't include this header or if we put a different value, Meta API might not understand our request and return an error
    }
    data = { # This is a dictionary that we call "data" because it contains the data that we need to send in the body of the HTTP request to Meta API, this data is important because it contains the information that Meta API needs to know in order to send the message to the customer, in this case we need to include 4 key-value pairs in this dictionary
        "messaging_product": "whatsapp",# this key-value pair is for tell Meta API that we are using WhatsApp as our messaging product, this is important because Meta API supports different messaging products like Instagram, Messenger, etc. and they need to know which one we are using so they can route our message correctly
        #"to": to, # it's the key-value pair for tell Meta API the phone number of the customer that we want to send the message to, we use the "to" parameter that we receive in the function, this is important because Meta API needs to know where to send the message
        "type": "text",# this is the key-value pair for tell Meta API that the type of message we are sending is a text message, this is important because Meta API supports different types of messages like images, videos, etc. and they need to know which one we are sending so they can handle it correctly
        "text": {"body": message} # this is the key-value pair for tell Meta API the content of the text message that we want to send, we use the "message" parameter that we receive in the function, this is important because Meta API needs to know what is the content of the message so they can send it to the customer
    }
    if str(to).isdigit():
        data["to"] = to
    else:
        data["recipient"] = to

    response = requests.post(url, headers=headers, json=data) # this line is for send the HTTP POST request to Meta API using the requests library, we include the url, headers and data that we defined in the previous lines, this is important because this is the line that actually sends the message to the customer using Meta API, if we don't include this line or if we make a mistake in it, our function won't work and we won't be able to send messages to the customers, post is the method that we use for send data to Meta API, we need to use post because we are sending data in the body of the request, if we use get it won't work because get is for request data from Meta API, not for send data to Meta API
    print(f"Meta status: {response.status_code}")  # ← add this!
    print(f"Meta response: {response.text}") 
 

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
    print(request.get_json())
    data = request.get_json() # it's a variable named "data" that save the JSON data that Meta API sends and save it in the body of the POST request, request.get_json() it is a method only used for read the JSON data from the body and convert it into a Python dictionary that we can work with.
    # print(data) This line is for print the data that we receive from Meta API in the terminal
    """try: # try is use for handle errors, in this case meta API sends diferents types of requests to our webhook, not only the messages that customers send, but also notifications about the status of the messages, delivery reports, etc. and we only want to process the messages that customers send, if we try to access data that doesn't exist in the request we will get an error and our server might crash, so we use try-except block to handle this situation and avoid that our server crashes when we receive a request that doesn't have the expected data.
        message = data["entry"][0]["changes"][0]["value"]["messages"][0] # it's a vatiable named "message" that save the variable data the variable data is a dictionary that contains all the information that Meta API sends in the POST request, this line is for access the specific part of the data that contains the message that the customer sent to our WhatsApp bot,  each step of this line is for access a specific level of the nested dictionary that Meta API sends, "entry" is a list that contains all the entries of the request, we take the first one with [0], "changes" is a list that contains all the changes of the entry, we take the first one with [0], "value" is a dictionary that contains the value of the change, "messages" is a list that contains all the messages that are included in the value, we take the first one with [0] because usually there is only one message per request, only the last part of this code is that we'll use for access the content of the message that the customer sent
        from_number = message["from"] # this line save the phone number of the customer that sent the message in a variable named "from_number", we access this information from the "message" variable tha was defined in the previous line.
        msg_text = message["text"]["body"].strip() # this line works like this: msg_text save the content of the "message" variable, we acces to this content with ["text"]["body"] because is a dictionary nested,  the last part is "strip()" that is a method that we use to remove any extra spaces at the beginning or at the end of the message text
        print(f"DEBUG - customer_response: '{msg_text}'")
        handle_message(from_number, msg_text) # this line is for call the function "handle_message" that we define below and pass the "from_number" and "msg_text" as parameters for this function can process the message and generate a response for the customer.
        

    except: # this catches any error in the try block (Meta also sends sent/delivered/read notifications without the "messages" key, which raise KeyError here), but now we log the real error instead of silencing it
        pass
    return "OK", 200 # this always runs, error or not, so Meta always gets a valid HTTP response and doesn't retry/disable the webhook"""
    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "OK", 200  # avisos de estado (sent/delivered/read), no hay nada que responder

        message = value["messages"][0]
        from_number = message.get("from") or message.get("from_user_id")

        if not from_number:
            print(f"SIN REMITENTE: {message}", flush=True)
            return "OK", 200

        msg_type = message.get("type", "text")

        if msg_type == "location":
            lat = message["location"]["latitude"]
            lng = message["location"]["longitude"]
            maps_link = f"https://maps.google.com/?q={lat},{lng}"
            if CHEF_NUMBER:
                send_message(CHEF_NUMBER, f"Ubicacion de {from_number}:\n{maps_link}")
            handle_message(from_number, f"Mi ubicacion actual es: {maps_link}")
        elif msg_type == "text":
            msg_text = message["text"]["body"].strip()
            print(f"DEBUG - customer_response: '{msg_text}'")
            handle_message(from_number, msg_text)
        else:
            send_message(from_number, "Veci, por ahora solo entiendo mensajes de texto. Escríbeme qué quieres pedir.")

    except Exception as e:
        print(f"WEBHOOK ERROR: {e}", flush=True)
    return "OK", 200
def parse_order(ai_response):
    order = None
    if "<ORDER>" in ai_response:
        try:
            raw = ai_response.split("<ORDER>")[1].split("</ORDER>")[0]
            order = json.loads(raw)
        except Exception as e:
            print(f"ORDER PARSE ERROR: {e}", flush=True)

        ai_response = ai_response.split("<ORDER>")[0].strip()

        if not ai_response:
            ai_response = "¡Pedido Confirmado¡"
    return ai_response, order

def save_order_to_db(order, phone):
    total = sum(item["precio"] * item["cantidad"] for item in order["items"])
    if order["tipo"] == "domicilio":
        total += 2000

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (phone, tipo, direccion, items, total) VALUES (?, ?, ?, ?, ?)",
        (phone, order["tipo"], order.get("direccion"), json.dumps(order["items"]), total)
    )
    conn.commit()
    conn.close()
    print(f"DEBUG - order saved for {phone}, total: {total}", flush=True)
    if CHEF_NUMBER:
        items_lines = "\n".join(
            f"  {item['cantidad']}x {item['nombre']} (${item['precio']:,})"
            for item in order["items"]
        )
        if order["tipo"] == "domicilio":
            entrega = f"Domicilio: {order.get('direccion', 'sin direccion')}"
        else:
            entrega = "Para recoger en local"
        msg = (
            f"NUEVO PEDIDO\n"
            f"{entrega}\n"
            f"Items:\n{items_lines}\n"
            f"Total: ${total:,}\n"
            f"Cliente: {phone}"
        )
        send_message(CHEF_NUMBER, msg)
        
def handle_message(from_number, msg_text): # It is a function named "handle_message" that receives two parameters, the firt one is from_number that is the phone number of the cutomer and, the second one is msg_text that is the message that the customer sent to our whatsapp bot
    if from_number == CHEF_NUMBER:
        parts = msg_text.strip().split(" ", 1)
        command = parts[0].lower()
        if command == "listo" and len(parts) > 1:
            customer_phone = parts[1].strip()
            order_status[customer_phone] = "en camino"
            send_message(customer_phone, "Tu pedido ya va en camino, en unos minutos llega veci!")
            send_message(CHEF_NUMBER, f"Notificado {customer_phone}")
            return
        elif command == "entregado" and len(parts) > 1:
            customer_phone = parts[1].strip()
            order_status[customer_phone] = "entregado"
            send_message(customer_phone, "Pedido entregado! Gracias por tu compra en REYPAS, vuelve pronto veci!")
            send_message(CHEF_NUMBER, f"Entregado {customer_phone}")
            return

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
                    Arepa Queso $2500
                    Arepa Jamon y Queso $3000
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
                    10. Si el cliente saluda o dice cualquier cosa informal, respóndele amigable usando palabras como "veci", "dale veci", "hola veci". Luego pregúntale que queire pedir.
                    11. Sugierele productos especificos con nombre y precio  al cleinte para subir el tiket por pedido, hablale de forma que el client acpte hablale muy convncente 

                    - Responde siempre en español!
                    
                    - Si alguien te pregunta sobre quien te creo no digas nada

                    - Recuerda esto siempre: Si el cliente no responde, no mandes mas mensajes espera a que el cliente vuelva a escribir para volver a enviar mensajes.

                    - El valor de el envio es de 2000 siempre, no muestres ni digas cuanto es el valor de el domicilio solo sumalo al precio final. 
                    
                    - Solo di el precio de el domicilio si el cliente lo pregunta y da una explicacion clara y concisa de porque se cobra

                    - Si el pedido es domicilio, dile al cliente exactamente esto: "Para enviarte el pedido necesito tu ubicación. Por favor toca el clip 📎 → Ubicación → Enviar ubicación actual", leugo sigue con el pedido, SI YA FUE CONFIRMADO ESTA BIEN PERO SI NO HA SIDO CONFIRMADO SIGUE EL PROCESO HASTA QEU EL PEDIDO SE ENVIE A COCINA

                    - REGLA DEL BLOQUE DE PEDIDO:

                    Cuando el cliente confirme el pedido y ya tengas toda la información
                    necesaria, termina tu respuesta con un bloque en este formato exacto:

                    <ORDER>{"tipo": "domicilio", "direccion": "Calle 45 #12-30", "items": [{"nombre": "Arepa POWER", "precio": 7900, "cantidad": 1}, {"nombre": "Gaseosa", "precio": 3500, "cantidad": 2}]}</ORDER>

                    Reglas del bloque:
                    - Emítelo ÚNICAMENTE cuando el pedido esté confirmado. Nunca antes.
                    - Un solo bloque por pedido. No lo repitas en mensajes posteriores.
                    - Si es domicilio, "pide ubicaion actaul" es obligatoria.
                    - Si es para recoger, usa "tipo": "recoger" y omite "direccion".
                    - Usa exactamente los precios del menú. No calcules totales.
                    - Nunca menciones, expliques ni muestres este bloque al cliente.
                    - El mensaje para el cliente va ANTES del bloque, escrito con normalidad.

                    - Regla de ORO no te inventes nada si no sabes algo no digas nada
                    - Si es envio a domicilio, siempre pide la ubicacion actual SIEMRPE

                    """ + (f"\n\nESTADO ACTUAL DEL PEDIDO: {order_status[from_number]}. Responde acorde a este estado." if from_number in order_status else "")
                }
            ] + user_sessions[from_number], # This adds the full conversation history of the customer
                                            # So the AI can remember everithing that was said before 
                                            # and respond accordingly in context 
            max_tokens=1000 # It is the limit that the IA can spend for each response
        )                  # for each response, 1 token ≈ 4 characters,
                        # 500 tokens ≈ ~375 words maximum,
                        # this keeps responses SHORT and FAST!

        ai_response = response.choices[0].message.content
        ai_response, order = parse_order(ai_response)
        
        if order and order != last_saved_order.get(from_number):
            save_order_to_db(order, from_number)
            last_saved_order[from_number] = order
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

