# Rancher Server Deployment

To start deploying Rancher server, copy this directory in your server
to a certain location. We will call it ```BASE_DIR```.

# Starting Rancher Server

Go to directory ```BASE_DIR``` and do necessary settings:

1. Change server name.

Go into ```BASE_DIR/nginx-conf.d/rancher-server.conf```.
Change ```rancher.bnpb.go.id``` to your appropriate domain name.

2. Fill certificate information

Go into ```BASE_DIR/ssl-cert``` and you have to provide the following
certificate files:

- ```certificate.cert``` Public certificate
- ```pri-decrypted.key``` Decrypted (without passphrase) of private key for the certificate to be loaded by nginx

3. Spin up Rancher server

Do ```make up``` to start the server at port 8080.
Do ```make down``` to shutdown server.

# References

https://rancher.com/docs/rancher/v1.6/en/installing-rancher/installing-server/basic-ssl-config/

