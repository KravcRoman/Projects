"""Task"""
"""Given an integer x, return true if x is a palindrome, and false otherwise."""
class Solution:
    def isPalindrome(self, x: int) -> bool:
        return False if x < 0 else x == int(str(x)[::-1])