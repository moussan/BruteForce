import itertools
import time
from datetime import timedelta
from multiprocessing import Pool

# Helper function to format time in years, months, days, hours, minutes, and seconds
def format_time(seconds):
    years, seconds = divmod(seconds, 31_536_000)  # 1 year = 31,536,000 seconds
    months, seconds = divmod(seconds, 2_592_000)  # 1 month = 2,592,000 seconds
    days, seconds = divmod(seconds, 86_400)       # 1 day = 86,400 seconds
    hours, seconds = divmod(seconds, 3_600)       # 1 hour = 3,600 seconds
    minutes, seconds = divmod(seconds, 60)        # 1 minute = 60 seconds
    return f"{int(years)}y {int(months)}mo {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

# Function to calculate estimated time
def calculate_estimated_time(chars, min_length, max_length, guesses_per_second):
    total_combinations = sum(len(chars) ** length for length in range(min_length, max_length + 1))
    estimated_seconds = total_combinations / guesses_per_second
    return format_time(estimated_seconds), f"{total_combinations:,}", f"{total_combinations:.2e}"

# Worker function for parallel processing
def worker(args):
    password, chars, length, start_index, end_index = args
    for guess in itertools.product(chars, repeat=length):
        if start_index <= end_index:
            guess_str = ''.join(guess)
            if guess_str == password:
                return guess_str
        start_index += 1
    return None

# Brute force function using CPU with parallel processing
def brute_force_attack(password, min_length, max_length, chars, guesses_per_second):
    total_combinations = sum(len(chars) ** length for length in range(min_length, max_length + 1))
    attempts = 0
    start_time = time.time()

    with Pool() as pool:
        for length in range(min_length, max_length + 1):
            num_workers = pool._processes
            chunk_size = (len(chars) ** length) // num_workers
            worker_args = [
                (password, chars, length, i * chunk_size, (i + 1) * chunk_size)
                for i in range(num_workers)
            ]

            results = pool.map(worker, worker_args)
            for result in results:
                if result:
                    elapsed_time = time.time() - start_time
                    return attempts, result, elapsed_time

            attempts += len(chars) ** length

    elapsed_time = time.time() - start_time
    return attempts, None, elapsed_time

# Main menu
def main():
    print("Brute Force Password Cracker (CPU-Based)")
    print("=========================================")

    while True:
        print("\nMenu:")
        print("1. Start Brute Force Attack")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            # Get password to crack
            password = input("Enter the password to attempt cracking: ")

            # Get search space range
            try:
                min_length = int(input("Enter the minimum password length: "))
                max_length = int(input("Enter the maximum password length: "))
                if min_length > max_length:
                    print("Minimum length cannot be greater than maximum length. Try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue

            # Define character set
            chars = [chr(i) for i in range(32, 127)]  # Printable ASCII characters

            # Get CPU speed (dummy speed, update based on your system's benchmark)
            cpu_guesses_per_second = 100_000  # Replace with your system's benchmark

            # Calculate estimated time
            estimated_time, total_combinations_formatted, total_combinations_scientific = calculate_estimated_time(
                chars, min_length, max_length, cpu_guesses_per_second
            )
            print(f"\nEstimated cracking time: {estimated_time}")
            print(f"Total possible combinations: {total_combinations_formatted} ({total_combinations_scientific})")

            # Ask if the user wants to proceed
            proceed = input("Do you want to proceed? (yes/no): ").strip().lower()
            if proceed == "yes":
                print("\nStarting brute force attack...\n")
                attempts, guess, elapsed_time = brute_force_attack(password, min_length, max_length, chars, cpu_guesses_per_second)
                if guess:
                    print(f"\nPassword cracked in {attempts:,} attempts!")
                    print(f"The password is: {guess}")
                    print(f"Time taken: {format_time(elapsed_time)}")
                else:
                    print("\nFailed to crack the password.")
            else:
                print("\nReturning to the main menu...")
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
