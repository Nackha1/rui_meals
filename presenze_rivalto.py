from urllib.request import urlopen
from datetime import datetime, timedelta
import ssl
import json
import csv


def get_date(msg):
    input_str = str(input(f"{msg} date: "))
    try:
        date = datetime.strptime(input_str, "%Y-%m-%d")
    except ValueError:
        print("<!> Incorrect format")
        input("Press any key to close...")
        raise SystemExit

    return date.date()


def fetch_json(date, context):
    url = f"http://mycollegeapp.rui.it/jsonapi?residenza=cml2YWx0bw-&data={date}"
    response = urlopen(url, context=context)
    json_data = json.loads(response.read())
    return json_data


def clean(data, day):
    data = data.get("nomi")

    for person in data.get("Pranzo"):
        del person["dieta"]
        person[f"pranzo({day})"] = person.pop("stato")
        person[f"cena({day})"] = [x for x in data.get("Cena") if x.get(
            "nome") == person.get("nome")][0].get("stato")

    return data.get("Pranzo")


def merge(final_data, temp_data, day):
    temp_data = temp_data.get("nomi")

    for person in temp_data.get("Pranzo"):
        del person["dieta"]
        person[f"pranzo({day})"] = person.pop("stato")
        person[f"cena({day})"] = [x for x in temp_data.get("Cena") if x.get(
            'nome') == person.get("nome")][0].get("stato")
        try:
            [x for x in final_data if x.get(
                "nome") == person.get("nome")][0] |= person
        except:
            print(
                f"<!> The list of people changed on the {day}, this program only works if the list of people remains consistent during the time period specified")
            input("Press any key to close...")
            raise SystemExit

    #print(json.dumps(temp_data.get("Pranzo"), indent=4))


def main():
    print("<?> Date formatting: YYYY-MM-DD")
    start_date = get_date("Starting")
    end_date = get_date("Ending")
    delta = end_date - start_date
    csv_file = "Presenze.csv"
    csv_columns = ["nome", f"pranzo({start_date})", f"cena({start_date})"]
    context = ssl._create_unverified_context()
    res = []

    start_time = datetime.now()
    res = clean(fetch_json(start_date, context), start_date)

    for i in range(delta.days):
        day = start_date + timedelta(days=i+1)
        data = fetch_json(day, context)
        merge(res, data, day)
        csv_columns.append(f"pranzo({day})")
        csv_columns.append(f"cena({day})")

    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in res:
                writer.writerow(data)
    except IOError:
        print("I/O error")

    end_time = datetime.now()
    print(
        f"<i> Program completed in: {(end_time-start_time).total_seconds()}s")
    input("Press any key to close...")


if __name__ == "__main__":
    main()
