# lec02 — ETL Jobs (job_raw + job_stg)

## 🔹 job_raw
- Flask app (port 8081)
- Accepts POST with `date` and `raw_dir`
- Fetches sales data from API and saves it to JSON
- Idempotent: clears `raw_dir` before saving

## 🔹 job_stg
- Flask app (port 8082)
- Accepts POST with `raw_dir` and `stg_dir`
- Reads all JSON files and writes a single Avro file using `fastavro`
- Schema is auto-generated from the first record

## 🧪 Tests
- Covers `DAL` and `BLL` for both jobs
- Uses `pytest`, `tmp_path`, and `mock`
- Run tests with: `pytest` from `lec02` root

## ⚙️ Config
- `.env`: stores `AUTH_TOKEN` (must be create)
- `config.yaml`: API settings

## 📦 Dependencies
- `Flask`, `requests`, `fastavro`, `pytest`, `python-dotenv`, `pyyaml`
