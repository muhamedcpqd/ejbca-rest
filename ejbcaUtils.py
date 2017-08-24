#this file contain utilitary function to help co-autenticate with ejbca
# and configure the ejbcaWSDLbase class
import OpenSSL.crypto
import os
import ssl
import zeep
import requests
from zeep.transports import Transport

#the WSDL service class
global ejbcaWSDLbase

#just and alias
def ejbcaServ():
    return ejbcaWSDLbase.service

def pfx_to_pem(pfx_path, pfx_password):
    #https://gist.github.com/erikbern/756b1d8df2d1487497d29b90e81f8068
    ''' Decrypts the .pfx or .p12 file to be used with requests. '''
    f_pem = open('cert/superadmin.pem', 'wb')
    pfx = open(pfx_path, 'rb').read()
    p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)
    f_pem.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
    f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
    ca = p12.get_ca_certificates()
    if ca is not None:
        for cert in ca:
            f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
    f_pem.close()

def initicalConf():
    global ejbcaWSDLbase
    if not os.path.isfile('cert/superadmin.pem'):
        if not os.path.isfile('cert/superadmin.p12'):
            print "certificado do cliente 'superadmin.p12' nao encontrado no diretorio 'cert'"
            exit(-1)
        pfx_to_pem('cert/superadmin.p12', 'ejbca')

    session = requests.Session()
    session.verify = 'cert/ca.crt'
    session.cert = 'cert/superadmin.pem'
    transport = Transport(session=session)
    try:
        ejbcaWSDLbase = zeep.Client(
            'https://localhost:8443/ejbca/ejbcaws/ejbcaws?wsdl', transport=transport)
    except requests.exceptions.ConnectionError:
        print "Cant connect to EJBCA server"
        exit(-1)    

    ejbcaWSDLbase.options(raw_response=True)