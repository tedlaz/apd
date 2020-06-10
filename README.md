# apd

Greek EFKA APD check and print


## To install
```bash
git clone https://github.com/tedlaz/apd.git
cd apd
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m apd.apd2pdf <CSL01>
```


## Create docker image and run

```bash
docker build . -t tedlaz/apd
docker run -d -p 8000:8000 --name apd tedlaz/apd
```