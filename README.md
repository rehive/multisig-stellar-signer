# Multisig Stellar Signer (MSS)

Signing service for multisig Stellar hotwallet.

The MSS needs to be deployed on your own infrastructure or cloud provider. A Google Cloud Account is required as this signer services makes use of Google's cloud-hosted hardware security module, Cloud HSM to encrypt the stellar private key.

We have included instructions for easily deploying the MSS via Heroku, but the service can be deployed easily as a standard Django web app.

Once deployed, you will run through the configuration steps to create the Stellar private keypair that will form part of your 2/3 Multisig hot wallet. The second of the three keys is a backup key that you will need to create and store securely and the third key is on the Rehive Stellar Extension.

Whenever the Rehive Stellar Extension creates a transaction on behalf of your end-users, it will sign the transaction using it's own key and then forward it to your self-hosted MSS which will add the second signature. This means that Rehive is unable to initiate the transfer of end-user funds without your approval via the MSS.


## Running locally
Create a test HSM on Google Cloud and a test service account as described in the "Prerequisite: Google HSM and Service Account creation" section below. Download a keyfile associated with that service account for local use. Don't use the same HSM and service account for your production setup.

Create a .env file using `.env.example` as a template.

You'll need to have python (ideally via a virtual environment), docker and docker-compose installed.

Start the database:
```
# You need to have your .env file set up with the COMPOSE_FILE var for this command to work
docker-compose up -d postgres
```
Install the python requirements
```
pip install -r requirements.txt
```
Initial migrations
```
./src/manage.py migrate
```
Run the local server
```
./src/manage.py runserver
```
Configure the service as described in the "Configuration: Initial Setup" section below.


## Deployment prerequisites
Before starting the deployment setup it is required to generate and store a backup Stellar private/public keypair. This should be done by the entity that intends on holding custody for the Hot Wallet funds. The *public address* of this keypair is required to complete the setup of the service.

To generate the Stellar keypair we recommend doing this on a secure hardware wallet as follows:

1. Connect your hardware wallet. If using a Ledger, open the Stellar App on the device
2. Navigate to the official Stellar Account Viewer application: https://accountviewer.stellar.org/#!/
3. Deselect the “Use default account” option and ensure that the derivation input field is set to an unused one example 44'/148'/1' (The final digit is the one that should change)
4. Store the derivation path with a note that it is your Hot Wallet backup
4. Click “Sign in with Ledger” or “Sign in with Trezor”
5. Make a note of the public address displayed as “Your Stellar public key.” This should be stored with the derivation path.


## Deployment
We have provided instructions for easily deploying to Heroku below, but the service can be deployed easily as a standard Django web app. If you do not wish to make use of the Heroku deployment, you will need to run your own PostgreSQL database and configure the connection in django settings. With the heroku deployment described below, the database setup as well as django static files deployment is taken care of automatcially.

Whether following the Heroku setup below or your own deployment, be sure to follow [best practices](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/) for a production Django app deployment.

### Prerequisite: Google HSM and Service Account creation
Follow the steps below to create the hardware security module (HSM) on Google Cloud as well as the service account credentials that will be loaded in the MSS in order to access the HSM. Alternatively, both the HSM and the service account can also be created via the Google Cloud Web interface.

#### Install Gcloud CLI
We recommend following https://cloud.google.com/sdk/docs/install to install and setup the CLI for running any required gcloud commands.

#### Enabling the KSM(HSM) for your Gcloud project
While in the project you wish to create the KSM. Browse to the Security Section -> Key Management (https://console.cloud.google.com/security/kms/). Then enable the KSM for your project.

```
# Replace the variables below with the name you would like to use for your HSM key ring, HSM key and GCP service account
# as well as the name of your Google Cloud project and GCP region you would like to create the HSM in.

KEYRING=test-signer
KEY=test-signer-encryption-key
LOCATION=europe-west4
PROJECT=test-project

cloud kms keyrings create $KEYRING --location $LOCATION --project $PROJECT
gcloud kms keys create $KEY --keyring $KEYRING --project $PROJECT --protection-level=hsm --purpose=encryption --location $LOCATION

# Create the service account on Google Cloud with encrypt/decrypt permissions on the HSM
SERVICE_ACCOUNT=test-hsm-service-account
gcloud iam service-accounts create $SERVICE_ACCOUNT --project $PROJECT
gcloud kms keyrings add-iam-policy-binding \
    $KEYRING \
    --location $LOCATION \
    --member serviceAccount:$SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com \
    --role roles/cloudkms.cryptoKeyEncrypterDecrypter
```

### Heroku Deployment
```
APP=test-signer

# Login to heroku and link the app via git
heroku login

# Create the app
heroku apps:create $APP --region eu

# Set to the python build pack for running the django app:
heroku buildpacks:set heroku/python -a $APP
# Add a buildpack for mounting the Google Credentials:
heroku buildpacks:add --index 1 https://github.com/buyersight/heroku-google-application-credentials-buildpack.git -a $APP

# Link the app for deployments via git
heroku git:remote -a $APP

# Download the Google Cloud Service and load it into an env var
gcloud iam service-accounts keys create keyfile.json --iam-account=$SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com --key-file-type=json --project $PROJECT
GOOGLE_CREDENTIALS=$(cat keyfile.json)

# Upload the GOOGLE_CREDENTIALS as a heroku configuration:
heroku config:set GOOGLE_CREDENTIALS=$GOOGLE_CREDENTIALS -a $APP

# Delete the keyfile for security - it is no longer needed and you can always create another in the future
rm -rf keyfile.json

# Add addional env variables needed for the app
heroku config:set USE_HEROKU=True
heroku config:set GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
heroku config:set DEBUG=False -a $APP
heroku config:set STELLAR_NETWORK=LIVENET -a $APP
heroku config:set HORIZON_URL=https://horizon.stellar.org -a $APP
heroku config:set DJANGO_SECRET=<random-generated-string> -a $APP

# Deploy
git push heroku master
# or git push heroku branch-name:main
```

### Configuration: Initial Setup
```
heroku run bash -a $APP

# Run the initial database migrations
python src/manage.py migrate

# Create a new user on the signer service
python src/manage.py create_user <your-username> <your-email> <your-password>
# Securely store the API token and User ID (E.g. in a password manager)

# Run the setup command to create a signing key encrypted by the HSM
python src/manage.py setup_keypair <user-id> <gcp-project-id> <gcp-region> <gcp-hsm-keyring> <gcp-hsm-key>
# Note down the signer service public key for future reference

# Create a secure Stellar keypair (e.g. on a Hardware Wallet or offline computer) and store it securely as the backup key for the multisig wallet.
# Run the setup command to load the public key of the backup keypair into the signer service:
python src/manage.py set_backup_key <user-id> <backup-key-stellar-public-key>
```

### Configure your Rehive company
Once you have the signer setup the details will need to be added to your Rehive company with the Stellar Extension enabled. To do this browse to the Swagger API (https://stellar.services.rehive.io/swagger/). This requires your signer service to be publically accesible.

Login via Swagger: Click the padlock on the right of an endpoint and enter "Token YOUR_REHIVE_ADMIN_TOKEN" in the value and hit Authorize.

Update the Stellar Extension configuration: PATCH the `/admin/company/configuration/` endpoint with the following fields
```
{ 
  "external_signer_url": "YOUR_DEPLOYED_SIGNERS_PUBLIC_DNS",
  "external_signer_key": "YOUR_SIGNER_API_KEY"
}
```

