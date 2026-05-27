#!/usr/bin/env python3
"""
Interactive 9x9 Sudoku Game
Commands: place <row> <col> <num>, erase <row> <col>, hint, solve, new, quit
"""

import random
import copy
import sys
import time


def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True


def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def solve_ordered(board):
    """Solve without randomization (for hint/solution display)."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_ordered(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_puzzle(difficulty="medium"):
    board = [[0] * 9 for _ in range(9)]
    solve(board)
    solution = copy.deepcopy(board)

    cells_to_remove = {"easy": 36, "medium": 46, "hard": 54}
    remove = cells_to_remove.get(difficulty, 46)

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    for r, c in positions[:remove]:
        board[r][c] = 0

    return board, solution


def display_board(board, original, selected=None, errors=None):
    errors = errors or set()

    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    DIM = "\033[2m"
    BG_SEL = "\033[48;5;237m"

    print()
    print(f"  {BOLD}    1   2   3   4   5   6   7   8   9  {RESET}")
    print(f"  {DIM}  +---+---+---+---+---+---+---+---+---+{RESET}")

    for r in range(9):
        row_str = f"  {BOLD}{r+1}{RESET} |"
        for c in range(9):
            val = board[r][c]
            is_selected = selected == (r, c)
            is_original = original[r][c] != 0
            is_error = (r, c) in errors

            prefix = BG_SEL if is_selected else ""
            suffix = RESET if is_selected else ""

            if val == 0:
                cell = f"{prefix} . {suffix}"
            elif is_error:
                cell = f"{prefix}{RED}{BOLD} {val} {RESET}{suffix}"
            elif is_original:
                cell = f"{prefix}{BOLD} {val} {RESET}{suffix}"
            else:
                cell = f"{prefix}{CYAN} {val} {RESET}{suffix}"

            row_str += cell
            if c in (2, 5):
                row_str += f"{BOLD}|{RESET}"
            elif c < 8:
                row_str += "|"

        row_str += "|"
        print(row_str)

        if r in (2, 5):
            print(f"  {DIM}  +===+===+===+===+===+===+===+===+===+{RESET}")
        elif r < 8:
            print(f"  {DIM}  +---+---+---+---+---+---+---+---+---+{RESET}")

    print(f"  {DIM}  +---+---+---+---+---+---+---+---+---+{RESET}")
    print()


def find_errors(board, solution):
    errors = set()
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0 and board[r][c] != solution[r][c]:
                errors.add((r, c))
    return errors


def count_empty(board):
    return sum(1 for r in range(9) for c in range(9) if board[r][c] == 0)


def is_complete(board):
    return all(board[r][c] != 0 for r in range(9) for c in range(9))


def print_help():
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    print(f"""
  {BOLD}Commands:{RESET}
    {CYAN}p <row> <col> <num>{RESET}  Place number (row/col 1-9, num 1-9)
    {CYAN}e <row> <col>{RESET}        Erase a cell
    {CYAN}h{RESET}                    Hint (fills one cell)
    {CYAN}s{RESET}                    Show solution
    {CYAN}c{RESET}                    Check for errors
    {CYAN}n [easy|medium|hard]{RESET} New game
    {CYAN}?{RESET}                    Show this help
    {CYAN}q{RESET}                    Quit
""")


def print_banner():
    BOLD = "\033[1m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    print(f"""
  {BOLD}{YELLOW}╔══════════════════════════════╗
  ║     S U D O K U   9 × 9     ║
  ╚══════════════════════════════╝{RESET}
  Type {BOLD}?{RESET} for help | {BOLD}n{RESET} for new game
""")


def main():
    difficulty = "medium"
    if len(sys.argv) > 1 and sys.argv[1] in ("easy", "medium", "hard"):
        difficulty = sys.argv[1]

    print_banner()
    print(f"  Generating {difficulty} puzzle...")
    board, solution = generate_puzzle(difficulty)
    original = copy.deepcopy(board)
    selected = None
    hints_used = 0
    start_time = time.time()

    display_board(board, original)

    while True:
        empty = count_empty(board)
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        print(f"  Cells left: {empty}  |  Time: {mins:02d}:{secs:02d}  |  Hints: {hints_used}")

        try:
            raw = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0]

        if cmd in ("q", "quit"):
            print("  Goodbye!")
            break

        elif cmd in ("?", "help"):
            print_help()

        elif cmd in ("n", "new"):
            d = parts[1] if len(parts) > 1 else difficulty
            if d not in ("easy", "medium", "hard"):
                print("  Difficulty must be easy, medium, or hard.")
                continue
            difficulty = d
            print(f"\n  Generating {difficulty} puzzle...")
            board, solution = generate_puzzle(difficulty)
            original = copy.deepcopy(board)
            hints_used = 0
            start_time = time.time()
            display_board(board, original)

        elif cmd in ("p", "place"):
            if len(parts) != 4:
                print("  Usage: p <row> <col> <num>")
                continue
            try:
                r, c, num = int(parts[1]) - 1, int(parts[2]) - 1, int(parts[3])
            except ValueError:
                print("  Invalid input. Use numbers only.")
                continue
            if not (0 <= r < 9 and 0 <= c < 9):
                print("  Row and column must be between 1 and 9.")
                continue
            if not (1 <= num <= 9):
                print("  Number must be between 1 and 9.")
                continue
            if original[r][c] != 0:
                print("  Cannot modify a given (original) cell.")
                continue
            board[r][c] = num
            selected = (r, c)
            errors = find_errors(board, solution)
            display_board(board, original, selected, errors)

            if is_complete(board) and not errors:
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                print(f"\033[1m\033[92m  Congratulations! Puzzle solved in {mins:02d}:{secs:02d} with {hints_used} hint(s)!\033[0m\n")
                cont = input("  Play again? (y/n): ").strip().lower()
                if cont == "y":
                    print(f"\n  Generating {difficulty} puzzle...")
                    board, solution = generate_puzzle(difficulty)
                    original = copy.deepcopy(board)
                    hints_used = 0
                    start_time = time.time()
                    selected = None
                    display_board(board, original)
                else:
                    print("  Goodbye!")
                    break

        elif cmd in ("e", "erase"):
            if len(parts) != 3:
                print("  Usage: e <row> <col>")
                continue
            try:
                r, c = int(parts[1]) - 1, int(parts[2]) - 1
            except ValueError:
                print("  Invalid input.")
                continue
            if not (0 <= r < 9 and 0 <= c < 9):
                print("  Row and column must be between 1 and 9.")
                continue
            if original[r][c] != 0:
                print("  Cannot erase an original cell.")
                continue
            board[r][c] = 0
            selected = (r, c)
            display_board(board, original, selected)

        elif cmd in ("h", "hint"):
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if not empties:
                print("  No empty cells left!")
                continue
            r, c = random.choice(empties)
            board[r][c] = solution[r][c]
            hints_used += 1
            selected = (r, c)
            display_board(board, original, selected)
            print(f"  Hint: placed {solution[r][c]} at row {r+1}, col {c+1}")

        elif cmd in ("s", "solve"):
            confirm = input("  Show full solution? This will end the game. (y/n): ").strip().lower()
            if confirm == "y":
                display_board(solution, original)
                print("  Solution shown. Start a new game with 'n'.")

        elif cmd in ("c", "check"):
            errors = find_errors(board, solution)
            if errors:
                display_board(board, original, selected, errors)
                print(f"  Found {len(errors)} error(s) highlighted in red.")
            else:
                print("  No errors found!")

        else:
            print(f"  Unknown command '{cmd}'. Type ? for help.")


if __name__ == "__main__":
    main()
