#!/usr/bin/env python3

import curses
import random
import subprocess
from typing import Optional, Tuple


def _parse_git_log_to_ticker(log_output: str) -> Optional[Tuple[str, str]]:
        """Parse raw `git log` output into paired scrolling texts.

        Top line:   commit subject
        Bottom line: "by AUTHOR N days/weeks/years ago"
        """
        lines = [line.strip() for line in log_output.splitlines() if line.strip()]
        if not lines:
                return None

        message_segments = []
        meta_segments = []
        for line in lines:
                parts = line.split("\t", 3)
                if len(parts) != 4:
                        continue
                _commit_hash, author, rel_time, subject = parts
                message = subject
                meta = f"by {author} {rel_time}"
                segment_width = max(len(message), len(meta)) + 4
                message_segments.append(message.ljust(segment_width))
                meta_segments.append(meta.ljust(segment_width))

        if not message_segments:
                return None

        message_text = "".join(message_segments)
        meta_text = "".join(meta_segments)
        return message_text, meta_text


def _build_git_ticker_text(max_commits: int = 20) -> Optional[Tuple[str, str]]:
        """Return paired scrolling texts (message and meta) from recent git commits."""
        try:
                result = subprocess.run(
                        [
                                "git",
                                "log",
                                f"-n{max_commits}",
                                "--pretty=format:%h%x09%an%x09%ar%x09%s",
                        ],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        text=True,
                )
        except (FileNotFoundError, subprocess.CalledProcessError):
                return None

        return _parse_git_log_to_ticker(result.stdout)


def main(screen: "curses._CursesWindow") -> None:
        height, width = screen.getmaxyx()
        size = width * height
        chars = [" ", ".", ":", "^", "*", "x", "s", "S", "#", "$"]
        buffer = [0] * (size + width + 1)

        # Build git ticker text once; if not a git repo or git is missing,
        # this will just be None and the animation behaves as before.
        ticker_pair = _build_git_ticker_text()
        if ticker_pair is not None:
                message_text, meta_text = ticker_pair
        else:
                message_text = meta_text = None
        ticker_offset = 0
        # Use the bottom two lines for the git info when possible.
        ticker_row_message = height - 2 if height >= 2 else None
        ticker_row_meta = height - 1 if height >= 2 else None
        frame = 0

        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, 0, 0)
        curses.init_pair(2, 1, 0)
        curses.init_pair(3, 3, 0)
        curses.init_pair(4, 4, 0)
        # White color pairs for the git ticker text, with a slight
        # gradient achieved via attributes rather than different hues.
        curses.init_pair(5, 7, 0)
        curses.init_pair(6, 7, 0)
        screen.clear()

        while True:
                # Inject heat along the bottom row.
                for _ in range(int(width / 9)):
                        index = int((random.random() * width) + width * (height - 1))
                        buffer[index] = 65

                # Propagate and cool.
                for i in range(size):
                        buffer[i] = int(
                                (buffer[i] + buffer[i + 1] + buffer[i + width] + buffer[i + width + 1]) / 4
                        )
                        value = buffer[i]
                        color = 4 if value > 15 else 3 if value > 9 else 2 if value > 4 else 1
                        if i < size - 1:
                                row = int(i / width)
                                col = i % width
                                # Reserve the bottom two lines for the git info, if available.
                                if message_text and meta_text and ticker_row_message is not None and ticker_row_meta is not None:
                                        if row == ticker_row_message or row == ticker_row_meta:
                                                continue
                                char_index = 9 if value > 9 else value
                                ch = chars[char_index]
                                try:
                                        screen.addstr(row, col, ch, curses.color_pair(color) | curses.A_BOLD)
                                except curses.error:
                                        # Ignore drawing errors that can happen on resize.
                                        pass

                # Draw the git info as two lines at the bottom, scrolling right-to-left.
                if message_text and meta_text and ticker_row_message is not None and ticker_row_meta is not None:
                        length = len(message_text)
                        if length <= width:
                                visible_message = message_text.ljust(width)
                                visible_meta = meta_text.ljust(width)
                        else:
                                msg_slice = [
                                        message_text[(ticker_offset + j) % length] for j in range(width)
                                ]
                                meta_slice = [
                                        meta_text[(ticker_offset + j) % length] for j in range(width)
                                ]
                                visible_message = "".join(msg_slice)
                                visible_meta = "".join(meta_slice)
                        # Draw both lines left-aligned, with first characters vertically aligned.
                        for col, ch in enumerate(visible_message[:width]):
                                if ch == "\n":
                                        continue
                                try:
                                        screen.addstr(ticker_row_message, col, ch, curses.color_pair(5))
                                except curses.error:
                                        pass
                        for col, ch in enumerate(visible_meta[:width]):
                                if ch == "\n":
                                        continue
                                try:
                                        screen.addstr(ticker_row_meta, col, ch, curses.color_pair(5))
                                except curses.error:
                                        pass
                        # Advance the scroll position so text moves right-to-left.
                        # Only update every 4 frames to move at quarter speed.
                        if length > 0 and frame % 4 == 0:
                                ticker_offset = (ticker_offset + 1) % length

                screen.refresh()
                screen.timeout(30)
                frame += 1
                if screen.getch() != -1:
                        break


if __name__ == "__main__":
        curses.wrapper(main)