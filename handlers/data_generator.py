import random
import faker

fake = faker.Faker()

ALLOWED_DATA_TYPES = [
    "Random Choice",
    "Name",
    "Title",
    "Address",
    "Gender",
    "Date of Birth",
    "Nationality",
    "Occupation",
    "Education",
    "Marital Status",
    "Email",
    "Phone Number",
    "Age",
    "Postcode",
    "Country",
    "Random Number",
    "Boolean",
    "Company",
    "Job",
    "Date",
    "City",
    "State",
    "Street Address",
    "Zip Code",
]

def get_allowed_data_types():
    return ALLOWED_DATA_TYPES

# Mapping of data types to generator functions
DATA_TYPE_GENERATORS = {
    "Name": fake.name,
    "Title": fake.prefix,
    "Address": fake.address,
    "Gender": lambda: random.choice(["Male", "Female", "Other"]),
    "Date of Birth": lambda: fake.date_of_birth().strftime("%Y-%m-%d"),
    "Nationality": fake.country,
    "Occupation": fake.job,
    "Education": lambda: random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
    "Marital Status": lambda: random.choice(["Single", "Married", "Divorced", "Widowed"]),
    "Contact Email": fake.email,
    "Email": fake.email,
    "Contact Phone Number": fake.phone_number,
    "Phone Number": fake.phone_number,
    "Age": lambda: random.randint(18, 90),
    "Postcode": fake.postcode,
    "Country": fake.country,
    "Random Number": lambda: random.randint(1, 1000),
    "Boolean": lambda: random.choice([True, False]),
    "Company": fake.company,
    "Job": fake.job,
    "Date": fake.date,
    "City": fake.city,
    "State": fake.state,
    "Street Address": fake.street_address,
    "Zip Code": fake.zipcode,
    "Random Choice": lambda: random.choice(["Apple", "Banana", "Cherry", "Date"]),
}

def generate_field_value(dtype):
    generator = DATA_TYPE_GENERATORS.get(dtype)
    if generator:
        return generator()
    return ""