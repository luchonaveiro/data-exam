# Mutt Data Exam

## Exercise 1

I will set up my environment using Poetry, to manage all the dependences and enable a reproduceable command line Python app. To do so, i instantiate the project:

```
$ mkdir exercise_1/exercise_1
$ mkdir exercise_1/exercise_1/output
$ cd exercise_1
$ touch exercise_1/__init__.py
$ pip3 install poetry==1.1.8
$ poetry init
```

After completing the init process, we will have a `pyproject.toml` file defined as follows:
```
[tool.poetry]
name = "exercise_1"
version = "0.1.0"
description = "Exercise 1 from Mutt Data Exam"
authors = ["Luciano Naveiro"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
``` 

Now we can install our Python app dependencies (and some dev dependencies also), by running the following commands:
```
$ poetry add requests==2.26.0
$ poetry add black --dev
$ poetry add isort --dev
$ poetry add pytest --dev
$ poetry add pytest-mock --dev
```

I'll add some configuration on the `pyproject.toml` file:
```
[tool.black]
line-length = 79
```

Once somebody clones this repo, as the project is already set up, the only requirement is to have Python 3.8 or higher. To install all the dependencies, you can run:
```
$ poetry install
```

Now we can run some commands to clean the code:
```
$ poetry run isort exercise_1
$ poetry run black exercise_1
```

We can execute some examples to check if everything is fine:

```
$ poetry run python exercise_1/main.py --date=2022-04-10 --coin=bitcoin
```

To set up the cron job, we execute the following:
```
$ crontab -e
```

it will open a vim editor, and there we input the following command:
```
DATEVAR=date +20%y-%m-%d
* 3 * * * python3 exercise_1/main.py --date=$($DATEVAR) --coin=bitcoin
* 3 * * * python3 exercise_1/main.py --date=$($DATEVAR) --coin=ethereum
* 3 * * * python3 exercise_1/main.py --date=$($DATEVAR) --coin=cardano
```

This will execute everyday at 3 AM and store the date for `bitcoin`, `ethereum` and `cardano`

For the Point 3, i will assume that each day's data should be stored separatelly, and I added `tqdm` to monitor the progress of the whole bulk reprocess.

## Exercise 2

On this Exercise, I am going to create another Poetry app, extending the previous on:
```
$ mkdir exercise_2/exercise_2
$ mkdir exercise_2/exercise_2/output
$ cd exercise_2
$ touch exercise_2/__init__.py
$ poetry init
```

After completing the init process, we will have a `pyproject.toml` file defined as follows:
```
[tool.poetry]
name = "exercise_2"
version = "0.1.0"
description = "Exercise 2 from Mutt Data Exam"
authors = ["Luciano Naveiro"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
``` 

Now we can install our Python app dependencies (and some dev dependencies also), by running the following commands:
```
$ poetry add requests==2.26.0
$ poetry add tqdm==4.60.0
$ poetry add sqlalchemy==1.4.35
$ poetry add psycopg2-binary==2.9.1
$ poetry add pandas==1.2.3
$ poetry add black --dev
$ poetry add isort --dev
```

I'll add some configuration on the `pyproject.toml` file:
```
[tool.black]
line-length = 79
```

Now we can run some commands to clean the code:
```
$ poetry run isort exercise_2
$ poetry run black exercise_2
```


To set up the PostgreSQL database, I'll use the [official Docker Image](https://hub.docker.com/_/postgres?tab=description)
```
$ docker pull postgres:13.0
$ docker run --name mutt_db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:13.0
```
The default `POSTGRES_USER` and `POSTGRES_DB` are both `postgres`.

Now , I run `exercise_2/create_tables.py` to create 2 tables:
- `coin_raw`
- `coin_aggregated`

```
$ poetry run python exercise_2/db/create_tables.py
```

I added a new Boolean parameter on `main.py` called `store_data`, in case is `False`, it is just the same as the old `main.py` script. But in case is `True`, data is stored on both tables: `coin_raw` and `coin_aggregated`.
So the logic is as follows:
- for `coin_raw`, it will store on the DB every new combination of `coin_id` and `date`
- for `coin_aggregated`, it will first delete the record from the month belonging to the selected date, it will compute the max/min values again with the new data, and will store this new value.

To populate the tables from values since 2020-01-01, I execute the following commands:

