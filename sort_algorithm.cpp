#include <iostream>
#include <omp.h>
#include <vector>
#include <stdlib.h>
#include <time.h>

// Merge Function to combine two sorted halves
void merge(std::vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    // Create temporary arrays
    std::vector<int> L(n1), R(n2);
    // Copy data to temporary arrays L[] and R[]
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    // Merge the temporary arrays back into arr[left..right]
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    // Copy the remaining elements of L[], if any
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    // Copy the remaining elements of R[], if any
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

// Parallel merge sort function
void parallelMergeSort(std::vector<int>& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        // Sort the two halves in parallel
        #pragma omp parallel sections
        {
            #pragma omp section
            {
                parallelMergeSort(arr, left, mid);
            }
            #pragma omp section
            {
                parallelMergeSort(arr, mid + 1, right);
            }
        }
        // Merge the sorted halves
        merge(arr, left, mid, right);
    }
}

// Main Funtion 
int main() {
    // Create a large random vector
    int n = 1000000;
    std::vector<int> arr(n);
    srand(time(NULL)); // Seed the random number generator

    for(int i = 0; i < n; i++) {
        arr[i] = rand() % 10000; // Fill with random numbers
    }

    std::cout << "Starting sort of " << n << " elements" << std::endl;

    // Run the Parallel Sort
    #pragma omp parallel
    {
        #pragma omp master
        {
            std::cout << "--- OpenMP running with " << omp_get_num_threads() << " threads ---" << std::endl;
        }
    }

    // Start the parallel sort
    parallelMergeSort(arr, 0, n - 1);

    std::cout << "Sort finished!" << std::endl;
    
    // std::cout << "First 10 elements: ";
    // for (int i = 0; i < 10; i++) std::cout << arr[i] << " ";
    // std::cout << std::endl;
    return 0;
}
