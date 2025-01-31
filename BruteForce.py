import itertools
import time
import hashlib
import random
from multiprocessing import Pool

# Predefined character sets for better efficiency
CHAR_SETS = {
    "digits": "0123456789",
    "lowercase": "abcdefghijklmnopqrstuvwxyz",
    "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "special": "!@#$%^&*()_+-=[]{}|;':\",.<>?/\\",
    "all": ''.join(chr(i) for i in range(32, 127))  # Default: Printable ASCII
}

# Function to dynamically benchmark CPU performance
# This estimates the number of password attempts per second

def benchmark_guesses(chars, length=6, duration=5):
    """
    Estimates the number of guesses per second by hashing random guesses
    for a set duration. The results will help in calculating estimated time.
    """
    start_time = time.time()
    guesses = 0
    while time.time() - start_time < duration:
        _ = hashlib.sha256(''.join(random.choices(chars, k=length)).encode()).hexdigest()
        guesses += 1
    return guesses // duration  # Returns average guesses per second


def format_time(seconds):
    """Formats time into days, hours, minutes, and seconds."""
    days, seconds = divmod(seconds, 86_400)  # 1 day = 86,400 seconds
    hours, seconds = divmod(seconds, 3_600)  # 1 hour = 3,600 seconds
    minutes, seconds = divmod(seconds, 60)   # 1 minute = 60 seconds
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


def calculate_estimated_time(chars, min_length, max_length, guesses_per_second):
    """Calculates the estimated time required to brute-force a password."""
    total_combinations = sum(len(chars) ** length for length in range(min_length, max_length + 1))
    estimated_seconds = total_combinations / guesses_per_second
    return format_time(estimated_seconds), f"{total_combinations:,}", f"{total_combinations:.2e}"


def brute_force_worker(password, guess):
    """Worker function to compare a generated guess against the password."""
    return ''.join(guess) if ''.join(guess) == password else None


def brute_force_attack(password, min_length, max_length, chars):
    """
    Uses multiprocessing to distribute brute-force attack attempts efficiently.
    """
    total_combinations = sum(len(chars) ** length for length in range(min_length, max_length + 1))
    attempts = 0
    start_time = time.time()

    with Pool() as pool:
        for length in range(min_length, max_length + 1):
            guesses = itertools.product(chars, repeat=length)
            for result in pool.imap_unordered(lambda g: brute_force_worker(password, g), guesses, chunksize=10000):
                attempts += 1
                if result:
                    return attempts, result, time.time() - start_time

    return attempts, None, time.time() - start_time


def select_charset():
    """Allows the user to select a character set for better efficiency."""
    print("\nChoose character set:")
    for i, (key, value) in enumerate(CHAR_SETS.items(), 1):
        print(f"{i}. {key} ({len(value)} characters)")
    
    try:
        choice = int(input("Enter choice: ").strip())
        return CHAR_SETS.get(list(CHAR_SETS.keys())[choice - 1], CHAR_SETS["all"])
    except (ValueError, IndexError):
        print("Invalid choice. Using default character set.")
        return CHAR_SETS["all"]


def main():
    """Main menu for the Brute-Force Password Cracker."""
    print("Brute Force Password Cracker (Optimized Version)")
    print("==============================================")

    while True:
        print("\nMenu:")
        print("1. Start Brute Force Attack")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            password = input("Enter the password to attempt cracking: ")
            
            try:
                min_length = int(input("Enter the minimum password length: "))
                max_length = int(input("Enter the maximum password length: "))
                if min_length > max_length:
                    print("Minimum length cannot be greater than maximum length. Try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue

            # Allow user to select character set
            chars = select_charset()

            # Benchmark system performance
            print("\nBenchmarking system performance...")
            cpu_guesses_per_second = benchmark_guesses(chars)
            print(f"Estimated CPU speed: {cpu_guesses_per_second:,} guesses/sec")

            # Calculate estimated cracking time
            estimated_time, total_combinations_formatted, total_combinations_scientific = calculate_estimated_time(
                chars, min_length, max_length, cpu_guesses_per_second
            )

            print(f"\nEstimated cracking time: {estimated_time}")
            print(f"Total possible combinations: {total_combinations_formatted} ({total_combinations_scientific})")

            # Ask for confirmation
            proceed = input("Do you want to proceed? (yes/no): ").strip().lower()
            if proceed == "yes":
                print("\nStarting brute force attack...\n")
                attempts, guess, elapsed_time = brute_force_attack(password, min_length, max_length, chars)
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
