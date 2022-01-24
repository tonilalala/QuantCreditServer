# Trading Server & Client 



### Environment Setup

All the code has been run and tested on MacOS 10.15.7, Python 3.8

- Go into the downloaded code directory
```
cd <path_to_downloaded_directory>
```
- Setup python environment
```
pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
- Add the project to PYTHONPATH  
```
export PYTHONPATH=$PWD
```



### Run code

You have to run server and client separately. Server accept threads from clients.

- Run server 

```
python server.py --host localhost --port 9999 --minutes 5 --tickers AAPL,IBM --filenames AAPL_price.csv,IBM_price.csv
```

​     --minutes	--tickers.  --filenames. are required fild indicated in the handout.

​    --filenames must match --tickers field. I recommend you to include filenames for testing due to API requests limitations.

- Open one another bash and run client 

```
python client.py --host localhost --port 9999
```



### Sample Client Log

###

(env) bash$ python client.py --host localhost --port 9999

Connecting to server: localhost on port: 9999



What do we want to ask the server?: Hello
The server's response was:
Message must start with 'client'! Try again!



What do we want to ask the server?: client --price 2022-01-21-16:35

The server's response was:
AAPL 162.5
IBM 129.4



What do we want to ask the server?: client --signal 2022-01-21-16:35

The server's response was:
AAPL -1.0
IBM -1.0



What do we want to ask the server?: client --del_ticker AAPL

The server's response was:
Delete ticker AAPL, Return Code: 0



What do we want to ask the server?: client --del_ticker AAPLL

The server's response was:
Delete ticker AAPLL, Return Code: 2



What do we want to ask the server?: client --add_ticker NVDA

The server's response was:
Add ticker NVDA, Return Code: 0



What do we want to ask the server?: client --price 2022-01-21-16:35

The server's response was:
IBM 129.4
NVDA 232.65



What do we want to ask the server?: client --reset

The server's response was:
Reset successfully! Return Code: 0



What do we want to ask the server?: exit

Close!