```
$ poetry run python exercise_2/main.py --coin=bitcoin --date=2020-01-01 --store_data_on_db=True --bulk_reprocess=True --end_date=2022-04-14
$ poetry run python exercise_2/main.py --coin=ethereum --date=2020-01-01 --store_data_on_db=True --bulk_reprocess=True --end_date=2022-04-14
$ poetry run python exercise_2/main.py --coin=cardano --date=2020-01-01 --store_data_on_db=True --bulk_reprocess=True --end_date=2022-04-14
```

## Exercise 3
To solve this Exercise, I created 2 queries using the data from `2022-01-01` to `2022-04-14` from `bitcoin`, `ethereum` and `cardano`:
- `exercise_3/avg_monthly_price.sql`: which returns the following:

| coin_id | year_month | avg_price        |
|-----------|--------------|--------------------|
| bitcoin   | 2022-01-01 | 41413.91580726949  |
| bitcoin   | 2022-02-01 | 40648.22165632696  |
| bitcoin   | 2022-03-01 | 41897.67000621025  |
| bitcoin   | 2022-04-01 | 43674.93983449922  |
| cardano   | 2022-01-01 | 1.2269163364346785 |
| cardano   | 2022-02-01 | 1.0315629113580438 |
| cardano   | 2022-03-01 | 0.9337815400992453 |
| cardano   | 2022-04-01 | 1.0818478000646592 |
| ethereum  | 2022-01-01 | 3091.3834038019118 |
| ethereum  | 2022-02-01 | 2863.4249876166464 |
| ethereum  | 2022-03-01 | 2864.979345093724  |
| ethereum  | 2022-04-01 | 3276.7140754157303 |


- `exercise_3/avg_increase_after_drops.sql`: which returns the following:

| coin_id | avg_nominal_increase | avg_percentage_increase | current_market_cap |
|-----------|------------------------|---------------------------|----------------------|
| bitcoin   | 424.8575848682216      | 0.01127334655842378       | 783560801481.9719    |
| cardano   | 0.029080197432107196   | 0.026837297511847897      | 31303049352.34989    |
| ethereum  | 68.87484261145323      | 0.0255933618938961        | 375767680796.0061    |


On this one I assumed that the "the current market cap" is the market cap from the last date I have data.

## Exercise 4

For Exersice 4 I am going to create another Poetry app, and install all the dependencies and Jupyter to use a Notebook. As on the previuous exercises, I initiate teh app by just running the followoing command:

```
$ poetry init
```

After completing the init process, we will have a `pyproject.toml` file defined as follows:

```
[tool.poetry]
name = "exercise_2"
version = "0.1.0"
description = "Exercise 2 from Mutt Data Exam"
authors = ["Luciano Naveiro"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
``` 

Now we can install our Python app dependencies (and some dev dependencies also), by running the following commands:

```
$ poetry add sqlalchemy==1.4.35
$ poetry add psycopg2-binary==2.9.1
$ poetry add pandas==1.2.3
$ poetry add jupyter==1.0.0
$ poetry add matplotlib==3.4.1
$ poetry add holidays==0.13
$ poetry add scikit-learn==0.24.2
```

Now I can launch a Notebook and start working there:

```
$ poetry run jupyter-notebook
```

On this exercise, we can plot the last 30 days point prices of each of the coins, resulting on the following plots
![](exercise_4/exercise_4/output/bitcoin_plot.png)
![](exercise_4/exercise_4/output/ethereum_plot.png)
![](exercise_4/exercise_4/output/cardano_plot.png)


To create the forecast, I am going to use dates from `2020-01-01` to `2021-12-31` as training data, and try to forecast the values from `2022-01-01` to `2022-04-14` and compare them with the real values.

To solve this time series analysis, I am going to use a simple `LinearRegression` from `sklearn`, and just using the price features, and the weekend and holiday ones. As I am using the previuos 7 prices as an input to the model, I will use a recursive multi step forecasting strategy (when forecasting I have to use the result from the previous predictions).

After running the model for each of the three models, we can conlcude that this simple linear model is not even close of catching the breaking points and the different trends, as we can see on the following plots

![](exercise_4/exercise_4/model_output/bitcoin_model_plot.png)
![](exercise_4/exercise_4/model_output/ethereum_model_plot.png)
![](exercise_4/exercise_4/model_output/cardano_model_plot.png)
