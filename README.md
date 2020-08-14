# PRUEBA TECNICA FLANKS (JAIME PERICAS)

## REQUERIMENTS
- docker
- docker-compose
- minikube
- kubectl
- kompose
tested on minikube running on KVM

## BUILD
run ./build.sh on root dir

## API DOC

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