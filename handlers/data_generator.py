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
    "Integer",
    "Float",
    "Decimal",
    "String",
]

def get_allowed_data_types():
    return ALLOWED_DATA_TYPES

def random_choice(options):
    if options:
        choices = [opt.strip() for opt in options.split(",") if opt.strip()]
        return random.choice(choices) if choices else ""
    return ""

def age_range(options):
    if options and "-" in options:
        try:
            min_age, max_age = map(int, options.split("-"))
            return random.randint(min_age, max_age)
        except Exception:
            return ""
    return random.randint(18, 90)

def date_with_format(options):
    fmt = options if options else "%d/%b/%y"
    try:
        return fake.date().strftime(fmt)
    except Exception:
        return fake.date()

def dob_with_format(options):
    fmt = options if options else "%d/%b/%y"
    try:
        return fake.date_of_birth().strftime(fmt)
    except Exception:
        return fake.date_of_birth()

def integer_generator(options):
    # options: "min-max" or just a number for max (default 1-100)
    if options and "-" in options:
        try:
            min_val, max_val = map(int, options.split("-"))
            return random.randint(min_val, max_val)
        except Exception:
            return random.randint(1, 100)
    elif options and options.isdigit():
        return random.randint(1, int(options))
    return random.randint(1, 100)

def float_generator(options):
    # options: "min-max" or just a number for max (default 1.0-100.0)
    try:
        if options and "-" in options:
            min_val, max_val = map(float, options.split("-"))
            return round(random.uniform(min_val, max_val), 2)
        elif options:
            return round(random.uniform(1.0, float(options)), 2)
    except Exception:
        pass
    return round(random.uniform(1.0, 100.0), 2)

def decimal_generator(options):
    # options: "min-max,precision" (e.g. "1-10,3"), or just "precision" (e.g. "4")
    min_val, max_val, precision = 1.0, 100.0, 1
    if options:
        try:
            if "-" in options:
                # e.g. "1-10,3"
                range_part, *precision_part = options.split(",")
                min_val, max_val = map(float, range_part.split("-"))
                if precision_part and precision_part[0].isdigit():
                    precision = int(precision_part[0])
            elif options.isdigit():
                precision = int(options)
        except Exception:
            pass
    value = random.uniform(min_val, max_val)
    return round(value, precision)

def string_generator(options):
    # options: length or pattern (default 10 chars)
    length = 10
    if options and options.isdigit():
        length = int(options)
    return fake.pystr(min_chars=length, max_chars=length)



# Centralized mapping: each function takes (options)
DATA_TYPE_GENERATORS = {
    "Random Choice": random_choice,
    "Age": age_range,
    "Date": date_with_format,
    "Date of Birth": dob_with_format,
    "Name": lambda options: fake.name(),
    "Title": lambda options: fake.prefix(),
    "Address": lambda options: fake.address(),
    "Gender": lambda options: random.choice(["Male", "Female", "Other"]),
    "Nationality": lambda options: fake.country(),
    "Occupation": lambda options: fake.job(),
    "Education": lambda options: random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
    "Marital Status": lambda options: random.choice(["Single", "Married", "Divorced", "Widowed"]),
    "Contact Email": lambda options: fake.email(),
    "Email": lambda options: fake.email(),
    "Contact Phone Number": lambda options: fake.phone_number(),
    "Phone Number": lambda options: fake.phone_number(),
    "Postcode": lambda options: fake.postcode(),
    "Country": lambda options: fake.country(),
    "Random Number": lambda options: random.randint(1, 1000),
    "Boolean": lambda options: random.choice([True, False]),
    "Company": lambda options: fake.company(),
    "Job": lambda options: fake.job(),
    "City": lambda options: fake.city(),
    "State": lambda options: fake.state(),
    "Street Address": lambda options: fake.street_address(),
    "Zip Code": lambda options: fake.zipcode(),
    "Integer": integer_generator,
    "Float": float_generator,
    "Decimal": decimal_generator,
    "String": string_generator,
}

def generate_field_value(dtype, options=None):
    generator = DATA_TYPE_GENERATORS.get(dtype)
    if generator:
        return generator(options)
    return ""