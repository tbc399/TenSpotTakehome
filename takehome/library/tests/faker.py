'''
Faker: https://faker.readthedocs.io/en/master/
'''
from faker import Faker
from faker_music import MusicProvider  # to provide 'genre's
from faker.providers import (
    company,
    lorem,
    person,
    python,
)


faker = Faker(locale='en_US')
faker.add_provider(company)
faker.add_provider(lorem)
faker.add_provider(person)
faker.add_provider(python)
faker.add_provider(MusicProvider)
