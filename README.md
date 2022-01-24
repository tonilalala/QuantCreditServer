# Trading Server & Client 



### Environment Setup

All the code has been run and tested on MacOS 10.15.7, Python 3.8

- Go into the downloaded code directory
```
cd <path_to_downloaded_directory>
```
- Setup python environment
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
- Add the project to PYTHONPATH  
```
export PYTHONPATH=$PWD
```



### Run code

- Run server 

```
python server.py --host localhost --port 9999 --minutes 5 --tickers AAPL,IBM --filenames AAPL_price.csv,IBM_price.csv
```

​     --minutes	--tickers.  --filenames. are required fild indicated in the handout.

- Run client 

```
python client.py --host localhost --port 9999
```



### Sample Client Log

> python client.py --host localhost --port 9999
>
> Connecting to server: localhost on port: 9999
>
> What do we want to ask the server?: client --price 2016-07-29-13:34
> The server's response was:
> Server has no data
> Server has no data
> What do we want to ask the server?: client --price 2022-01-21-16:35
> The server's response was:
> AAPL 162.5
> IBM 129.4
> What do we want to ask the server?: client --signal 2022-01-21-16:35
> The server's response was:
> AAPL nan
> IBM nan
> What do we want to ask the server?: client --signal 2016-07-29-13:34
> The server's response was:
> Server has no data
> Server has no data
> What do we want to ask the server?: client --del_ticker AAPL
> The server's response was:
> Delete ticker AAPL, Return Code: 0
> What do we want to ask the server?: client --price 2016-07-29-13:34
> The server's response was:
> Server has no data
> What do we want to ask the server?: client --price 2022-01-21-16:35
> The server's response was:
> IBM 129.4
> What do we want to ask the server?: client --del_ticker AAPLL
> The server's response was:
> Delete ticker AAPLL, Return Code: 2
> What do we want to ask the server?: client --add_ticker NVA
> The server's response was:
> Add ticker NVA, Return Code: 2
> What do we want to ask the server?: client --add_ticker NVDA
> The server's response was:
> Add ticker NVDA, Return Code: 0
> What do we want to ask the server?: client --price 2022-01-21-16:35
> The server's response was:
> IBM 129.4
> NVDA 232.65
> What do we want to ask the server?: client --reset
> The server's response was:
> Reset! Return Code: 0
> What do we want to ask the server?: client --price 2022-01-21-16:35
> The server's response was:
> AAPL 162.5
> IBM 129.4