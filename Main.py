from urllib.request import urlopen
import json
import ipaddress
from itertools import groupby
from operator import itemgetter
from collections import defaultdict


# sorts and prints data by 3 chosen keys (for example first by region, then by service and finally by ip range)
def sort_by_values(json_data, key1, key2, key3):
    # sort data by 3 keys
    json_data = sorted(json_data, key=lambda x: (x.get(key1), x.get(key2), x.get(key3)))
    for key, value in groupby(json_data, key=itemgetter(key1)):
        print(f'{key1} ' + key + ':')
        # create dictionary where:
        # keys are values of key2 (for example, names of all services in specific region)
        # values are sets of key3 (for example, all ip_ranges in specific service)
        criteria_dictionary = defaultdict(set)
        # add all keys and values to dictionary
        for val in value:
            criteria_dictionary[val[key2]].add(val[key3])
        for k in criteria_dictionary:
            print(f'- ' + k, end=': ')
            print(", ".join(sorted(criteria_dictionary[k])))
        print()


# allows user to choose a specific value (for example specific region or service)
def choose_value(json_data, value):
    print("Please, choose one of these " + value + "s:")
    # creates a set of all unique values (for example, all unique regions or services) to choose from
    value_set = set()
    for prefix in json_data:
        value_set.add(prefix[value])
    print(", ".join(value_set))
    users_choice = input()
    # check whether user's choice is valid
    if users_choice not in value_set:
        print(f'There is no such {value} as {users_choice} in AWS {value}s. Please, try again!\n')
        users_choice = choose_value(json_data, value)
    return users_choice


# finds all prefixes with chosen value (for example all prefixes in specific region or service)
def search_by_value(json_data, criteria, users_choice):
    selected_prefixes = []
    for prefix in json_data:
        if prefix[criteria] == users_choice:
            selected_prefixes.append(prefix)
    return selected_prefixes


# returns a count of ip addresses in selected region or service
# brute force method
def count_ip_addresses(selected_prefixes):
    ips = set()
    for prefix in selected_prefixes:
        [ips.add(str(ip)) for ip in ipaddress.IPv4Network(prefix["ip_prefix"])]
    return len(ips)

# Program starts
url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
# store the response of url
response = urlopen(url)
# return response as json object
data = json.loads(response.read())['prefixes']

use_program = True
print('~Welcome to AWS IP range program~')

while use_program:
    print('~Please select one of these operations:~\n'
          '1 - press one to group AWS IP ranges by region\n'
          '2 - press two to group AWS IP ranges by service\n'
          '3 - press three to see all AWS IP prefixes in the region of your choice\n'
          '4 - press four to see all AWS IP prefixes in the service of your choice\n'
          '5 - press five to calculate the number of available IP addresses in the region of your choice\n'
          '6 - press six to calculate the number of available IP address in the service of your choice')
    operation = input()
    if operation == '1':
        print('AWS IP ranges grouped by region:\n')
        sort_by_values(data, 'region', 'service', 'ip_prefix')
    elif operation == '2':
        print('AWS IP ranges grouped by service:\n')
        sort_by_values(data, 'service', 'region', 'ip_prefix')
    elif operation == '3':
        print(f'You will see all AWS IP ranges in one specific region.')
        region = choose_value(data, 'region')
        ip_prefix = search_by_value(data, 'region', region)
        print(f'In AWS region {region} there are following IP prefixes:\n{ip_prefix}\n')
    elif operation == '4':
        print(f'You will see all AWS IP ranges of one specific service.')
        service = choose_value(data, 'service')
        ip_prefix = search_by_value(data, 'service', service)
        print(f'In AWS region {service} there are following IP prefixes:\n{ip_prefix}\n')
    elif operation == '5':
        print(f'You will see how many free IP addresses there are in one specific region.')
        region = choose_value(data, 'region')
        regionList = search_by_value(data, 'region', region)
        result = count_ip_addresses(regionList)
        print(f'There are {result} available IP addresses in the region {region}\n')
    elif operation == '6':
        print(f'You will see how many free IP addresses there are in one specific service.')
        service = choose_value(data, 'service')
        used_ip_addresses = search_by_value(data, 'service', service)
        result = count_ip_addresses(used_ip_addresses)
        print(f'There are {result} available IP addresses in the service {service}\n')
    else:
        print('This is not a valid option')
    print('--------')
    print('y - press y if you want to continue\n'
          'any - press any other key to quit the program')
    final_choice = input().lower()
    if final_choice != 'y':
        use_program = False
print("Thank you for using this program!")


