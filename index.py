from flask import Flask, request, send_file
from flask.templating import render_template
import pyDes
import base64
from PIL import Image
from stegano import lsb
from cryptosteganography import CryptoSteganography

app = Flask(__name__)


class Steganography(object):
    
    @staticmethod
    def __int_to_bin(rgb):
        """Convert an integer tuple to a binary (string) tuple.
        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        """Convert a binary (string) tuple to an integer tuple.
        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        """Merge two RGB tuples.
        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple
        (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:3] + r2[:5],
               g1[:3] + g2[:5],
               b1[:3] + b2[:5])
        return rgb

    @staticmethod
    def merge(img1, img2):
        """Merge two images. The second one will be merged into the first one.
        :param img1: First image
        :param img2: Second image
        :return: A new merged image.
        """

        # Check the images dimensions
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = Steganography.__int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = Steganography.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img):
        """Unmerge an image.
        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple used to store the image original size
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit
                rgb = (r[3:] + '011',
                       g[3:] + '011',
                       b[3:] + '011')

                # Convert it to an integer tuple
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

                # If this is a 'valid' position, store it
                # as the last valid position
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # Crop the image based on the 'valid' pixels
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image

    

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

@app.route('/encrypt_image')
def fun3():
    return render_template('encrypt_image.html')

@app.route('/decrypt_image')
def fun4():
    return render_template('decrypt_image.html')

    
@app.route("/enc_img_action",methods=["POST"])
def encrypt_image():
  
    c_image = request.files.get("img1")
    h_image = request.files.get("img2")
    c_image.save('Static/c_image.jpg')
    h_image.save('Static/h_image.jpg')
    m1 = Image.open('Static/c_image.jpg')
    m2 = Image.open('Static/h_image.jpg')
    merged_image = Steganography.merge(m1,m2)
    merged_image.save('Static/encrypted_image.jpg')

    return render_template("enc_img_output.html")
        


@app.route("/dec_img_action", methods=["POST"])
def decrypt_image():
    e_image = request.files.get("img1")
    e_image.save('Static/e_image.jpg')
    e_im = Image.open('Static/e_image.jpg')
    unmerged_image = Steganography.unmerge(e_im)
    unmerged_image.save('Static/decrypted_image.jpg')
    
    return render_template('dec_img_output.html')

@app.route('/enc_txt_action',methods=["POST"])
def EncryptText():
    plain_text = request.form.get("plain_text")
    #print(plain_text)
    cover = request.files.get("img1")
    cover.save('Static/tc_image.png')
    cc_im= Image.open('Static/tc_image.png')
    method = request.form.get("method")
    key = request.form.get("key")
   
    if method == 'triple_des':
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
    method = request.form.get("method")
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

@app.route('/enc_img_download')
def fun13():
    return send_file('Static/encrypted_image.jpg',as_attachment=True)

@app.route('/dec_img_download')
def fun14():
    return send_file('Static/decrypted_image.jpg',as_attachment=True)
    
if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0")
