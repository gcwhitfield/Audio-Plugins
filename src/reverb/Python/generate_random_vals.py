import random

def main():
    max_num = 7000
    min_num = 5000
    num_nums = 10
    for i in range(num_nums):
        print(random.randint(min_num, max_num))

if __name__ == "__main__":
    main()