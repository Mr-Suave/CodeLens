function merge(arr, begin, mid, end) {
    let sub1 = arr.slice(begin, mid + 1);
    let sub2 = arr.slice(mid + 1, end + 1);

    let j = 0, k = 0, main = begin;

    while (j < sub1.length && k < sub2.length) {
        if (sub1[j] < sub2[k]) {
            arr[main] = sub1[j++];
        } else {
            arr[main] = sub2[k++];
        }
        main++;
    }

    while (j < sub1.length) arr[main++] = sub1[j++];
    while (k < sub2.length) arr[main++] = sub2[k++];
}

function mergeSort(arr, begin, end) {
    if (begin >= end) return;
    let mid = begin + Math.floor((end - begin) / 2);
    mergeSort(arr, begin, mid);
    mergeSort(arr, mid + 1, end);
    merge(arr, begin, mid, end);
}

function binarySearch(arr, x) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        let middle = left + Math.floor((right - left) / 2);
        if (arr[middle] === x) return middle;
        else if (arr[middle] < x) left = middle + 1;
        else right = middle - 1;
    }
    return -1;
}

let arr = [54, 26, 93, 17, 77, 31, 44, 55, 20, 85];
mergeSort(arr, 0, arr.length - 1);
console.log("Sorted array:", arr);

const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
});

readline.question("Enter the element to search: ", (x) => {
    let index = binarySearch(arr, parseInt(x));
    if (index !== -1) {
        console.log(`Element is present at index ${index}`);
    } else {
        console.log("-1");
    }
    readline.close();
});