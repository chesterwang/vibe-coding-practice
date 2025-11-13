from collections import defaultdict
from typing import List, Optional


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def get_arr(self):
        result = []
        cursor = self
        while cursor is not None:
            result.append(cursor.val)
            cursor = cursor.next
        return result
class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head is None:
            return head
        if head.next is None:
            return head
        pre_of_mid = self.find_mid(head)
        head2 = pre_of_mid.next
        pre_of_mid.next = None

        result1 = self.sortList(head)
        result2 = self.sortList(head2)
        result = self.merge_ordered_list(result1, result2)
        return result

    def merge_ordered_list(self, head1, head2):
        if head1 is None:
            return head2
        if head2 is None:
            return head1
        result_head = ListNode(None, None)  # empty head
        result_tail = result_head
        while head1 is not None and head2 is not None:
            if head1.val < head2.val:
                result_tail.next = head1
                head1 = head1.next
                result_tail = result_tail.next
            else:
                result_tail.next = head2
                head2 = head2.next
                result_tail = result_tail.next
        if head1 is None:
            result_tail.next = head2
        if head2 is None:
            result_tail.next = head1
        return result_head.next

    def find_mid(self, head):
        no_value_head = ListNode(val=None, next=head)
        if no_value_head.next is None:
            return head
        i = no_value_head
        j = no_value_head
        while j.next.next is not None and j.next.next.next is not None:
            i = i.next
            j = j.next.next
        return i.next


if __name__ == '__main__':

    sol = Solution()
    a = ListNode(3)
    b = ListNode(1,a)
    c = ListNode(2,b)
    d = ListNode(4,c)
    # 4213
    print(sol.sortList(d).get_arr())

    from collections import deque
    deque

