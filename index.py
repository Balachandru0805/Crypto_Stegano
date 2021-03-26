from flask import Flask, request, send_file
from flask.templating import render_template
import pyDes
import base64
from PIL import Image
from stegano import lsb
from cryptosteganography import CryptoSteganography

app = Flask(__name__)



@app.route('/')
@app.route('/home')
def Home():
    return render_template('main_page.html')

@app.route('/about_us')
def Contact():
    return render_template('about_us.html')

@app.route('/encrypt_text')
def fun1():
    return render_template('encrypt_text.html')

@app.route('/decrypt_text')
def fun2():
    return render_template('decrypt_text.html')




@app.route('/enc_txt_action',methods=["POST"])
def EncryptText():
    plain_text = request.form.get("plain_text")
    #print(plain_text)
    cover = request.files.get("img1")
    cover.save('Static/tc_image.png')
    cc_im= Image.open('Static/tc_image.png')
    method = request.form.get("methods")
    key = request.form.get("key")
    if method == 'triple_des':
        print('started')
        data = plain_text
        alg = pyDes.triple_des(key) 
        cipher_text  = alg.encrypt(data)
        #print('Cipher Text',cipher_text)
        encrypted_data = base64.b64encode(cipher_text).decode()
        #print(encrypted_data)
        stego = Image.open('Static/tc_image.png')
        sec_img = lsb.hide(stego,encrypted_data)
        sec_img.save('Static/secret.png')

        
    elif method == 'aes':
        crypto_steganography = CryptoSteganography(key)
        crypto_steganography.hide('Static/tc_image.png', 'Static/secret.png', plain_text)

    return render_template('enc_text_output.html')

@app.route('/dec_txt_action', methods=["POST"])
def DecryptText():
    secretImg = request.files.get("img1")
    method = request.form.get("methods")
    key = request.form.get("key")
    if method == 'triple_des':
        alg = pyDes.triple_des(key) 
        encrypted_data_retrival = lsb.reveal(secretImg)
        cypher_data = base64.b64decode(encrypted_data_retrival)
        plain_text = alg.decrypt(cypher_data)
        file = open("Static/decrypted_message.txt","w")
        file.seek(0)
        file.write(str(plain_text))
        file.close()
        #print('Secret Message :',plain_text)
    elif method == 'aes':
        crypto_steganography = CryptoSteganography(key)
        secret = crypto_steganography.retrieve('Static/secret.png')
        file = open("Static/decrypted_message.txt","w")
        file.seek(0)
        file.write(str(secret))
        file.close()
        #print('Secret Message :',plain_text)
    else:
        print("Hi")
    return render_template('dec_text_output.html')
    

@app.route('/enc_text_download')
def fun11():
    return send_file('Static/secret.png',as_attachment=True)

@app.route('/dec_text_download')
def fun12():
    return send_file('Static/decrypted_message.txt',as_attachment=True)


    
if __name__ == '__main__':
    app.run()
