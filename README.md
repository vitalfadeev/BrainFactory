## install 
    ./1-install.sh
    ./2-update-settings.sh
    ./3-post-install.sh
    
## Deploy
    ./deploy.sh


## Send logic
- phase 1 (uploading)
    - upload file xls / csv
    - read
      - detect column names 
      - detect column types
    - create SQL table
    - insert data into SQL


- phase 2 (PreAnalyser)
    - run PreAnalyser
    - if OK:
        - go to phase 3 
    - if FAIL: 
        - show errors

 
- phase 3 (NN parameters)


## Setup TF

- TensorFlow
  - in
    - data 
    - config
  - out
    - logs
    - model

- TensorBoard
  - in
    - TF logs
  - out
    - web page

