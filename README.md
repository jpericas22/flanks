# Prueba técnica Flanks (Jaime Pericás)

## Requeriments
- docker
- docker-compose
- minikube
- kubectl
- kompose
tested on minikube running on KVM

## Build

- Make sure you have already started minikube
- Make sure port 5000 is free (needed for minikube local registry)
- run ./build.sh on project root dir and follow instructions

## API Doc

### POST /auth

returns token required in api requests

#### request body
expects json with parameters
- username (string)
- password (string)

#### response body
returns json with parameters
- token (string) : auth token for future requests (Authorization header), expires in 5min


### POST /renew

renews token

#### request body
empty

#### response body
returns json with parameters
- token (string) : auth token for future requests (Authorization header)


### POST /address/{address_hash}/transaction

returns transactions of address

#### path parameters
- address_hash (string): address hash of address to query

#### request headers
- Authorization=Bearer {token}
> fetch token with route /auth

#### request body
expects json with parameters
- from (string) (optional): filter by sender address
- to (string) (optional): filter by receiver address
- date_from (string) (optional): format = DD-MM-YYYY HH:MM, filter by minimum transaction date
- date_from (string) (optional): format = DD-MM-YYYY HH:MM, filter by maximum transaction date
- page (int) (optional): page to query (default 0)
> if no filters applied, send empty json object

#### response body
returns json with parameters
- count (int): items returned
- countTotal (int): total items matching criteria
- page (int): current page (starts at 0)
- pageTotal (int): available pages
- results (array)
  - hash (striny)
  - amount (float)
  - type (string)
  - baseTransactions (array)
  - leftParentHash (array) (encrypted): returns encrypted chunks with provided public key
  - rightParentHash (string)
  - trustChainConsensus (boolean)
  - trustChainTrustScore (float)
  - transactionConsensusUpdateTime (date string)
  - createTime (date string)
  - attachmentTime (date string)
  - senderTrustScore (float)
  - childrenTransactionHashes (array)
  - isValid (boolean or null)
  - transactionDescription (string)


### POST /address/{address_hash}/transaction/{transaction_hash}

returns specific transaction

#### path parameters
- address_hash (string): address hash of address to query
- transaction_hash (string): hash of transaction to query

#### request headers
- Authorization=Bearer {token}
> fetch token with route /auth

#### request body
same as POST /address/{address_hash}/transaction

#### response body
same as POST /address/{address_hash}/transaction

## Comentarios

He añadido una opcion para monitorear la cuenta sin tener que realizar la query que devuelve todos los datos. El servicio "monitor" se conecta a un websocket de COTI que devuelve actualizaciones de la cuenta, de momento solo devuelve la información recibida, no inserta nada en la base de datos. Un GET a https://mainnet-nodemanager.coti.io/wallet/nodes devuelve los diferentes WS disponibles.

He añadido el binario de "dockerize" para lanzar los servicios cuando la base de datos y el broker estén activos

He tenido que usar también la api de Google Docs para dar permisos al sheet cuando se crea para que el link sea público

El dump a google sheets está optimizado a nivel de procesamiento, no a nivel de envio de datos. Con tal de reducir carga de procesamiento, se borran los datos del sheet y se vuelven a introducir (en el mismo documento)

La api de google está configurada para usar mis credenciales (archivo g_flanks_k.zip) y reusar un sheet_id hardcodeado en una variable de entorno. El código esta preparado para crear un documento nuevo en caso de que el sheet no exista
