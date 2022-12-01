
from distutils.log import debug
from flask_webhook import app
from OpenSSL import SSL

context = SSL.Context(SSL.TLSv1_2_METHOD)
context = ('/home/raymond.yung.ee/interviewmeplz_com/interviewmeplz_com.crt', '/home/raymond.yung.ee/ssl/server.key')

if __name__ == "__main__":
  app.run(host = '0.0.0.0', port=8080, debug= True, ssl_context=context)
