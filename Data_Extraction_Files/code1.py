def merge(arr, begin, mid, end):
    sub1 = arr[begin:mid + 1]
    sub2 = arr[mid + 1:end + 1]
    
    j = k = 0
    main = begin

    while j < len(sub1) and k < len(sub2):
        if sub1[j] < sub2[k]:
            arr[main] = sub1[j]
            j += 1
        else:
            arr[main] = sub2[k]
            k += 1
        main += 1

    while j < len(sub1):
        arr[main] = sub1[j]
        j += 1
        main += 1

    while k < len(sub2):
        arr[main] = sub2[k]
        k += 1
        main += 1

def merge_sort(arr, begin, end):
    if begin >= end:
        return
    mid = begin + (end - begin) // 2
    merge_sort(arr, begin, mid)
    merge_sort(arr, mid + 1, end)
    merge(arr, begin, mid, end)

def binary_search(arr, x):
    left, right = 0, len(arr) - 1
    while left <= right:
        middle = left + (right - left) // 2
        if arr[middle] == x:
            return middle
        elif arr[middle] < x:
            left = middle + 1
        else:
            right = middle - 1
    return -1

arr = [54, 26, 93, 17, 77, 31, 44, 55, 20, 85]
merge_sort(arr, 0, len(arr) - 1)
print("Sorted array:", arr)

x = int(input("Enter the element to search: "))
index = binary_search(arr, x)

if index != -1:
    print(f"Element is present at index {index}")
else:
    print("-1")