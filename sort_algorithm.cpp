#include <iostream>
#include <omp.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <cmath>
#include <algorithm>


// Parameters
const int SERIAL_THRESHOLD = 30000; // for gem5 100k–300k, we have to use 200000 (1% of N)
const int N = 1000000; // for gem5 to 1M or 2M, we have to use 20000000

// Merge
void merge(std::vector<int>& arr, std::vector<int>& temp, int left, int mid, int right) {
    int i = left;
    int j = mid + 1;
    int k = left; 

    // Merge the two halves into the temp array
    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }

    // Copy remaining elements of left subarray
    while (i <= mid) {
        temp[k++] = arr[i++];
    }

    // Copy remaining elements of right subarray
    while (j <= right) {
        temp[k++] = arr[j++];
    }

    // Copy the merged elements from temp back into arr
    std::copy(temp.begin() + left, temp.begin() + right + 1, arr.begin() + left);
}

void serialMergeSort(std::vector<int>& arr, std::vector<int>& temp, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        serialMergeSort(arr, temp, left, mid);
        serialMergeSort(arr, temp, mid + 1, right);
        merge(arr, temp, left, mid, right);
    }
}

// Parallel Merge Sort
void parallelMergeSort(std::vector<int>& arr, std::vector<int>& temp, int left, int right, int depth, int maxDepth) {
    
    // Switch to serial for small chunks
    if (right - left < SERIAL_THRESHOLD) {
        serialMergeSort(arr, temp, left, right);
        return;
    }

    // Switch to serial if max depth is reached
    if (depth >= maxDepth) {
        serialMergeSort(arr, temp, left, right);
        return;
    }

    int mid = left + (right - left) / 2;

    #pragma omp task shared(arr, temp) firstprivate(left, mid, depth, maxDepth)
    {
        parallelMergeSort(arr, temp, left, mid, depth + 1, maxDepth);
    }

    #pragma omp task shared(arr, temp) firstprivate(mid, right, depth, maxDepth)
    {
        parallelMergeSort(arr, temp, mid + 1, right, depth + 1, maxDepth);
    }

    // Wait for both recursive tasks to complete
    #pragma omp taskwait
    
    merge(arr, temp, left, mid, right);
}

// Main
int main() {
    std::vector<int> arr(N);
    std::vector<int> temp(N);
    
    srand(0); // Fixed seed for consistent results

    for (int i = 0; i < N; i++)
        arr[i] = rand() % 100000;

    std::cout << "Sorting " << N << " elements\n";

    double start = omp_get_wtime();
    int maxDepth; 
    int numThreads;

    #pragma omp parallel
    {
        #pragma omp single
        {
            numThreads = omp_get_num_threads();        
            maxDepth = std::log2(numThreads);
            std::cout << "--- Running with " << omp_get_num_threads() 
                      << " threads (Max Depth: " << maxDepth << ") ---" << std::endl;
            parallelMergeSort(arr, temp, 0, N - 1, 0, maxDepth);
        }
    }

    double end = omp_get_wtime();
    std::cout << "Time: " << end - start << " seconds\n";
	
    /*
    // Validating the result
    for (int i = 0; i < N - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            std::cout << "ERROR: Not sorted at index " << i << '\n';
            return 1;
        }
    }

    std::cout << "Validation PASSED \n";
    */
    
    std::cout << "Simulation Finished \n";
    return 0;
}
